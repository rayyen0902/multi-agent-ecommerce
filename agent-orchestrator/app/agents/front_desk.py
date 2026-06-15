"""前台 Agent - 意图识别与路由（不执行任何业务操作）"""
import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage

from app.llm.router import ModelRouter
from app.prompts.front_desk import FRONT_DESK_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class FrontDeskAgent:
    """前台 Agent：理解用户意图，分类并提取实体，不调用任何工具"""

    def __init__(self, model_router: ModelRouter):
        self.model = model_router.get_model("front_desk")

    async def analyze_intent(self, user_input: str) -> dict:
        """分析用户意图，返回结构化结果

        Returns:
            {
                "intent_category": str,
                "intent_summary": str,
                "extracted_entities": dict,
                "confidence": float,
                "needs_clarification": bool,
                "clarification_question": str,
            }
        """
        messages = [
            SystemMessage(content=FRONT_DESK_SYSTEM_PROMPT),
            HumanMessage(content=user_input),
        ]

        response = await self.model.ainvoke(messages)
        content = response.content.strip()

        # 尝试解析 JSON
        try:
            # 处理可能的 markdown 代码块包裹
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
                content = content.strip()

            result = json.loads(content)
        except json.JSONDecodeError:
            logger.warning(f"Front-desk Agent 输出非 JSON: {content[:200]}")
            # 回退：尝试从文本中提取 JSON
            result = self._fallback_parse(content)

        return result

    @staticmethod
    def _fallback_parse(content: str) -> dict:
        """回退解析：当 LLM 未输出标准 JSON 时使用"""
        return {
            "intent_category": "general_query",
            "intent_summary": content[:200],
            "extracted_entities": {},
            "confidence": 0.5,
            "needs_clarification": True,
            "clarification_question": "抱歉，我没能完全理解您的需求。能否请您更具体地描述一下？",
        }
