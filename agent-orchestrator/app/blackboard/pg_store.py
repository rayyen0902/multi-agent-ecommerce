"""PostgreSQL 黑板持久化存储 - 审计与回放"""
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.blackboard.models import (
    AgentExecutionLog,
    BlackboardEntry,
    BlackboardSession,
    TaskPlan,
    SubTask,
)


class PgBlackboardStore:
    """PostgreSQL 持久化存储，用于审计和回放"""

    def __init__(self, session_factory):
        """session_factory: 返回 AsyncSession 的可调用对象"""
        self._session_factory = session_factory

    # ---------- 会话 ----------

    async def create_session(self, session: BlackboardSession) -> None:
        async with self._session_factory() as db:
            await db.execute(
                text("""
                    INSERT INTO agent_sessions (session_id, user_id, title, status, metadata, created_at, updated_at)
                    VALUES (:session_id, :user_id, :title, :status, :metadata, :created_at, :updated_at)
                    ON CONFLICT (session_id) DO NOTHING
                """),
                {
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "title": session.title,
                    "status": session.status,
                    "metadata": "{}",
                    "created_at": session.created_at,
                    "updated_at": session.updated_at,
                },
            )
            await db.commit()

    async def update_session_status(
        self, session_id: str, status: str
    ) -> None:
        async with self._session_factory() as db:
            await db.execute(
                text("""
                    UPDATE agent_sessions
                    SET status = :status, updated_at = NOW()
                    WHERE session_id = :session_id
                """),
                {"session_id": session_id, "status": status},
            )
            await db.commit()

    # ---------- 黑板条目 ----------

    async def persist_entry(self, entry: BlackboardEntry) -> None:
        async with self._session_factory() as db:
            await db.execute(
                text("""
                    INSERT INTO blackboard_entries
                        (id, session_id, entry_type, key, value, author_agent,
                         version, parent_version, metadata, created_at, expires_at)
                    VALUES
                        (:id, :session_id, :entry_type, :key, :value::jsonb, :author_agent,
                         :version, :parent_version, :metadata::jsonb, :created_at, :expires_at)
                    ON CONFLICT (id) DO NOTHING
                """),
                {
                    "id": entry.id,
                    "session_id": entry.session_id,
                    "entry_type": entry.entry_type.value,
                    "key": entry.key,
                    "value": entry.model_dump_json(include={"value"}).split('"value": ')[-1].rstrip("}"),
                    "author_agent": entry.author_agent,
                    "version": entry.version,
                    "parent_version": entry.parent_version,
                    "metadata": "{}",
                    "created_at": entry.created_at,
                    "expires_at": entry.expires_at,
                },
            )
            await db.commit()

    # ---------- 执行日志 ----------

    async def save_execution_log(self, log: AgentExecutionLog) -> None:
        async with self._session_factory() as db:
            await db.execute(
                text("""
                    INSERT INTO agent_execution_logs
                        (session_id, agent_name, action, input_data, output_data,
                         model_used, tokens_input, tokens_output, cost_usd,
                         duration_ms, status, error_message, created_at)
                    VALUES
                        (:session_id, :agent_name, :action, :input_data::jsonb, :output_data::jsonb,
                         :model_used, :tokens_input, :tokens_output, :cost_usd,
                         :duration_ms, :status, :error_message, :created_at)
                """),
                {
                    "session_id": log.session_id,
                    "agent_name": log.agent_name,
                    "action": log.action,
                    "input_data": "{}",
                    "output_data": "{}",
                    "model_used": log.model_used,
                    "tokens_input": log.tokens_input,
                    "tokens_output": log.tokens_output,
                    "cost_usd": log.cost_usd,
                    "duration_ms": log.duration_ms,
                    "status": log.status,
                    "error_message": log.error_message,
                    "created_at": log.created_at,
                },
            )
            await db.commit()

    # ---------- 任务计划 ----------

    async def save_task_plan(self, plan: TaskPlan) -> None:
        async with self._session_factory() as db:
            await db.execute(
                text("""
                    INSERT INTO agent_task_plans
                        (plan_id, session_id, original_intent, plan_data, status, created_at)
                    VALUES
                        (:plan_id, :session_id, :original_intent, :plan_data::jsonb, :status, :created_at)
                    ON CONFLICT (plan_id) DO UPDATE SET status = EXCLUDED.status
                """),
                {
                    "plan_id": plan.plan_id,
                    "session_id": plan.session_id,
                    "original_intent": plan.original_intent,
                    "plan_data": plan.model_dump_json(),
                    "status": plan.status,
                    "created_at": plan.created_at,
                },
            )
            # 保存子任务
            for subtask in plan.subtasks:
                await db.execute(
                    text("""
                        INSERT INTO agent_subtasks
                            (task_id, plan_id, agent_name, description, dependencies,
                             status, revision_count, max_revisions, created_at)
                        VALUES
                            (:task_id, :plan_id, :agent_name, :description, :dependencies::jsonb,
                             :status, :revision_count, :max_revisions, :created_at)
                        ON CONFLICT (task_id) DO UPDATE SET
                            status = EXCLUDED.status,
                            revision_count = EXCLUDED.revision_count
                    """),
                    {
                        "task_id": subtask.task_id,
                        "plan_id": plan.plan_id,
                        "agent_name": subtask.agent_name,
                        "description": subtask.description,
                        "dependencies": "[]",
                        "status": subtask.status.value if hasattr(subtask.status, "value") else subtask.status,
                        "revision_count": subtask.revision_count,
                        "max_revisions": subtask.max_revisions,
                        "created_at": subtask.created_at,
                    },
                )
            await db.commit()

    # ---------- 查询 ----------

    async def get_session_history(
        self, user_id: int, limit: int = 20, offset: int = 0
    ) -> list[dict]:
        async with self._session_factory() as db:
            result = await db.execute(
                text("""
                    SELECT session_id, title, status, created_at, updated_at, message_count
                    FROM agent_sessions
                    WHERE user_id = :user_id
                    ORDER BY updated_at DESC
                    LIMIT :limit OFFSET :offset
                """),
                {"user_id": user_id, "limit": limit, "offset": offset},
            )
            rows = result.fetchall()
            return [
                {
                    "session_id": r[0],
                    "title": r[1],
                    "status": r[2],
                    "created_at": str(r[3]),
                    "updated_at": str(r[4]),
                    "message_count": r[5],
                }
                for r in rows
            ]

    async def get_session_entries(
        self, session_id: str
    ) -> list[dict]:
        async with self._session_factory() as db:
            result = await db.execute(
                text("""
                    SELECT id, entry_type, key, value, author_agent, version, created_at
                    FROM blackboard_entries
                    WHERE session_id = :session_id
                    ORDER BY created_at ASC
                """),
                {"session_id": session_id},
            )
            rows = result.fetchall()
            return [
                {
                    "id": r[0],
                    "entry_type": r[1],
                    "key": r[2],
                    "value": r[3],
                    "author_agent": r[4],
                    "version": r[5],
                    "created_at": str(r[6]),
                }
                for r in rows
            ]
