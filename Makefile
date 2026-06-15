.PHONY: help dev-go dev-python dev-frontend dev-agent dev build up down logs

help: ## 显示帮助
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ===== 开发模式 =====
dev-go: ## 启动 Go 服务 (开发)
	cd go-server && go run main.go

dev-python: ## 启动 Python Worker (开发)
	cd python-worker && uvicorn main:app --reload --port 8000

dev-celery: ## 启动 Celery Worker
	cd python-worker && celery -A app.tasks.celery_app worker -l info -Q order_sync,logistics,rule_engine

dev-celery-beat: ## 启动 Celery Beat
	cd python-worker && celery -A app.tasks.celery_app beat -l info

dev-frontend: ## 启动前端开发服务器
	cd web-frontend && npm run dev

dev-agent: ## 启动 Agent 编排服务 (开发)
	cd agent-orchestrator && uvicorn app.main:app --reload --port 9000

# ===== Docker =====
build: ## 构建所有 Docker 镜像
	docker-compose build

up: ## 启动所有服务
	docker-compose up -d

down: ## 停止所有服务
	docker-compose down

logs: ## 查看所有服务日志
	docker-compose logs -f

logs-go: ## 查看 Go 服务日志
	docker-compose logs -f go-server

logs-python: ## 查看 Python 服务日志
	docker-compose logs -f python-worker

logs-celery: ## 查看 Celery 日志
	docker-compose logs -f celery-worker

logs-agent: ## 查看 Agent 编排服务日志
	docker-compose logs -f agent-orchestrator

# ===== 数据库 =====
db-migrate: ## 运行数据库迁移
	docker-compose exec postgres psql -U ecom -d ecom_order_hub -f /docker-entrypoint-initdb.d/001_create_shops.sql
	docker-compose exec postgres psql -U ecom -d ecom_order_hub -f /docker-entrypoint-initdb.d/002_create_all_tables.sql

db-reset: ## 重置数据库 (危险!)
	docker-compose down -v
	docker-compose up -d postgres redis

# ===== 工具 =====
go-deps: ## 安装 Go 依赖
	cd go-server && GOPROXY=https://goproxy.cn,direct go mod tidy

frontend-deps: ## 安装前端依赖
	cd web-frontend && npm install

agent-deps: ## 安装 Agent 服务依赖
	cd agent-orchestrator && pip install -r requirements.txt
