"""数据分析 Agent"""
import logging

from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent

from app.llm.router import ModelRouter
from app.prompts.data_analyst import DATA_ANALYST_SYSTEM_PROMPT
from app.tools import ToolRegistry

logger = logging.getLogger(__name__)


def create_data_analyst_agent(
    model_router: ModelRouter,
    tool_registry: ToolRegistry,
):
    """创建数据分析 Agent（生成分析报告和趋势预测）"""
    model = model_router.get_model("data_analyst")
    tools = tool_registry.get_tools_for_agent("data_analyst")

    agent = create_react_agent(
        model=model,
        tools=tools,
        prompt=SystemMessage(content=DATA_ANALYST_SYSTEM_PROMPT),
    )

    logger.info(
        f"Data Analyst Agent 已创建，工具数: {len(tools)}"
    )
    return agent
