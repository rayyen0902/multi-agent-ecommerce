"""Token 用量与成本追踪"""
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from app.llm.models import ModelConfig

logger = logging.getLogger(__name__)


@dataclass
class UsageRecord:
    """单次调用记录"""
    agent_name: str
    model_name: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class CostTracker:
    """Token 用量与成本追踪器"""

    def __init__(self):
        self._records: list[UsageRecord] = []
        self._total_input_tokens: int = 0
        self._total_output_tokens: int = 0
        self._total_cost_usd: float = 0.0

    def record_usage(
        self,
        agent_name: str,
        model_config: ModelConfig,
        input_tokens: int,
        output_tokens: int,
    ) -> UsageRecord:
        """记录一次模型调用的用量"""
        cost = (
            (input_tokens / 1000) * model_config.cost_per_1k_input
            + (output_tokens / 1000) * model_config.cost_per_1k_output
        )

        record = UsageRecord(
            agent_name=agent_name,
            model_name=model_config.name,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
        )

        self._records.append(record)
        self._total_input_tokens += input_tokens
        self._total_output_tokens += output_tokens
        self._total_cost_usd += cost

        logger.debug(
            f"CostTracker: {agent_name} used {model_config.name} - "
            f"in={input_tokens}, out={output_tokens}, cost=${cost:.6f}"
        )
        return record

    def get_summary(self) -> dict:
        """获取成本汇总"""
        # 按 Agent 分组统计
        agent_costs: dict[str, dict] = {}
        for r in self._records:
            if r.agent_name not in agent_costs:
                agent_costs[r.agent_name] = {
                    "calls": 0,
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "cost_usd": 0.0,
                }
            agent_costs[r.agent_name]["calls"] += 1
            agent_costs[r.agent_name]["input_tokens"] += r.input_tokens
            agent_costs[r.agent_name]["output_tokens"] += r.output_tokens
            agent_costs[r.agent_name]["cost_usd"] += r.cost_usd

        return {
            "total_calls": len(self._records),
            "total_input_tokens": self._total_input_tokens,
            "total_output_tokens": self._total_output_tokens,
            "total_cost_usd": round(self._total_cost_usd, 6),
            "by_agent": agent_costs,
        }

    def get_records(
        self, agent_name: str = None, limit: int = 100
    ) -> list[UsageRecord]:
        """获取用量记录列表"""
        records = self._records
        if agent_name:
            records = [r for r in records if r.agent_name == agent_name]
        return records[-limit:]

    def reset(self) -> None:
        """重置所有统计"""
        self._records.clear()
        self._total_input_tokens = 0
        self._total_output_tokens = 0
        self._total_cost_usd = 0.0
