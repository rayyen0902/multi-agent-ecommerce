"""黑板服务统一接口 - Redis 即时写入 + PostgreSQL 异步持久化"""
import asyncio
import logging
from typing import Any, Optional

from app.blackboard.models import (
    AgentExecutionLog,
    BlackboardEntry,
    BlackboardSession,
    EntryType,
    TaskPlan,
)
from app.blackboard.redis_store import RedisBlackboardStore
from app.blackboard.pg_store import PgBlackboardStore

logger = logging.getLogger(__name__)


class BlackboardService:
    """黑板服务：双写 Redis + PostgreSQL，读取优先 Redis"""

    def __init__(
        self,
        redis_store: RedisBlackboardStore,
        pg_store: PgBlackboardStore,
    ):
        self.redis = redis_store
        self.pg = pg_store

    async def initialize(self) -> None:
        await self.redis.connect()

    async def shutdown(self) -> None:
        await self.redis.disconnect()

    # ---------- 写入 ----------

    async def write(self, entry: BlackboardEntry) -> None:
        """写入黑板条目：Redis 即时 + PG 后台持久化"""
        await self.redis.write_entry(entry)
        # PG 持久化不阻塞主流程
        asyncio.create_task(self._persist_entry(entry))

    async def _persist_entry(self, entry: BlackboardEntry) -> None:
        try:
            await self.pg.persist_entry(entry)
        except Exception as e:
            logger.warning(f"PG 持久化黑板条目失败: {e}")

    # ---------- 读取 ----------

    async def read_context(self, session_id: str) -> dict:
        """读取当前会话的完整上下文（供 Agent 参考）"""
        entries = await self.redis.read_all(session_id)
        context: dict[str, Any] = {}
        for entry in entries:
            context_key = f"{entry.entry_type.value}:{entry.key}"
            context[context_key] = entry.value
        return context

    async def read_latest_by_type(
        self, session_id: str, entry_type: EntryType, limit: int = 10
    ) -> list[BlackboardEntry]:
        return await self.redis.read_latest_by_type(session_id, entry_type, limit)

    async def read_latest_result(
        self, session_id: str, agent_name: str
    ) -> Optional[BlackboardEntry]:
        return await self.redis.read_latest_result(session_id, agent_name)

    async def read_entry(
        self, session_id: str, entry_id: str
    ) -> Optional[BlackboardEntry]:
        return await self.redis.read_entry(session_id, entry_id)

    # ---------- 会话管理 ----------

    async def create_session(self, session: BlackboardSession) -> None:
        await self.pg.create_session(session)

    async def update_session_status(
        self, session_id: str, status: str
    ) -> None:
        await self.pg.update_session_status(session_id, status)

    # ---------- 任务计划 ----------

    async def save_task_plan(self, plan: TaskPlan) -> None:
        await self.pg.save_task_plan(plan)

    # ---------- 执行日志 ----------

    async def save_execution_log(self, log: AgentExecutionLog) -> None:
        asyncio.create_task(self._persist_log(log))

    async def _persist_log(self, log: AgentExecutionLog) -> None:
        try:
            await self.pg.save_execution_log(log)
        except Exception as e:
            logger.warning(f"PG 持久化执行日志失败: {e}")

    # ---------- 历史记录 ----------

    async def get_session_history(
        self, user_id: int, limit: int = 20, offset: int = 0
    ) -> list[dict]:
        return await self.pg.get_session_history(user_id, limit, offset)

    async def get_session_entries(self, session_id: str) -> list[dict]:
        return await self.pg.get_session_entries(session_id)

    # ---------- 订阅 ----------

    async def subscribe(self, session_id: str):
        return await self.redis.subscribe(session_id)

    # ---------- 清理 ----------

    async def clear_session(self, session_id: str) -> None:
        await self.redis.clear_session(session_id)
