"""订单相关工具集"""
from langchain_core.tools import tool

from app.tools.base import GoServerClient


def create_order_tools(client: GoServerClient) -> list:
    """创建订单相关工具集"""

    @tool
    async def list_orders(
        status: str = "",
        platform: str = "",
        shop_id: int = 0,
        keyword: str = "",
        date_from: str = "",
        date_to: str = "",
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """查询订单列表。支持按状态(pending/paid/shipped/delivered/completed/closed/refunding)、
        平台(taobao/jd/pdd)、店铺ID、关键词、日期范围(格式YYYY-MM-DD)筛选。返回分页结果，
        包含list(订单数组)、total(总数)、page、page_size。"""
        params: dict = {"page": page, "page_size": page_size}
        if status:
            params["status"] = status
        if platform:
            params["platform"] = platform
        if shop_id:
            params["shop_id"] = shop_id
        if keyword:
            params["keyword"] = keyword
        if date_from:
            params["date_from"] = date_from
        if date_to:
            params["date_to"] = date_to
        return await client.get("/orders", params=params)

    @tool
    async def get_order_detail(order_id: int) -> dict:
        """获取订单详情，包含订单基本信息、订单明细(items)、物流信息(logistics)。"""
        return await client.get(f"/orders/{order_id}")

    @tool
    async def get_order_by_platform_no(platform_order_no: str) -> dict:
        """通过平台订单号查询订单。platform_order_no 是淘宝/京东/拼多多等平台的原始订单号。"""
        return await client.get(f"/orders/by-platform/{platform_order_no}")

    @tool
    async def update_order_remark(order_id: int, seller_remark: str) -> dict:
        """更新订单的卖家备注。seller_remark 为备注文本内容。"""
        return await client.put(
            f"/orders/{order_id}/remark",
            json_data={"seller_remark": seller_remark},
        )

    @tool
    async def update_order_tags(order_id: int, tags: list[str]) -> dict:
        """更新订单标签。标签用于分类和筛选，如['VIP客户', '加急', '赠品']。"""
        return await client.put(
            f"/orders/{order_id}/tags",
            json_data={"tags": tags},
        )

    @tool
    async def ship_order(
        order_id: int, shipping_company: str, tracking_no: str
    ) -> dict:
        """对单个订单执行发货操作。仅'paid'(待发货)状态的订单可发货。
        shipping_company 为物流公司名，tracking_no 为快递单号。"""
        return await client.post(
            f"/orders/{order_id}/ship",
            json_data={
                "shipping_company": shipping_company,
                "tracking_no": tracking_no,
            },
        )

    @tool
    async def batch_ship_orders(items: list[dict]) -> dict:
        """批量发货。items 格式: [{"order_id": 1, "shipping_company": "顺丰", "tracking_no": "SF123"}]。
        返回失败订单的错误信息列表。"""
        return await client.post("/orders/batch-ship", json_data={"items": items})

    @tool
    async def get_order_stats_overview() -> dict:
        """获取订单统计概览：今日订单数(today_order_count)、今日销售额(today_sales_amount)、
        待发货数(pending_ship_count)、库存预警数(stock_alert_count)。"""
        return await client.get("/orders/stats/overview")

    return [
        list_orders,
        get_order_detail,
        get_order_by_platform_no,
        update_order_remark,
        update_order_tags,
        ship_order,
        batch_ship_orders,
        get_order_stats_overview,
    ]
