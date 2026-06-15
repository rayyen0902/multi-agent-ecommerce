"""模型配置与实例化"""
from dataclasses import dataclass, field


@dataclass
class ModelConfig:
    """LLM 模型配置"""
    name: str
    provider: str          # "openai" / "anthropic"
    model_id: str
    tier: str              # "strong" / "medium" / "light"
    max_tokens: int = 4096
    temperature: float = 0.3
    cost_per_1k_input: float = 0.0   # USD
    cost_per_1k_output: float = 0.0  # USD


MODEL_CONFIGS: dict[str, ModelConfig] = {
    # ---- 强模型：复杂推理、规则生成、验收评估 ----
    "claude_sonnet": ModelConfig(
        name="Claude Sonnet 4",
        provider="anthropic",
        model_id="claude-sonnet-4-20250514",
        tier="strong",
        max_tokens=8192,
        temperature=0.3,
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
    ),
    "gpt4o": ModelConfig(
        name="GPT-4o",
        provider="openai",
        model_id="gpt-4o-2024-08-06",
        tier="strong",
        max_tokens=8192,
        temperature=0.3,
        cost_per_1k_input=0.0025,
        cost_per_1k_output=0.01,
    ),

    # ---- 中等模型：数据分析、客服生成 ----
    "gpt4o_mini": ModelConfig(
        name="GPT-4o-mini",
        provider="openai",
        model_id="gpt-4o-mini-2024-07-18",
        tier="medium",
        max_tokens=4096,
        temperature=0.5,
        cost_per_1k_input=0.00015,
        cost_per_1k_output=0.0006,
    ),
    "claude_haiku": ModelConfig(
        name="Claude Haiku 3.5",
        provider="anthropic",
        model_id="claude-3-5-haiku-20241022",
        tier="medium",
        max_tokens=4096,
        temperature=0.5,
        cost_per_1k_input=0.0008,
        cost_per_1k_output=0.004,
    ),

    # ---- 轻量模型：意图识别、简单分类 ----
    "gpt4o_nano": ModelConfig(
        name="GPT-4o-mini (light)",
        provider="openai",
        model_id="gpt-4o-mini-2024-07-18",
        tier="light",
        max_tokens=2048,
        temperature=0.1,
        cost_per_1k_input=0.00015,
        cost_per_1k_output=0.0006,
    ),
}


def create_chat_model(config: ModelConfig, api_key: str = ""):
    """根据配置创建 LangChain ChatModel 实例"""
    if config.provider == "openai":
        from langchain_openai import ChatOpenAI
        kwargs = {
            "model": config.model_id,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
        }
        if api_key:
            kwargs["api_key"] = api_key
        return ChatOpenAI(**kwargs)

    elif config.provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        kwargs = {
            "model": config.model_id,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
        }
        if api_key:
            kwargs["api_key"] = api_key
        return ChatAnthropic(**kwargs)

    else:
        raise ValueError(f"不支持的模型提供商: {config.provider}")
