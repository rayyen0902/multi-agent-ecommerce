"""Agent Orchestrator - FastAPI 主入口"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config.settings import settings
from app.blackboard.redis_store import RedisBlackboardStore
from app.blackboard.pg_store import PgBlackboardStore
from app.blackboard.service import BlackboardService
from app.llm.router import ModelRouter
from app.llm.cost_tracker import CostTracker
from app.tools.base import GoServerClient, PythonWorkerClient
from app.tools import ToolRegistry
from app.agents.front_desk import FrontDeskAgent
from app.agents.pmo import PMOAgent
from app.agents.order_analyst import create_order_analyst_agent
from app.agents.smart_rule import create_smart_rule_agent
from app.agents.customer_service import create_customer_service_agent
from app.agents.data_analyst import create_data_analyst_agent
from app.agents.ad_manager import create_ad_manager_agent
from app.workflows.main_workflow import MainWorkflow

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------- 全局实例 ----------
blackboard: BlackboardService = None
workflow: MainWorkflow = None
cost_tracker = CostTracker()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    global blackboard, workflow

    logger.info("Agent Orchestrator 启动中...")

    # 1. 初始化黑板系统
    redis_store = RedisBlackboardStore(settings.redis.url)
    engine = create_async_engine(settings.db.dsn, echo=settings.debug)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    pg_store = PgBlackboardStore(session_factory)
    blackboard = BlackboardService(redis_store, pg_store)
    await blackboard.initialize()
    logger.info("黑板系统已初始化")

    # 2. 初始化工具层
    go_client = GoServerClient(settings.services.go_server_url)
    worker_client = PythonWorkerClient(settings.services.python_worker_url)
    tool_registry = ToolRegistry(go_client, worker_client)
    logger.info("工具层已初始化")

    # 3. 初始化模型路由
    model_router = ModelRouter(
        openai_api_key=settings.llm.openai_api_key,
        anthropic_api_key=settings.llm.anthropic_api_key,
    )
    logger.info("模型路由已初始化")

    # 4. 创建执行 Agent
    execution_agents = {
        "order_analyst": create_order_analyst_agent(model_router, tool_registry),
        "smart_rule": create_smart_rule_agent(model_router, tool_registry),
        "customer_service": create_customer_service_agent(model_router, tool_registry),
        "data_analyst": create_data_analyst_agent(model_router, tool_registry),
        "ad_manager": create_ad_manager_agent(model_router, tool_registry),
    }
    logger.info(f"执行 Agent 已创建: {list(execution_agents.keys())}")

    # 5. 创建前台和 PMO
    front_desk = FrontDeskAgent(model_router)
    pmo = PMOAgent(model_router, blackboard, execution_agents)
    logger.info("Front-desk + PMO Agent 已创建")

    # 6. 创建主编排工作流
    workflow = MainWorkflow(front_desk, pmo, blackboard)
    logger.info("主编排工作流已创建")

    # 注入依赖到 API 路由
    from app.api import chat as chat_api
    from app.api import tasks as tasks_api
    chat_api.set_dependencies(workflow, blackboard)
    tasks_api.set_dependencies(blackboard)

    logger.info("Agent Orchestrator 启动完成 ✓")

    yield

    # 清理
    await tool_registry.close()
    await blackboard.shutdown()
    await engine.dispose()
    logger.info("Agent Orchestrator 已关闭")


# ---------- FastAPI 应用 ----------

app = FastAPI(
    title="Ecom Order Hub - Agent Orchestrator",
    description="电商订单自动化 - 多 Agent 编排服务",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
from app.api.health import router as health_router
from app.api.chat import router as chat_router
from app.api.tasks import router as tasks_router

app.include_router(health_router)
app.include_router(chat_router)
app.include_router(tasks_router)


@app.get("/api/agent/cost-summary")
async def get_cost_summary():
    """获取 Token 用量和成本汇总"""
    return {"code": 0, "message": "success", "data": cost_tracker.get_summary()}
