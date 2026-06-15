"""Celery 应用配置"""
from celery import Celery
from celery.schedules import crontab
from config.settings import settings

celery_app = Celery(
    "ecom_worker",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=False,
    task_routes={
        "app.tasks.order_tasks.*": {"queue": "order_sync"},
        "app.tasks.logistics_tasks.*": {"queue": "logistics"},
        "app.tasks.rule_tasks.*": {"queue": "rule_engine"},
    },
    beat_schedule={
        # 每15分钟同步所有店铺订单
        "sync-all-orders": {
            "task": "app.tasks.order_tasks.sync_all_orders",
            "schedule": 900.0,  # 15 minutes
        },
        # 每30分钟同步物流
        "sync-all-logistics": {
            "task": "app.tasks.logistics_tasks.sync_all_pending_logistics",
            "schedule": 1800.0,  # 30 minutes
        },
        # 每1小时检查库存预警
        "check-stock-alerts": {
            "task": "app.tasks.rule_tasks.check_stock_alerts",
            "schedule": 3600.0,  # 1 hour
        },
        # 每天凌晨2点自动评价
        "auto-review-expired": {
            "task": "app.tasks.order_tasks.auto_review_expired_orders",
            "schedule": crontab(hour=2, minute=0),
        },
    },
)

# 自动发现任务
celery_app.autodiscover_tasks(["app.tasks"])
