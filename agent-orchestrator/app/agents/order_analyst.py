"""订单分析 Agent"""
import logging

from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent

from app.llm.router import ModelRouter
from app.prompts.order_analyst import ORDER_ANALYST_SYSTEM_PROMPT
from app.tools import ToolRegistry

logger = logging.getLogger(__name__)


def create_order_analyst_agent(
    model_router: ModelRouter,
    tool_registry: ToolRegistry,
):
    """创建订单分析 Agent（ReAct 模式，带工具调用）"""
    model = model_router.get_model("order_analyst")
    tools = tool_registry.get_tools_for_agent("order_analyst")

    agent = create_react_agent(
        model=model,
        tools=tools,
        prompt=SystemMessage(content=ORDER_ANALYST_SYSTEM_PROMPT),
    )

    logger.info(
        f"Order Analyst Agent 已创建，工具数: {len(tools)}"
    )
    return agent
