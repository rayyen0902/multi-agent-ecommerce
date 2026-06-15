"""物流相关工具集"""
from langchain_core.tools import tool

from app.tools.base import GoServerClient


def create_logistics_tools(client: GoServerClient) -> list:
    """创建物流相关工具集"""

    @tool
    async def list_logistics(page: int = 1, page_size: int = 20) -> dict:
        """查询物流记录列表（分页）。返回物流信息包含物流公司、单号、状态等。"""
        return await client.get(
            "/logistics", params={"page": page, "page_size": page_size}
        )

    @tool
    async def get_logistics_by_order(order_id: int) -> dict:
        """根据订单ID查询物流信息。返回物流公司、单号、状态、轨迹等。"""
        return await client.get(f"/logistics/by-order/{order_id}")

    return [list_logistics, get_logistics_by_order]
