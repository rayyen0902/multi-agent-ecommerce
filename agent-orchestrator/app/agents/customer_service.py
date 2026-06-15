"""客服对话 Agent"""
import logging

from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent

from app.llm.router import ModelRouter
from app.prompts.customer_service import CUSTOMER_SERVICE_SYSTEM_PROMPT
from app.tools import ToolRegistry

logger = logging.getLogger(__name__)


def create_customer_service_agent(
    model_router: ModelRouter,
    tool_registry: ToolRegistry,
):
    """创建客服对话 Agent（生成客服回复建议）"""
    model = model_router.get_model("customer_service")
    tools = tool_registry.get_tools_for_agent("customer_service")

    agent = create_react_agent(
        model=model,
        tools=tools,
        prompt=SystemMessage(content=CUSTOMER_SERVICE_SYSTEM_PROMPT),
    )

    logger.info(
        f"Customer Service Agent 已创建，工具数: {len(tools)}"
    )
    return agent
