"""PMO 验收循环工作流（独立模块，可被 PMO Agent 调用）"""
import logging
from typing import Annotated, Any
from typing_extensions import TypedDict
import operator

from langgraph.graph import END, StateGraph

from app.blackboard.models import ReviewResult, SubTask, SubTaskStatus

logger = logging.getLogger(__name__)

MAX_REVISIONS = 3
REVIEW_PASS_SCORE = 7.0


class PMOReviewState(TypedDict):
    """PMO 验收循环状态"""
    session_id: str
    subtask: dict
    result_text: str
    intent_summary: str
    review_result: dict
    revision_count: int
    final_result: str
    messages: Annotated[list, operator.add]


def build_pmo_review_graph(review_fn, execute_fn, revise_fn):
    """构建 PMO 验收循环工作流图

    Args:
        review_fn: 验收评估函数
        execute_fn: 任务执行函数
        revise_fn: 修改建议生成函数
    """
    graph = StateGraph(PMOReviewState)

    graph.add_node("review", review_fn)
    graph.add_node("execute", execute_fn)
    graph.add_node("revise", revise_fn)
    graph.add_node("accept", _accept_node)
    graph.add_node("fail", _fail_node)

    graph.set_entry_point("review")

    graph.add_conditional_edges(
        "review",
        _review_decision,
        {"accept": "accept", "revise": "revise", "fail": "fail"},
    )
    graph.add_edge("revise", "execute")
    graph.add_edge("execute", "review")
    graph.add_edge("accept", END)
    graph.add_edge("fail", END)

    return graph.compile()


def _review_decision(state: PMOReviewState) -> str:
    """决定是接受、重试还是放弃"""
    review = state.get("review_result", {})
    approved = review.get("approved", False)
    score = review.get("score", 0)
    revision_count = state.get("revision_count", 0)

    if approved or score >= REVIEW_PASS_SCORE:
        return "accept"
    elif revision_count < MAX_REVISIONS:
        return "revise"
    else:
        return "fail"


async def _accept_node(state: PMOReviewState) -> dict:
    return {"final_result": state["result_text"]}


async def _fail_node(state: PMOReviewState) -> dict:
    review = state.get("review_result", {})
    issues = review.get("issues", [])
    return {
        "final_result": (
            f"[任务未达标] {state['subtask'].get('description', '')}\n"
            f"问题: {'; '.join(issues)}\n"
            f"结果: {state['result_text']}"
        ),
    }
