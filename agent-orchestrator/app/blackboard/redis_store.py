"""Redis 黑板存储 - 热数据高频读写"""
import json
from typing import Optional

import redis.asyncio as aioredis

from app.blackboard.models import BlackboardEntry, EntryType


class RedisBlackboardStore:
    """Redis 黑板存储，支持 Pub/Sub 通知"""

    PREFIX = "blackboard"
    TTL_SECONDS = 86400  # 24 小时

    def __init__(self, redis_url: str):
        self._redis: Optional[aioredis.Redis] = None
        self._redis_url = redis_url

    async def connect(self) -> None:
        self._redis = aioredis.from_url(self._redis_url, decode_responses=True)

    async def disconnect(self) -> None:
        if self._redis:
            await self._redis.close()

    @property
    def redis(self) -> aioredis.Redis:
        if not self._redis:
            raise RuntimeError("Redis 未连接，请先调用 connect()")
        return self._redis

    # ---------- Key 构造 ----------

    def _entry_key(self, session_id: str, entry_id: str) -> str:
        return f"{self.PREFIX}:entry:{session_id}:{entry_id}"

    def _entries_zset_key(self, session_id: str) -> str:
        return f"{self.PREFIX}:entries:{session_id}"

    def _type_set_key(self, session_id: str, entry_type: str) -> str:
        return f"{self.PREFIX}:type:{session_id}:{entry_type}"

    def _channel(self, session_id: str) -> str:
        return f"{self.PREFIX}:notify:{session_id}"

    # ---------- 写入 ----------

    async def write_entry(self, entry: BlackboardEntry) -> None:
        """写入黑板条目，并发布通知"""
        entry_key = self._entry_key(entry.session_id, entry.id)
        entry_json = entry.model_dump_json()

        # 条目数据，TTL 24h
        await self.redis.setex(entry_key, self.TTL_SECONDS, entry_json)

        # 加入有序集合（按创建时间排序）
        await self.redis.zadd(
            self._entries_zset_key(entry.session_id),
            {entry.id: entry.created_at.timestamp()},
        )

        # 按类型索引
        await self.redis.sadd(
            self._type_set_key(entry.session_id, entry.entry_type.value),
            entry.id,
        )

        # 发布通知
        await self.redis.publish(
            self._channel(entry.session_id),
            json.dumps(
                {
                    "event": "entry_written",
                    "entry_id": entry.id,
                    "entry_type": entry.entry_type.value,
                    "author": entry.author_agent,
                    "key": entry.key,
                },
                ensure_ascii=False,
            ),
        )

    # ---------- 读取 ----------

    async def read_entry(
        self, session_id: str, entry_id: str
    ) -> Optional[BlackboardEntry]:
        """读取指定条目"""
        data = await self.redis.get(self._entry_key(session_id, entry_id))
        return BlackboardEntry.model_validate_json(data) if data else None

    async def read_latest_by_type(
        self, session_id: str, entry_type: EntryType, limit: int = 10
    ) -> list[BlackboardEntry]:
        """读取某类型的最新条目"""
        entry_ids = await self.redis.smembers(
            self._type_set_key(session_id, entry_type.value)
        )
        entries: list[BlackboardEntry] = []
        for eid in entry_ids:
            entry = await self.read_entry(session_id, eid)
            if entry:
                entries.append(entry)
        entries.sort(key=lambda e: e.created_at, reverse=True)
        return entries[:limit]

    async def read_all(self, session_id: str) -> list[BlackboardEntry]:
        """读取会话所有条目（按时间升序）"""
        entry_ids = await self.redis.zrange(
            self._entries_zset_key(session_id), 0, -1
        )
        entries: list[BlackboardEntry] = []
        for eid in entry_ids:
            entry = await self.read_entry(session_id, eid)
            if entry:
                entries.append(entry)
        return entries

    async def read_latest_result(
        self, session_id: str, agent_name: str
    ) -> Optional[BlackboardEntry]:
        """读取指定 Agent 的最新 task_result"""
        entries = await self.read_latest_by_type(
            session_id, EntryType.TASK_RESULT, limit=50
        )
        for e in entries:
            if e.author_agent == agent_name:
                return e
        return None

    # ---------- 订阅 ----------

    async def subscribe(self, session_id: str):
        """订阅黑板变更通知，返回 pubsub 对象"""
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(self._channel(session_id))
        return pubsub

    # ---------- 清理 ----------

    async def clear_session(self, session_id: str) -> None:
        """清理会话的所有黑板数据"""
        entries = await self.read_all(session_id)
        keys_to_delete = [
            self._entry_key(session_id, e.id) for e in entries
        ]
        keys_to_delete.append(self._entries_zset_key(session_id))

        # 删除类型集合
        for entry_type in EntryType:
            keys_to_delete.append(
                self._type_set_key(session_id, entry_type.value)
            )

        if keys_to_delete:
            await self.redis.delete(*keys_to_delete)
