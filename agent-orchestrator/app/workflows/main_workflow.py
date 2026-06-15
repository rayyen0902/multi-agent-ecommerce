"""主编排工作流 - Front-desk -> PMO -> 执行 Agents"""
import logging
import uuid
from datetime import datetime

from langgraph.graph import END, StateGraph

from app.agents.front_desk import FrontDeskAgent
from app.agents.pmo import PMOAgent
from app.blackboard.models import BlackboardEntry, BlackboardSession, EntryType
from app.blackboard.service import BlackboardService
from app.workflows.state import AgentOrchestrationState

logger = logging.getLogger(__name__)


class MainWorkflow:
    """主编排工作流：用户输入 -> 意图识别 -> PMO编排 -> 最终响应"""

    def __init__(
        self,
        front_desk: FrontDeskAgent,
        pmo: PMOAgent,
        blackboard: BlackboardService,
    ):
        self.front_desk = front_desk
        self.pmo = pmo
        self.blackboard = blackboard
        self._graph = self._build_graph()

    def _build_graph(self):
        graph = StateGraph(AgentOrchestrationState)

        graph.add_node("front_desk", self._front_desk_node)
        graph.add_node("clarify", self._clarify_node)
        graph.add_node("pmo_orchestrate", self._pmo_node)
        graph.add_node("format_response", self._format_response_node)

        graph.set_entry_point("front_desk")

        graph.add_conditional_edges(
            "front_desk",
            self._should_clarify,
            {"clarify": "clarify", "proceed": "pmo_orchestrate"},
        )
        graph.add_edge("clarify", END)
        graph.add_edge("pmo_orchestrate", "format_response")
        graph.add_edge("format_response", END)

        return graph.compile()

    async def run(
        self,
        session_id: str,
        user_id: int,
        user_input: str,
    ) -> dict:
        """执行完整编排流程

        Returns:
            {
                "session_id": str,
                "phase": str,
                "final_response": str,
                "needs_clarification": bool,
                "clarification_question": str,
                "intent_analysis": dict,
            }
        """
        # 创建会话记录
        session = BlackboardSession(
            session_id=session_id,
            user_id=user_id,
        )
        await self.blackboard.create_session(session)

        # 执行工作流
        result = await self._graph.ainvoke({
            "session_id": session_id,
            "user_id": user_id,
            "messages": [],
            "user_input": user_input,
            "intent_analysis": {},
            "task_plan": {},
            "subtask_results": {},
            "final_response": "",
            "current_phase": "intent",
            "needs_clarification": False,
            "clarification_question": "",
        })

        return {
            "session_id": session_id,
            "phase": result.get("current_phase", "done"),
            "final_response": result.get("final_response", ""),
            "needs_clarification": result.get("needs_clarification", False),
            "clarification_question": result.get("clarification_question", ""),
            "intent_analysis": result.get("intent_analysis", {}),
        }

    # ---------- 节点实现 ----------

    async def _front_desk_node(
        self, state: AgentOrchestrationState
    ) -> dict:
        """前台 Agent 节点：意图识别"""
        logger.info(f"[{state['session_id']}] Front-desk: 分析意图")

        intent = await self.front_desk.analyze_intent(state["user_input"])

        # 写入黑板
        await self.blackboard.write(BlackboardEntry(
            session_id=state["session_id"],
            entry_type=EntryType.USER_INTENT,
            key="latest",
            value=intent,
            author_agent="front_desk",
        ))

        return {
            "intent_analysis": intent,
            "needs_clarification": intent.get("needs_clarification", False),
            "clarification_question": intent.get("clarification_question", ""),
            "current_phase": "intent",
        }

    async def _clarify_node(
        self, state: AgentOrchestrationState
    ) -> dict:
        """澄清节点：需要用户补充信息"""
        logger.info(f"[{state['session_id']}] 需要澄清")

        question = state.get("clarification_question") or \
            "抱歉，我没能完全理解您的需求。能否请您更具体地描述一下？"

        await self.blackboard.write(BlackboardEntry(
            session_id=state["session_id"],
            entry_type=EntryType.FINAL_RESPONSE,
            key="clarification",
            value=question,
            author_agent="front_desk",
        ))

        return {
            "final_response": question,
            "current_phase": "clarify",
        }

    async def _pmo_node(
        self, state: AgentOrchestrationState
    ) -> dict:
        """PMO 编排节点：分解任务、执行、验收"""
        logger.info(f"[{state['session_id']}] PMO: 开始编排")

        final_response = await self.pmo.orchestrate(
            session_id=state["session_id"],
            intent=state["intent_analysis"],
        )

        return {
            "final_response": final_response,
            "current_phase": "execution",
        }

    async def _format_response_node(
        self, state: AgentOrchestrationState
    ) -> dict:
        """格式化最终响应"""
        return {"current_phase": "done"}

    # ---------- 条件判断 ----------

    @staticmethod
    def _should_clarify(state: AgentOrchestrationState) -> str:
        if state.get("needs_clarification"):
            return "clarify"
        return "proceed"
