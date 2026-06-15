"""主编排工作流状态定义"""
from typing import Annotated, Any, Optional
from typing_extensions import TypedDict
import operator


class AgentOrchestrationState(TypedDict):
    """主编排工作流状态"""
    session_id: str
    user_id: int
    messages: Annotated[list, operator.add]

    # 各阶段数据
    user_input: str
    intent_analysis: dict
    task_plan: dict
    subtask_results: dict          # {subtask_id: result}
    final_response: str

    # 控制流
    current_phase: str             # "intent" / "planning" / "execution" / "review" / "done"
    needs_clarification: bool
    clarification_question: str
