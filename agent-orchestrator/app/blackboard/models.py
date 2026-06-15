"""黑板系统数据模型"""
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class EntryType(str, Enum):
    """黑板条目类型"""
    USER_INTENT = "user_intent"
    TASK_PLAN = "task_plan"
    TASK_ASSIGNMENT = "task_assignment"
    TASK_RESULT = "task_result"
    REVIEW_RESULT = "review_result"
    REVISION_GUIDANCE = "revision_guidance"
    FINAL_RESPONSE = "final_response"
    AGENT_LOG = "agent_log"
    CONTEXT = "context"


class BlackboardEntry(BaseModel):
    """黑板条目"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    entry_type: EntryType
    key: str
    value: Any
    author_agent: str
    version: int = 1
    parent_version: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None


class BlackboardSession(BaseModel):
    """黑板会话"""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: int
    title: Optional[str] = None
    status: str = "active"  # active / completed / failed
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    message_count: int = 0


class SubTaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    REVISION = "revision"


class SubTask(BaseModel):
    """PMO 分解的子任务"""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str
    description: str
    dependencies: list[str] = Field(default_factory=list)
    status: SubTaskStatus = SubTaskStatus.PENDING
    result: Optional[Any] = None
    revision_count: int = 0
    max_revisions: int = 3
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class TaskPlan(BaseModel):
    """PMO Agent 生成的任务计划"""
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    original_intent: str
    subtasks: list[SubTask] = Field(default_factory=list)
    status: str = "created"  # created / executing / completed / failed
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class ReviewResult(BaseModel):
    """PMO 验收结果"""
    approved: bool
    score: float = 0.0  # 0-10
    issues: list[str] = Field(default_factory=list)
    revision_guidance: str = ""


class AgentExecutionLog(BaseModel):
    """Agent 执行日志"""
    id: Optional[int] = None
    session_id: str
    agent_name: str
    action: str
    input_data: Optional[Any] = None
    output_data: Optional[Any] = None
    model_used: Optional[str] = None
    tokens_input: int = 0
    tokens_output: int = 0
    cost_usd: float = 0.0
    duration_ms: int = 0
    status: str = "success"
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
