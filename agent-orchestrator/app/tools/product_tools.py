"""商品相关工具集"""
from langchain_core.tools import tool

from app.tools.base import GoServerClient


def create_product_tools(client: GoServerClient) -> list:
    """创建商品相关工具集"""

    @tool
    async def list_products(
        shop_id: int = 0, page: int = 1, page_size: int = 20
    ) -> dict:
        """查询商品列表（分页）。可按 shop_id 筛选。返回商品信息包含名称、价格、库存等。"""
        params: dict = {"page": page, "page_size": page_size}
        if shop_id:
            params["shop_id"] = shop_id
        return await client.get("/products", params=params)

    @tool
    async def get_stock_alerts(page: int = 1, page_size: int = 20) -> dict:
        """获取库存预警商品列表。返回库存低于预警阈值的商品。"""
        return await client.get(
            "/products/stock-alerts",
            params={"page": page, "page_size": page_size},
        )

    return [list_products, get_stock_alerts]
