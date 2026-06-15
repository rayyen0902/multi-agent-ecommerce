"""规则相关工具集"""
from langchain_core.tools import tool

from app.tools.base import GoServerClient


def create_rule_tools(client: GoServerClient) -> list:
    """创建规则相关工具集"""

    @tool
    async def list_rules(page: int = 1, page_size: int = 20) -> dict:
        """查询自动化规则列表（分页）。返回规则信息包含名称、类型(auto_ship/auto_review/
        stock_alert/custom)、条件(conditions)、动作(actions)、启用状态等。"""
        return await client.get(
            "/rules", params={"page": page, "page_size": page_size}
        )

    return [list_rules]
