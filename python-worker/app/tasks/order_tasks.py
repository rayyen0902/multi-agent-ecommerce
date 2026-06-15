"""订单同步 Celery 任务"""
import logging
from datetime import datetime, timedelta

from app.tasks.celery_app import celery_app
from app.platforms import get_adapter

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, queue="order_sync", max_retries=3,
                 default_retry_delay=60, acks_late=True)
def sync_shop_orders(self, shop_id: int, platform: str,
                     app_key: str, app_secret: str,
                     access_token: str):
    """同步单个店铺的订单"""
    try:
        import asyncio
        adapter = get_adapter(platform, shop_id, app_key, app_secret, access_token)

        # 同步最近24小时的订单
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)

        async def _fetch():
            return await adapter.fetch_orders(start_time, end_time)

        orders = asyncio.run(_fetch())
        logger.info(f"店铺 {shop_id} 同步到 {len(orders)} 个订单")

        # TODO: 将订单写入数据库（通过 Go 服务 API 或直接写库）
        for order in orders:
            logger.info(f"  订单: {order.platform_order_no} - {order.status} - ¥{order.pay_amount}")

        return {"shop_id": shop_id, "count": len(orders)}

    except Exception as exc:
        logger.error(f"店铺 {shop_id} 订单同步失败: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(queue="order_sync")
def sync_all_orders():
    """遍历所有启用的店铺，分发同步子任务"""
    # TODO: 从数据库查询所有启用的店铺
    # 示例：shops = db.query(Shop).filter(status=1, sync_enabled=True).all()
    logger.info("开始同步所有店铺订单...")
    # for shop in shops:
    #     sync_shop_orders.delay(shop.id, shop.platform, ...)
    return "triggered"


@celery_app.task(queue="order_sync")
def auto_review_expired_orders():
    """自动评价超时订单"""
    logger.info("检查自动评价订单...")
    # TODO: 查询已签收超过N天且未评价的订单，调用平台评价API
    return "done"
