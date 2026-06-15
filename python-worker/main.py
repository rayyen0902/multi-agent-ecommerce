"""FastAPI 主入口 - Python 工作服务"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from config.settings import settings
from app.tasks.order_tasks import sync_shop_orders
from app.tasks.logistics_tasks import sync_order_logistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Python Worker 服务启动")
    yield
    logger.info("Python Worker 服务关闭")


app = FastAPI(
    title="Ecom Order Hub - Python Worker",
    description="电商订单自动化 - 平台对接与任务调度服务",
    version="1.0.0",
    lifespan=lifespan,
)


class HealthResponse(BaseModel):
    status: str
    service: str


class SyncRequest(BaseModel):
    shop_id: int
    platform: str
    app_key: str
    app_secret: str
    access_token: str
    sync_type: str = "orders"  # orders / logistics
    # logistics 同步所需的字段
    order_id: Optional[int] = None
    tracking_no: Optional[str] = None
    company_code: Optional[str] = None


class SyncResponse(BaseModel):
    task_id: str
    status: str


@app.get("/health", response_model=HealthResponse)
async def health_check():
    return HealthResponse(status="ok", service="python-worker")


@app.post("/api/sync/trigger", response_model=SyncResponse)
async def trigger_sync(req: SyncRequest):
    """触发同步任务（供 Go 服务调用）"""
    if req.sync_type == "orders":
        result = sync_shop_orders.delay(
            shop_id=req.shop_id,
            platform=req.platform,
            app_key=req.app_key,
            app_secret=req.app_secret,
            access_token=req.access_token,
        )
        return SyncResponse(task_id=str(result.id), status="queued")
    elif req.sync_type == "logistics":
        # 修复: 使用正确的参数映射
        result = sync_order_logistics.delay(
            order_id=req.order_id,
            tracking_no=req.tracking_no or "",
            company_code=req.company_code or "",
        )
        return SyncResponse(task_id=str(result.id), status="queued")

    return SyncResponse(task_id="", status="unknown_type")


@app.get("/api/sync/status/{task_id}")
async def get_sync_status(task_id: str):
    """查询同步任务状态"""
    from app.tasks.celery_app import celery_app
    result = celery_app.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
    }
