"""店铺相关工具集"""
from langchain_core.tools import tool

from app.tools.base import GoServerClient


def create_shop_tools(client: GoServerClient) -> list:
    """创建店铺相关工具集"""

    @tool
    async def list_shops(page: int = 1, page_size: int = 20) -> dict:
        """查询店铺列表（分页）。返回店铺信息包含名称、平台、状态、同步配置等。"""
        return await client.get("/shops", params={"page": page, "page_size": page_size})

    @tool
    async def get_shop_detail(shop_id: int) -> dict:
        """获取店铺详情，包含基本信息、平台授权状态、同步配置等。"""
        return await client.get(f"/shops/{shop_id}")

    @tool
    async def create_shop(
        name: str,
        platform: str,
        app_key: str = "",
        app_secret: str = "",
    ) -> dict:
        """创建新店铺。platform 可选: taobao/jd/pdd。"""
        return await client.post(
            "/shops",
            json_data={
                "name": name,
                "platform": platform,
                "app_key": app_key,
                "app_secret": app_secret,
            },
        )

    @tool
    async def update_shop(
        shop_id: int,
        name: str = "",
        status: int = -1,
        sync_enabled: bool = False,
    ) -> dict:
        """更新店铺信息。status: 1=启用, 0=禁用。sync_enabled 控制是否开启自动同步。"""
        data: dict = {}
        if name:
            data["name"] = name
        if status >= 0:
            data["status"] = status
        data["sync_enabled"] = sync_enabled
        return await client.put(f"/shops/{shop_id}", json_data=data)

    @tool
    async def trigger_shop_sync(shop_id: int) -> dict:
        """手动触发店铺数据同步（订单+物流）。"""
        return await client.post(f"/shops/{shop_id}/sync")

    return [
        list_shops,
        get_shop_detail,
        create_shop,
        update_shop,
        trigger_shop_sync,
    ]
