"""智能规则 Agent"""
import logging

from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent

from app.llm.router import ModelRouter
from app.prompts.smart_rule import SMART_RULE_SYSTEM_PROMPT
from app.tools import ToolRegistry

logger = logging.getLogger(__name__)


def create_smart_rule_agent(
    model_router: ModelRouter,
    tool_registry: ToolRegistry,
):
    """创建智能规则 Agent（自然语言 -> 结构化规则）"""
    model = model_router.get_model("smart_rule")
    tools = tool_registry.get_tools_for_agent("smart_rule")

    agent = create_react_agent(
        model=model,
        tools=tools,
        prompt=SystemMessage(content=SMART_RULE_SYSTEM_PROMPT),
    )

    logger.info(
        f"Smart Rule Agent 已创建，工具数: {len(tools)}"
    )
    return agent
