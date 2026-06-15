# 多 Agent 电商系统 — 代码审查任务单

> 生成时间: 2026-06-15
> 审查范围: go-server / python-worker / agent-orchestrator / web-frontend / docker-compose / CI/CD
> 执行原则: 先修 CRITICAL → HIGH → MEDIUM → LOW，逐级推进

---

## 优先级总览

| 优先级 | 数量 | 说明 |
|--------|------|------|
| 🔴 CRITICAL | 6 | 必须上线前修复 |
| 🟠 HIGH | 8 | 强烈建议修复 |
| 🟡 MEDIUM | 6 | 建议修复 |
| 🟢 LOW | 4 | 锦上添花 |

---

## 🔴 CRITICAL — 必须在上线前修复

### Task 1: 移除迁移文件中的默认管理员密码

**严重程度:** 🔴 CRITICAL
**影响面:** 任何可查看仓库历史的人都能获得 admin 账号密码

**文件:** `go-server/migration/002_create_all_tables.sql` (约第 149-152 行)

**当前代码:**
```sql
INSERT INTO users (username, password, nickname, role, status)
VALUES ('admin', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', ...);
```
注释中写明密码为 `admin123`。

**修复方案:**
- 删除这段 INSERT 语句
- 如需初始化 admin 账号，改为通过 API 创建或在部署脚本中通过环境变量注入
- 或者保留 INSERT 但将密码改为从环境变量读取的占位符，并在部署文档中强调首次登录后必须修改

**验证方式:** 搜索迁移文件中不应再出现任何明文密码或已知 bcrypt hash

---

### Task 2: SSH 部署修复 — 启用主机密钥验证

**严重程度:** 🔴 CRITICAL
**影响面:** CI/CD 部署过程可能被中间人攻击劫持

**文件:** `.github/workflows/deploy-ecom.yml` (约第 88 行)

**当前代码:**
```bash
ssh -o StrictHostKeyChecking=no -i ~/.ssh/id_deploy ${DEPLOY_USER}@${DEPLOY_HOST} \
```

**修复方案 (二选一):**

方案 A — 使用 `accept-new`:
```bash
ssh -o StrictHostKeyChecking=accept-new -i ~/.ssh/id_deploy ${DEPLOY_USER}@${DEPLOY_HOST} \
```

方案 B — 预先填充 known_hosts（推荐）:
```yaml
- name: Setup SSH known_hosts
  run: |
    mkdir -p ~/.ssh
    echo "$DEPLOY_KEY" > ~/.ssh/id_deploy
    chmod 600 ~/.ssh/id_deploy
    ssh-keyscan -H "${{ secrets.DEPLOY_HOST }}" >> ~/.ssh/known_hosts

- name: Deploy to Server
  env:
    DEPLOY_HOST: ${{ secrets.DEPLOY_HOST }}
    DEPLOY_USER: ${{ secrets.DEPLOY_USER }}
    DEPLOY_KEY: ${{ secrets.DEPLOY_KEY }}
  run: |
    ssh -i ~/.ssh/id_deploy ${DEPLOY_USER}@${DEPLOY_HOST} \
      "cd /opt/ecom && ..."
```

**验证方式:** workflow 中不应再出现 `StrictHostKeyChecking=no`

---

### Task 3: GITHUB_TOKEN 通过 stdin 传递

**严重程度:** 🔴 CRITICAL
**影响面:** token 暴露在远程服务器进程列表中

**文件:** `.github/workflows/deploy-ecom.yml` (约第 90 行)

**当前代码:**
```bash
docker login ghcr.io -u ${GITHUB_ACTOR} -p '${{ secrets.GITHUB_TOKEN }}' \
```

**修复方案:**
```bash
echo '${{ secrets.GITHUB_TOKEN }}' | docker login ghcr.io -u ${GITHUB_ACTOR} --password-stdin \
```

**验证方式:** 远程服务器上 `ps aux` 不应再显示 docker login 的 token

---

### Task 4: 为所有服务添加 .dockerignore 文件

**严重程度:** 🔴 CRITICAL
**影响面:** 敏感文件（.env、.git 等）被打包进 Docker 镜像

**需要创建的文件:**
- `go-server/.dockerignore`
- `python-worker/.dockerignore`
- `agent-orchestrator/.dockerignore`
- `web-frontend/.dockerignore`

**修复方案:** 每个文件内容如下（根据实际需要微调）:
```
.git
.gitignore
.env
.env.*
*.md
Makefile
.dockerignore
.docker-compose*.yml
scripts/
.claude/
.github/
```

**验证方式:** 构建镜像后 `docker image inspect <image>` 检查 layers 中不含敏感文件

---

### Task 5: Go Dockerfile 移除 go mod tidy

**严重程度:** 🔴 CRITICAL
**影响面:** 构建结果不可复现，同一源码可能产出不同二进制

**文件:** `go-server/Dockerfile` (约第 8 行)

**当前代码:**
```dockerfile
RUN CGO_ENABLED=0 GOOS=linux go mod tidy
```

**修复方案:**
1. 在本地执行 `cd go-server && go mod tidy && go mod verify`
2. 提交更新后的 `go.mod` 和 `go.sum`
3. 从 Dockerfile 中删除该行

**验证方式:** Dockerfile 中不再包含 `go mod tidy`

---

### Task 6: JWT 添加算法验证

**严重程度:** 🔴 CRITICAL
**影响面:** 存在 JWT 算法混淆攻击风险

**文件:** `go-server/internal/middleware/auth.go` (约第 41 行)

**当前代码:**
```go
func ParseToken(tokenString string) (*jwt.Token, error) {
    token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
        return []byte(config.Get().JWT.Secret), nil
    })
    ...
}
```

**修复方案:**
```go
func ParseToken(tokenString string) (*jwt.Token, error) {
    token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
        if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
        }
        return []byte(config.Get().JWT.Secret), nil
    })
    ...
}
```

**验证方式:** 使用 RS256 签名的 token 应被拒绝，HS256 正常通过

---

## 🟠 HIGH — 强烈建议修复

### Task 7: 修复 SQL 注入 — sort 参数白名单

**严重程度:** 🟠 HIGH
**影响面:** 攻击者可通过 sort 参数注入任意 SQL

**文件:** `go-server/internal/repository/order_repo.go` (约第 89-101 行)

**当前代码:**
```go
sortField := "platform_created_at"
if filter.Sort != "" {
    sortField = filter.Sort
}
```

**修复方案:**
```go
allowedSortFields := map[string]bool{
    "platform_created_at": true,
    "status":            true,
    "pay_amount":        true,
    "updated_at":        true,
}
if sortField, ok := allowedSortFields[filter.Sort]; !ok {
    sortField = "platform_created_at"
}
```

**验证方式:** 传入 `sort=id;DROP TABLE orders--` 应被拒绝并使用默认排序

---

### Task 8: 添加 shop 级别授权中间件

**严重程度:** 🟠 HIGH
**影响面:** 任何登录用户可访问/修改任意店铺数据

**文件:** `go-server/internal/handler/shop_handler.go`

**修复方案:**
- 创建 `ShopAuthMiddleware` — 检查当前用户是否属于该 shop 的 owner/operator
- 在 shop CRUD 和 order list/detail 接口上应用此中间件
- 需要 users 表和 shops 表之间有关联关系（user_shop 关联表或 user.shop_id 字段）

**验证方式:** 用 user_A 的 token 尝试访问 user_B 管理的 shop，应返回 403

---

### Task 9: 登录接口添加速率限制

**严重程度:** 🟠 HIGH
**影响面:** 暴力破解攻击无防护

**文件:** `go-server/router/router.go` (约第 47 行)

**修复方案:**
```go
import "github.com/gin-contrib/limiter"

// 在 login 路由前添加
r.POST("/api/v1/auth/login", limiter.LimiterByStore(
    limiter.NewInMemoryStore(&limiter.Rate{
        Period:      15 * time.Minute,
        Limit:       10,  // 15分钟内最多10次
    }),
    authHandler.Login,
))
```

**验证方式:** 连续失败登录 10 次后，第 11 次应返回 429

---

### Task 10: Python HTTP 客户端添加超时

**严重程度:** 🟠 HIGH
**影响面:** 第三方 API 无响应时耗尽 Celery worker 资源

**需要修改的文件:**
- `python-worker/app/platforms/taobao/client.py`
- `python-worker/app/platforms/jd/client.py`
- `python-worker/app/platforms/pdd/client.py`

**修复方案:**
```python
# 所有 async with httpx.AsyncClient() 改为:
async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=5.0)) as client:
```

**验证方式:** 模拟目标 API 长时间不响应，客户端应在 10 秒后超时退出

---

### Task 11: Celery 服务添加健康检查依赖

**严重程度:** 🟠 HIGH
**影响面:** Celery 可能在 Redis/PostgreSQL 未就绪时启动，导致连接失败

**文件:** `docker-compose.ecom.yml` (celery-worker 和 celery-beat 部分)

**当前代码:**
```yaml
celery-worker:
    depends_on:
      - redis
      - postgres
```

**修复方案:**
```yaml
celery-worker:
    depends_on:
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
celery-beat:
    depends_on:
      redis:
        condition: service_healthy
```

**验证方式:** 重启容器后 celery 不应再出现连接失败的重启循环

---

### Task 12: 为所有服务添加资源限制

**严重程度:** 🟠 HIGH
**影响面:** 单个服务可能耗尽宿主机所有资源

**文件:** `docker-compose.ecom.yml`

**修复方案:** 为每个服务添加:
```yaml
deploy:
    resources:
        limits:
            cpus: '1.0'
            memory: 512M
        reservations:
            cpus: '0.25'
            memory: 128M
```

根据各服务实际资源需求调整数值。

**验证方式:** `docker compose config` 检查所有服务都有资源限制

---

### Task 13: 修复规则引擎 null 值比较 crash

**严重程度:** 🟠 HIGH
**影响面:** 缺失数据的订单会导致规则引擎任务崩溃

**文件:** `python-worker/app/tasks/rule_tasks.py` (约第 44-62 行)

**修复方案:** 在 `match_condition` 函数开头添加防御:
```python
def match_condition(current, operator, value):
    if current is None:
        return False
    # ... 原有逻辑
```

**验证方式:** 传入 null 值字段测试规则匹配，不应再抛出 TypeError

---

### Task 14: 前端 Token 存储改为 sessionStorage

**严重程度:** 🟠 HIGH
**影响面:** localStorage 中的 token 可被 XSS 窃取且跨会话持久

**文件:** `web-frontend/src/stores/useAuthStore.ts`

**当前代码:**
```typescript
persist({ name: 'auth-storage' })  // 默认使用 localStorage
```

**修复方案:**
```typescript
persist(
    ({ set, get }) => ({ ... }),
    {
        name: 'auth-storage',
        storage: sessionStorage,  // 改为 sessionStorage
    }
)
```

**验证方式:** 关闭标签页后 token 应清除，重新打开需重新登录

---

## 🟡 MEDIUM — 建议修复

### Task 15: Makefile 迁移到 docker compose v2

**严重程度:** 🟡 MEDIUM
**影响面:** `docker-compose` v1 在新系统上可能不可用

**文件:** `Makefile`

**修复方案:** 将所有 `docker-compose` 替换为 `docker compose`（注意中间有空格）

**验证方式:** 运行 `make build` / `make up` 确认正常工作

---

### Task 16: 修复部署健康检查

**严重程度:** 🟡 MEDIUM
**影响面:** 前端 404 也被视为部署成功

**文件:** `.github/workflows/deploy-ecom.yml` (约第 96 行)

**当前代码:**
```bash
curl -sf http://127.0.0.1:6300/health || echo 'Frontend health check skipped'
```

**修复方案:**
```bash
HEALTH_STATUS=$(curl -sf -o /dev/null -w '%{http_code}' http://127.0.0.1:6300/ || echo "000")
if [ "$HEALTH_STATUS" != "200" ]; then
    echo "WARNING: Frontend health check failed (HTTP $HEALTH_STATUS)"
else
    echo "Frontend health check passed"
fi
```

**验证方式:** 当前端不可用时，workflow 应输出 WARNING 而非静默跳过

---

### Task 17: 前端定义 TypeScript 类型替代 any

**严重程度:** 🟡 MEDIUM
**影响面:** 全项目使用 `any`，丧失类型安全

**需要修改的文件:** 全前端项目

**修复方案:** 定义核心接口:
```typescript
// src/types/index.ts
export interface PageResponse<T> {
    list: T[]
    total: number
    page: number
    page_size: number
}

export interface ApiResponse<T> {
    code: number
    message: string
    data: T
}

export interface Order {
    id: number
    order_no: string
    status: string
    platform: string
    shop_id: number
    pay_amount: number
    // ...
}

export interface Shop {
    id: number
    name: string
    platform: string
    // ... 不包含 AppSecret/AccessToken
}
```

**验证方式:** ESLint `no-explicit-any` 规则检查，剩余 any 使用应有充分理由

---

### Task 18: 前端 catch 块添加错误提示

**严重程度:** 🟡 MEDIUM
**影响面:** 请求失败时用户无感知

**需要修改的文件:** 全前端项目

**修复方案:** 将所有空 catch 块改为:
```typescript
catch (e) {
    console.error('API call failed:', e)
    message.error('操作失败，请稍后重试')
}
```

**验证方式:** 断网或后端不可用时，前端应显示错误提示

---

### Task 19: WebSocket token 改为 Header 传递

**严重程度:** 🟡 MEDIUM
**影响面:** token 记录在服务器访问日志中

**文件:** `web-frontend/src/services/chatApi.ts` (约第 31 行)

**当前代码:**
```typescript
const url = `${protocol}//${window.location.host}/ecom/api/agent/ws?token=${encodeURIComponent(token)}`
```

**修复方案:**
```typescript
const ws = new WebSocket(`${protocol}//${window.location.host}/ecom/api/agent/ws`)
ws.onopen = () => {
    ws.send(JSON.stringify({ type: 'auth', token }))
}
```

后端需配合修改认证逻辑，从 WebSocket 连接后的第一条消息中读取 token。

**验证方式:** 检查服务器 access log 中不应出现 token 参数

---

### Task 20: 移除 PyPI --trusted-host 标志

**严重程度:** 🟡 MEDIUM
**影响面:** 包下载过程可能被中间人攻击篡改

**需要修改的文件:**
- `python-worker/Dockerfile` (约第 6 行)
- `agent-orchestrator/Dockerfile` (约第 6 行)

**修复方案:**
```dockerfile
# 改为使用官方 PyPI
RUN pip install --no-cache-dir -r requirements.txt
# 或使用带 TLS 验证的镜像
RUN pip install --no-cache-dir \
    -i https://pypi.org/simple \
    -r requirements.txt
```

**验证方式:** Docker 构建不再输出 `WARNING` 关于 trusted-host

---

## 🟢 LOW — 锦上添花

### Task 21: 容器使用非 root 用户

**严重程度:** 🟢 LOW
**影响面:** 容器逃逸后攻击面更大

**需要修改的文件:** 所有 Dockerfile

**修复方案:** 在每个 Dockerfile 末尾添加:
```dockerfile
USER nobody
```

对于需要写文件的目录，提前创建非 root 用户并设置权限。

---

### Task 22: 添加优雅关闭信号

**严重程度:** 🟢 LOW
**影响面:** 部署时正在处理的请求被中断

**需要修改的文件:**
- `go-server/main.go` — 添加 SIGTERM/SIGINT 处理
- Python Dockerfile — 添加 `STOPSIGNAL SIGINT`

**修复方案 (Go):**
```go
shutdown := make(chan os.Signal, 1)
signal.Notify(shutdown, syscall.SIGTERM, syscall.SIGINT)
go func() {
    <-shutdown
    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()
    server.Shutdown(ctx)
}()
```

---

### Task 23: 添加结构化日志

**严重程度:** 🟢 LOW
**影响面:** 生产环境日志难以聚合和调试

**文件:** `go-server/main.go`

**修复方案:** 集成 `uber-go/zap`:
```go
import "go.uber.org/zap"

logger, _ := zap.NewProduction()
defer logger.Sync()
// 替换所有 log.Printf / log.Fatalf
```

---

### Task 24: 添加基础测试

**严重程度:** 🟢 LOW
**影响面:** 无测试保障，回归风险高

**需要创建的文件:**
- `go-server/internal/handler/auth_handler_test.go`
- `go-server/internal/middleware/auth_test.go`
- `python-worker/tests/test_rule_tasks.py`
- `python-worker/tests/test_match_condition.py`

**修复方案:**
- Go: 至少覆盖 JWT 生成/解析、shop CRUD 基本流程
- Python: 至少覆盖规则引擎 `match_condition` 的各种场景

---

## 执行顺序建议

```
第一轮 (紧急): Task 1 → 2 → 3 → 4 → 5 → 6    # CRITICAL 全部修复
第二轮 (重要): Task 7 → 8 → 9 → 10 → 11 → 12 → 13 → 14  # HIGH 全部修复
第三轮 (改进): Task 15 → 16 → 17 → 18 → 19 → 20  # MEDIUM 全部修复
第四轮 (优化): Task 21 → 22 → 23 → 24            # LOW 全部修复

每轮完成后: git commit -m "fix: <描述>" && git push
```

---

## 注意事项

1. **所有修改在本地完成**，通过 git commit + git push 提交到 GitHub
2. **GitHub Actions** 自动构建 Docker 镜像并推送到 ghcr.io
3. **部署到服务器**由 GitHub Actions 的 Deploy job 自动完成
4. 修改 `.env.ecom` 中的密码时，请使用强随机密码: `openssl rand -hex 32`
5. 每次只修一个 task，修完一个提交一次，方便回滚

---

## 环境变量强密码生成命令

```bash
# 生成强随机密码
openssl rand -hex 32

# 示例输出: 3a7b8c9d2e1f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b
```

部署到服务器前，务必更新 `.env.ecom` 中的:
- `DB_PASSWORD`
- `REDIS_PASSWORD`
- `JWT_SECRET`
