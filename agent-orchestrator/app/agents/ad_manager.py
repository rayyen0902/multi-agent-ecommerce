"""自动化投流 Agent"""
import logging

from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent

from app.llm.router import ModelRouter
from app.prompts.ad_manager import AD_MANAGER_SYSTEM_PROMPT
from app.tools import ToolRegistry

logger = logging.getLogger(__name__)


def create_ad_manager_agent(
    model_router: ModelRouter,
    tool_registry: ToolRegistry,
):
    """创建自动化投流 Agent（广告投放管理）"""
    model = model_router.get_model("ad_manager")
    tools = tool_registry.get_tools_for_agent("ad_manager")

    agent = create_react_agent(
        model=model,
        tools=tools,
        prompt=SystemMessage(content=AD_MANAGER_SYSTEM_PROMPT),
    )

    logger.info(
        f"Ad Manager Agent 已创建，工具数: {len(tools)}"
    )
    return agent
