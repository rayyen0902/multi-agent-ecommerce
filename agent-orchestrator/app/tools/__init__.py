"""工具注册表 - 按 Agent 角色分配工具集"""
from app.tools.base import GoServerClient, PythonWorkerClient
from app.tools.order_tools import create_order_tools
from app.tools.shop_tools import create_shop_tools
from app.tools.product_tools import create_product_tools
from app.tools.logistics_tools import create_logistics_tools
from app.tools.rule_tools import create_rule_tools
from app.tools.dashboard_tools import create_dashboard_tools
from app.tools.platform_tools import create_platform_tools
from app.tools.ad_tools import create_ad_tools


# Agent 名称 -> 可用工具组映射
AGENT_TOOL_MAP: dict[str, list[str]] = {
    "order_analyst": ["order", "dashboard", "product", "logistics"],
    "smart_rule": ["rule", "order", "shop", "platform"],
    "customer_service": ["order", "logistics", "shop", "platform"],
    "data_analyst": ["dashboard", "order", "product", "shop"],
    "ad_manager": ["ad", "dashboard", "product"],
}


class ToolRegistry:
    """工具注册表：统一管理所有工具，按 Agent 角色分配"""

    def __init__(
        self,
        go_client: GoServerClient,
        worker_client: PythonWorkerClient,
    ):
        self.go_client = go_client
        self.worker_client = worker_client

        self.all_tools: dict[str, list] = {
            "order": create_order_tools(go_client),
            "shop": create_shop_tools(go_client),
            "product": create_product_tools(go_client),
            "logistics": create_logistics_tools(go_client),
            "rule": create_rule_tools(go_client),
            "dashboard": create_dashboard_tools(go_client),
            "platform": create_platform_tools(worker_client, go_client),
            "ad": create_ad_tools(),
        }

    def get_tools_for_agent(self, agent_name: str) -> list:
        """根据 Agent 名称返回对应的工具集"""
        tool_keys = AGENT_TOOL_MAP.get(agent_name, [])
        tools = []
        for key in tool_keys:
            tools.extend(self.all_tools.get(key, []))
        return tools

    def get_all_tools(self) -> list:
        """返回全部工具"""
        tools = []
        for tool_list in self.all_tools.values():
            tools.extend(tool_list)
        return tools

    async def close(self) -> None:
        await self.go_client.close()
        await self.worker_client.close()
