"""看板相关工具集"""
from langchain_core.tools import tool

from app.tools.base import GoServerClient


def create_dashboard_tools(client: GoServerClient) -> list:
    """创建看板相关工具集"""

    @tool
    async def get_dashboard_overview() -> dict:
        """获取看板总览数据：今日订单数、今日销售额、昨日对比、待发货数等关键指标。"""
        return await client.get("/dashboard/overview")

    @tool
    async def get_sales_trend(days: int = 7) -> dict:
        """获取销售趋势数据。days 为查询天数（默认7天）。返回每日订单数和销售额。"""
        return await client.get("/dashboard/sales-trend", params={"days": days})

    @tool
    async def get_platform_stats() -> dict:
        """获取各平台(taobao/jd/pdd)的订单和销售额统计。"""
        return await client.get("/dashboard/platform-stats")

    @tool
    async def get_shop_ranking(limit: int = 10) -> dict:
        """获取店铺排行榜（按销售额）。limit 为返回数量（默认10）。"""
        return await client.get("/dashboard/shop-ranking", params={"limit": limit})

    @tool
    async def get_order_status_distribution() -> dict:
        """获取订单状态分布统计。返回各状态(pending/paid/shipped/delivered/completed/
        closed/refunding)的订单数量。"""
        return await client.get("/dashboard/order-status-distribution")

    return [
        get_dashboard_overview,
        get_sales_trend,
        get_platform_stats,
        get_shop_ranking,
        get_order_status_distribution,
    ]
