# 多 Agent 自动化电商系统

一个基于多 Agent 协作的电商后端自动化平台，整合订单管理、广告投放、数据分析、客户服务等模块，通过智能调度实现电商运营流程的自动化。

## 架构概览

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Web Frontend   │────▶│  Agent Orchestrator│────▶│   Go Backend   │
│   (Next.js)      │     │   (FastAPI)       │     │   (Gin)         │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                  │                        │
                            ┌─────┴─────┐          ┌──────┴──────┐
                            │Python     │          │PostgreSQL   │
                            │Worker     │          │Redis        │
                            └───────────┘          └─────────────┘
```

## 项目结构

| 模块 | 说明 |
|------|------|
| `agent-orchestrator/` | Agent 编排中心（FastAPI），负责多 Agent 调度与黑板通信 |
| `go-server/` | Go 后端服务（Gin），提供核心业务 API |
| `python-worker/` | Python Worker，执行异步任务与 Agent 逻辑 |
| `web-frontend/` | Web 前端界面 |

## Agent 团队

- **Front Desk** — 前台接待，统一入口路由
- **PMO** — 项目管理与协调
- **Smart Rule** — 智能规则引擎
- **Ad Manager** — 广告管理 Agent
- **Customer Service** — 客服 Agent
- **Data Analyst** — 数据分析 Agent
- **Order Analyst** — 订单分析 Agent

## 快速开始

```bash
# 安装依赖
make dev-go
make dev-python
make dev-frontend

# 或使用 Docker Compose 一键启动
docker compose up --build
```

## 环境变量

复制 `.env.example` 到 `.env` 并填写相应配置：

```bash
cp .env.example .env
```

## License

MIT
