"""测试 BlackboardService 后台任务管理"""
import asyncio
import pytest


@pytest.mark.asyncio
async def test_write_creates_background_task():
    """write() 应创建后台任务并注册到 _background_tasks 集合"""
    from unittest.mock import AsyncMock, MagicMock

    from app.blackboard.models import BlackboardEntry, EntryType
    from app.blackboard.redis_store import RedisBlackboardStore
    from app.blackboard.pg_store import PgBlackboardStore
    from app.blackboard.service import BlackboardService

    redis_store = MagicMock(spec=RedisBlackboardStore)
    redis_store.write_entry = AsyncMock()

    pg_store = MagicMock(spec=PgBlackboardStore)
    pg_store.persist_entry = AsyncMock()

    service = BlackboardService(redis_store, pg_store)

    entry = BlackboardEntry(
        session_id="test-session",
        entry_type=EntryType.USER_INTENT,
        key="latest",
        value={"intent": "test"},
        author_agent="front_desk",
    )

    await service.write(entry)

    # 验证 Redis 写入被调用
    redis_store.write_entry.assert_called_once_with(entry)

    # 验证后台任务已创建
    assert len(service._background_tasks) == 1


@pytest.mark.asyncio
async def test_shutdown_waits_for_tasks():
    """shutdown() 应等待所有后台任务完成"""
    from unittest.mock import AsyncMock, MagicMock

    from app.blackboard.models import BlackboardEntry, EntryType
    from app.blackboard.redis_store import RedisBlackboardStore
    from app.blackboard.pg_store import PgBlackboardStore
    from app.blackboard.service import BlackboardService

    redis_store = MagicMock(spec=RedisBlackboardStore)
    redis_store.write_entry = AsyncMock()
    redis_store.disconnect = AsyncMock()

    pg_store = MagicMock(spec=PgBlackboardStore)
    pg_store.persist_entry = AsyncMock()

    service = BlackboardService(redis_store, pg_store)

    entry = BlackboardEntry(
        session_id="test-session",
        entry_type=EntryType.USER_INTENT,
        key="latest",
        value={"intent": "test"},
        author_agent="front_desk",
    )

    await service.write(entry)
    await service.shutdown()

    # 验证 PG 持久化被调用
    pg_store.persist_entry.assert_called_once_with(entry)
    # 验证 Redis 断开被调用
    redis_store.disconnect.assert_called_once()
