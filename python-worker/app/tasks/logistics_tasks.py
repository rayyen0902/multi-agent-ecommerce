"""物流同步 Celery 任务"""
import logging
from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, queue="logistics", max_retries=3)
def sync_order_logistics(self, order_id: int, tracking_no: str, company_code: str):
    """同步单个订单物流信息"""
    try:
        logger.info(f"同步订单 {order_id} 物流: {tracking_no}")
        # TODO: 调用快递100或平台物流API查询轨迹
        # TODO: 更新数据库物流记录
        return {"order_id": order_id, "status": "synced"}
    except Exception as exc:
        logger.error(f"物流同步失败 order={order_id}: {exc}")
        raise self.retry(exc=exc)


@celery_app.task(queue="logistics")
def sync_all_pending_logistics():
    """同步所有已发货未签收订单的物流"""
    logger.info("开始同步所有待跟踪物流...")
    # TODO: 查询所有 status in (pending, in_transit) 的物流记录
    # for logi in pending_logistics:
    #     sync_order_logistics.delay(logi.order_id, logi.tracking_no, logi.shipping_company_code)
    return "triggered"
