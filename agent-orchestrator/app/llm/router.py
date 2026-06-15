"""模型路由器 - 根据 Agent 角色和场景选择最优模型"""
import logging
from typing import Optional

from app.llm.models import MODEL_CONFIGS, ModelConfig, create_chat_model

logger = logging.getLogger(__name__)


# Agent 名称 -> 模型级别映射
AGENT_MODEL_TIER: dict[str, str] = {
    "front_desk": "light",
    "pmo": "strong",
    "order_analyst": "medium",
    "smart_rule": "strong",
    "customer_service": "medium",
    "data_analyst": "strong",
    "ad_manager": "strong",
}

# 特殊场景强制指定模型
FORCE_MODEL_RULES: dict[str, str] = {
    "pmo_review": "claude_sonnet",
    "revision_guidance": "claude_sonnet",
}


class ModelRouter:
    """模型路由器：根据任务类型和场景选择最优模型"""

    def __init__(
        self,
        openai_api_key: str = "",
        anthropic_api_key: str = "",
    ):
        self._openai_key = openai_api_key
        self._anthropic_key = anthropic_api_key
        self._cache: dict[str, object] = {}

    def get_model(self, agent_name: str, scenario: str = None):
        """获取模型实例

        Args:
            agent_name: Agent 名称
            scenario: 特殊场景标识（如 pmo_review, revision_guidance）

        Returns:
            LangChain ChatModel 实例
        """
        cache_key = f"{agent_name}:{scenario or 'default'}"

        if cache_key in self._cache:
            return self._cache[cache_key]

        # 特殊场景优先
        if scenario and scenario in FORCE_MODEL_RULES:
            config = MODEL_CONFIGS[FORCE_MODEL_RULES[scenario]]
        else:
            tier = AGENT_MODEL_TIER.get(agent_name, "medium")
            config = self._select_best_cost_model(tier)

        api_key = self._get_api_key(config.provider)
        model = create_chat_model(config, api_key)

        self._cache[cache_key] = model
        logger.info(
            f"ModelRouter: {agent_name}({scenario or 'default'}) -> {config.name}"
        )
        return model

    def _select_best_cost_model(self, tier: str) -> ModelConfig:
        """在同级别模型中选择性价比最优的"""
        candidates = [
            c for c in MODEL_CONFIGS.values() if c.tier == tier
        ]
        if not candidates:
            # 降级到 medium
            candidates = [
                c for c in MODEL_CONFIGS.values() if c.tier == "medium"
            ]
        return min(
            candidates,
            key=lambda c: c.cost_per_1k_input + c.cost_per_1k_output,
        )

    def _get_api_key(self, provider: str) -> str:
        if provider == "openai":
            return self._openai_key
        elif provider == "anthropic":
            return self._anthropic_key
        return ""

    def get_model_config(self, agent_name: str, scenario: str = None) -> ModelConfig:
        """获取模型配置（不创建实例），用于成本追踪"""
        if scenario and scenario in FORCE_MODEL_RULES:
            return MODEL_CONFIGS[FORCE_MODEL_RULES[scenario]]
        tier = AGENT_MODEL_TIER.get(agent_name, "medium")
        return self._select_best_cost_model(tier)
