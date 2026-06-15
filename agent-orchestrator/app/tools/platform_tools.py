"""平台操作工具集 - 调用 Python Worker 执行平台同步等任务"""
from langchain_core.tools import tool

from app.tools.base import GoServerClient, PythonWorkerClient


def create_platform_tools(
    worker_client: PythonWorkerClient,
    go_client: GoServerClient,
) -> list:
    """创建平台操作工具集"""

    @tool
    async def trigger_order_sync(
        shop_id: int,
        platform: str,
        app_key: str,
        app_secret: str,
        access_token: str,
    ) -> dict:
        """触发指定店铺的订单同步任务（异步）。返回 task_id 用于查询进度。"""
        return await worker_client.trigger_sync(
            shop_id=shop_id,
            platform=platform,
            app_key=app_key,
            app_secret=app_secret,
            access_token=access_token,
            sync_type="orders",
        )

    @tool
    async def trigger_logistics_sync(
        shop_id: int,
        platform: str,
        app_key: str,
        app_secret: str,
        access_token: str,
    ) -> dict:
        """触发指定店铺的物流同步任务（异步）。返回 task_id 用于查询进度。"""
        return await worker_client.trigger_sync(
            shop_id=shop_id,
            platform=platform,
            app_key=app_key,
            app_secret=app_secret,
            access_token=access_token,
            sync_type="logistics",
        )

    @tool
    async def get_sync_status(task_id: str) -> dict:
        """查询同步任务的执行状态。task_id 为触发同步时返回的任务ID。"""
        return await worker_client.get_sync_status(task_id)

    return [trigger_order_sync, trigger_logistics_sync, get_sync_status]
