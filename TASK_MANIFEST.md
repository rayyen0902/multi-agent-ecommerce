# 多 Agent 电商系统 — 运维任务单

> 最后更新: 2026-06-16
> 状态: 24 项安全加固已完成 (dfee177d)，进入持续运维阶段

---

## 已完成 (2026-06-15 ~ 2026-06-16)

| 类别 | 完成项 | 提交 |
|------|--------|------|
| 安全加固 | 24 项 CRITICAL/HIGH/MEDIUM/LOW 全部修复 | dfee177d |
| 部署 | SSH known_hosts 验证、Token stdin 传递 | dfee177d |
| 部署 | scp 传递 docker-compose.ecom.yml | 8e5e9805 |
| 部署 | Postgres/Redis 镜像从 GHCR 拉取 | 48aab60b |
| 部署 | 预拉取 DHD 基础镜像重试 | ce2a6cd5 |
| 基础设施 | Docker 加速器 + DNS + live-restore | d6480b18 |
| 运维 | 端口映射修复 + dev compose 对齐 | 本次 |

---

## 🔴 进行中

### Task A: 平台 API 集成 (P0 功能阻塞)

大量 `TODO` 桩代码，涉及核心业务流程：

| 文件 | 待实现 |
|------|--------|
| `python-worker/app/platforms/taobao/client.py` | `trade.fullinfo.get`, `logistics.trace.search` |
| `python-worker/app/platforms/jd/client.py` | `pop.order.search/get/ship`, 物流查询 |
| `python-worker/app/platforms/pdd/client.py` | `order.list.get/information.get`, `logistics.online.send` |
| `python-worker/app/tasks/order_tasks.py` | 店铺状态查询、订单写入、评价同步 |
| `python-worker/app/tasks/rule_tasks.py` | 规则匹配、库存预警、通知发送 |
| `python-worker/app/tasks/logistics_tasks.py` | 快递100/平台物流查询、轨迹更新 |
| `agent-orchestrator/app/tools/ad_tools.py` | 广告平台 API 对接 |
| `go-server/internal/handler/shop_handler.go` | Python Worker 触发同步 |
| `go-server/internal/handler/dashboard_handler.go` | 平台统计、店铺排行、订单分布 |

---

## 🟡 优化待办

### Task B: 添加优雅关闭

- [ ] `go-server/main.go` — SIGTERM/SIGINT 处理
- [ ] Python Dockerfile — `STOPSIGNAL SIGINT`

### Task C: 添加基础测试

- [ ] `go-server/internal/handler/auth_handler_test.go`
- [ ] `go-server/internal/middleware/auth_test.go`
- [ ] `python-worker/tests/test_rule_tasks.py`
- [ ] `python-worker/tests/test_match_condition.py`

### Task D: 结构化日志

- [ ] Go: 集成 `uber-go/zap`
- [ ] Python: 统一日志格式

### Task E: 容器非 root 用户

- [ ] 所有 Dockerfile 末尾添加 `USER nobody`

### Task F: WebSocket Token 改为 Header/首消息传递

- [ ] `web-frontend/src/services/chatApi.ts` — token 不在 URL 中
- [ ] 后端配合修改 WebSocket 认证逻辑

### Task G: 前端类型安全

- [ ] 定义 `PageResponse<T>`, `ApiResponse<T>`, `Order`, `Shop` 等核心类型
- [ ] 逐步消除 `any`

---

## 部署信息

- **仓库**: github.com/rayyen0902/multi-agent-ecommerce
- **镜像仓库**: ghcr.io/rayyen0902/ecom-*
- **部署服务器**: 通过 GitHub Actions → SSH 自动部署
- **访问地址**: https://knownot.cc/ecom/
- **环境变量**: `.env.ecom` (gitignored, 通过 GitHub Secret 注入)
