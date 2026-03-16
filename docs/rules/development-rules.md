# SOP 编排引擎 - 开发军规

## 一、技术栈

| 层面 | 技术 |
|------|------|
| 后端框架 | FastAPI |
| 后端语言 | Python 3.11+ |
| 数据库 | PostgreSQL + SQLAlchemy 2.0 |
| 消息队列 | Redis Streams |
| 前端框架 | Next.js 14 (App Router) |
| 前端语言 | React 18 + TypeScript |
| UI 组件 | shadcn/ui + TailwindCSS |
| 状态管理 | Zustand + TanStack Query |
| 流程编辑 | React Flow |

---

## 二、架构分层

```
API 层      → 接收请求，参数校验，返回响应
Service 层  → 业务逻辑编排，事务边界
Executor 层 → 节点执行实现，与外部系统交互
Model 层    → 数据定义，持久化
```

**依赖方向**：上层依赖下层，禁止反向依赖。

---

## 三、数据不可变

所有 Model 使用 Pydantic，创建后不修改：

```python
# 错误
execution.status = "running"

# 正确
return execution.model_copy(update={"status": "running"})
```

---

## 四、代码规范

### 4.1 类型注解（强制）

```python
# 正确
async def execute_node(execution: Execution, node: Node) -> NodeResult: ...

# 错误
async def execute_node(execution, node): ...
```

### 4.2 命名约定

| 类型 | 约定 | 示例 |
|------|------|------|
| 模块 | snake_case | `template_parser.py` |
| 类 | PascalCase | `FlowEngine` |
| 函数/变量 | snake_case | `start_execution` |
| 常量 | UPPER_SNAKE | `MAX_RETRIES` |
| 私有方法 | _前缀 | `_validate_node` |

### 4.3 长度限制

- 函数 ≤ 50 行
- 文件 ≤ 400 行

---

## 五、错误处理

### 5.1 异常层次

```python
class FlowError(Exception):
    """基类"""

class TemplateValidationError(FlowError):
    """模板验证失败"""

class NodeExecutionError(FlowError):
    """节点执行失败"""

class ContextVariableError(FlowError):
    """上下文变量解析失败"""
```

### 5.2 错误传播

```python
try:
    response = await self.http_client.post(...)
except httpx.RequestError as e:
    raise NodeExecutionError(f"OpenClaw 调用失败: {e}") from e
```

---

## 六、日志规范

使用 `structlog`，包含 `execution_id`、`node_id`：

```python
logger.info("node_started", execution_id=str(exec_id), node_id=node.id)
```

---

## 七、数据库规范

### 7.1 PostgreSQL 配置

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/sop_engine
```

### 7.2 表设计

```sql
CREATE TABLE templates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    yaml_content TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE executions (
    id TEXT PRIMARY KEY,
    template_id TEXT NOT NULL REFERENCES templates(id),
    status TEXT NOT NULL DEFAULT 'pending',
    params JSONB NOT NULL,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_executions_template ON executions(template_id);
CREATE INDEX idx_executions_status ON executions(status);
```

### 7.3 ORM 约定

- 使用 SQLAlchemy 2.0 异步模式
- 所有 Model 继承公共基类
- 使用 `asyncpg` 驱动

---

## 八、测试要求

### 7.1 测试层次

| 类型 | 位置 |
|------|------|
| 单元测试 | `tests/unit/` |
| 集成测试 | `tests/integration/` |
| E2E 测试 | `tests/e2e/` |

### 7.4 测试隔离

- 每个 `Execution` 使用独立的 `execution_id`
- Redis key 加前缀：`test:{execution_id}:...`
- PostgreSQL 使用独立测试数据库：`sop_engine_test`

### 7.2 覆盖率

- 最低 90%，新增代码 95%+
- `pytest --cov=app --cov-fail-under=90`

### 7.3 TDD 流程（强制）

1. 先写测试 → 红色
2. 写实现 → 绿色
3. 重构 → 仍绿色

---

## 八、Git 工作流

### 8.1 分支

```
main    → 稳定版本
feat/*  → 功能分支
fix/*   → 修复分支
```

### 8.2 提交规范

```
<type>: <description>
```

| type | 用途 |
|------|------|
| feat | 新功能 |
| fix | Bug 修复 |
| refactor | 重构 |
| test | 测试 |
| docs | 文档 |
| chore | 配置 |

### 8.3 合并要求

- 所有测试通过
- 覆盖率 ≥ 90%
- Review 自己的 diff

---

## 九、项目结构

```
sop-engine/
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── models/
│   │   ├── services/
│   │   ├── executors/
│   │   ├── api/
│   │   └── utils/
│   ├── tests/
│   └── pyproject.toml
│
├── frontend/               # Next.js 前端
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   ├── features/
│   │   ├── hooks/
│   │   ├── stores/
│   │   └── lib/
│   └── package.json
│
├── docs/
│   ├── plan.md
│   └── rules/
│       └── development-rules.md
│
└── CLAUDE.md
```

---

## 十、前端规范

### 10.1 状态管理

| 状态类型 | 存储 |
|----------|------|
| 服务端状态 | TanStack Query |
| 全局客户端状态 | Zustand |
| 局部状态 | useState |

### 10.2 组件设计

- Server Components 优先
- Client Components 按需
- 组件与逻辑分离

---

## 十一、API 规范

### 11.1 响应格式

```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

### 11.2 分页

```json
{
  "data": [...],
  "meta": { "total": 100, "page": 1, "page_size": 20 }
}
```

---

## 十二、OpenClaw 集成

### 12.1 设计原则

**SOP Engine 是 Agent 配置的唯一来源（Source of Truth）**
- OpenClaw 只负责加载配置，不修改配置
- 所有配置变更通过 SOP Engine 进行
- OpenClaw workspace 只是运行时加载目录

### 12.2 架构关系

```
SOP Engine (PostgreSQL)                    OpenClaw
┌─────────────────────────┐                ┌─────────────────────────┐
│ Agent 表                 │                │~/.openclaw/              │
│ - 元数据 (model, sandbox) │──同步────────→│openclaw.json             │
│ AgentConfigFile 表       │                │agents.list[] + bindings  │
│ - AGENTS.md, SOUL.md...  │──同步────────→│workspace-{agent_id}/     │
│ AgentBinding 表│                │- 所有配置文件            │
└─────────────────────────┘                └─────────────────────────┘
        │                                              │
        │ POST /hooks/agent                           │
        └──────────────────────────────────────────────┘
```

### 12.3 环境配置

```bash
OPENCLAW_URL=http://localhost:18789
OPENCLAW_TOKEN=your-hook-token
OPENCLAW_TIMEOUT=30
OPENCLAW_WORKSPACE_ROOT=~/.openclaw  # OpenClaw 根目录
```

### 12.4 Agent 配置文件

SOP Engine 管理的所有配置文件：

| 文件 | 作用 | 必需 |
|------|------|------|
| `AGENTS.md` | 操作指令、行为规则 | 是 |
| `SOUL.md` | 人设、语调、边界 | 是 |
| `USER.md` | 用户信息、称呼方式 | 是 |
| `IDENTITY.md` | Agent 名称、风格、emoji | 是 |
| `TOOLS.md` | 工具使用说明 | 否 |
| `HEARTBEAT.md` | 心跳检查清单 | 否 |
| `BOOT.md` | 启动清单 | 否 |
| `BOOTSTRAP.md` | 首次运行引导 | 否 |
| `MEMORY.md` | 长期记忆 | 否 |
| `memory/*.md` | 每日记忆日志 | 否 |
| `skills/*/SKILL.md` | Agent 专属技能 | 否 |

### 12.5 Agent 元数据

SOP Engine 管理的 openclaw.json agents.list[] 配置：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | Agent 唯一标识 |
| name | string | 显示名称 |
| workspace | string | 工作空间路径（自动生成） |
| default | boolean | 是否为默认 Agent |
| model.primary | string | 主模型 |
| model.fallbacks | string[] | 备选模型 |
| memorySearch.* | object | 记忆搜索配置 |
| heartbeat.every | string | 心跳间隔 |
| heartbeat.target | string | 心跳目标 |
| sandbox.mode | string | 沙箱模式（off/non-main/all） |
| sandbox.workspaceAccess | string | 工作空间访问（none/ro/rw） |
| sandbox.scope | string | 隔离范围（session/agent/shared） |
| sandbox.docker.* | object | Docker 容器配置 |
| tools.profile | string | 工具配置集 |
| tools.allow | string[] | 允许的工具 |
| tools.deny | string[] | 禁用的工具 |
| tools.exec.host | string | 执行位置（gateway/sandbox） |
| tools.exec.security | string | 安全模式 |
| tools.exec.safeBins | string[] | 允许执行的命令 |
| groupChat.mentionPatterns | string[] | 群聊触发模式 |

### 12.6 同步机制

**创建 Agent 时**：
1. 在 PostgreSQL 创建 Agent 记录和默认配置文件
2. 创建 workspace 目录：`{OPENCLAW_WORKSPACE_ROOT}/{agent_id}/`
3. 写入所有配置文件
4. 更新 openclaw.json 的 agents.list[]

**更新 Agent 时**：
1. 更新 PostgreSQL 中的配置
2. 同步写入 workspace 文件
3. 如有元数据变更，更新 openclaw.json

**删除 Agent 时**：
1. 删除 PostgreSQL 中的记录
2. 删除 workspace 目录
3. 从 openclaw.json 移除对应条目

### 12.7 Webhook API

**端点**: `POST {OPENCLAW_URL}/hooks/agent`

**认证**:
```
Authorization: Bearer {OPENCLAW_TOKEN}
```

**请求格式**:
```json
{
  "message": "string (required) - 发送给 Agent 的提示词",
  "agentId": "string (optional) - 目标 Agent ID",
  "name": "string (optional) - Hook 名称",
  "sessionKey": "string (optional) - 会话标识",
  "wakeMode": "now | next-heartbeat",
  "model": "string (optional) - 模型覆盖",
  "thinking": "low | medium | high",
  "timeoutSeconds": 120
}
```

### 12.8 YAML 节点定义

```yaml
security_check:
  type: agent
  agentId: security-scanner      # SOP Engine 管理的 Agent ID
  message: "扫描 {repo_path} 的安全漏洞"
  model: "anthropic/claude-3-5-sonnet"  # 可选覆盖
  thinking: high                 # 可选
  timeoutSeconds: 120            # 可选
  output_var: security_report
```

### 12.9 重试策略

- 超时：30 秒（默认）
- 重试：3 次，指数退避（1s, 2s, 4s）
- 仅网络错误重试，4xx 错误不重试

---

## 十三、安全规范

### 13.1 密钥管理

- **禁止硬编码**：所有密钥、Token、密码必须通过环境变量注入
- **环境变量验证**：启动时验证必需的环境变量存在
- **日志脱敏**：禁止在日志中输出密钥、Token、密码
- **API 响应脱敏**：凭证值显示为 `***`

### 13.2 输入验证

- API 层 Pydantic 强制校验
- YAML 模板解析时验证节点类型和引用
- 文件上传限制（大小、类型、扩展名）
- 禁止直接使用用户输入构造 SQL/命令

### 13.3 命令执行安全

- **script 节点命令白名单**：只允许预定义的安全命令
- **禁止命令注入**：使用参数列表 `subprocess.run(["cmd", arg1, arg2])`
- **禁止 shell=True**：避免 shell 解析特殊字符
- **超时控制**：所有命令执行必须有超时限制

### 13.4 数据库安全

- 所有查询使用 SQLAlchemy ORM 或参数化查询
- 禁止字符串拼接 SQL
- 敏感数据加密存储（AES-256）
- 凭证表字段加密

### 13.5 API 安全

- 所有端点添加速率限制
- 敏感操作需要认证
- 错误消息不暴露内部细节
- CORS 配置白名单

### 13.6 OpenClaw 集成安全

- Webhook Token 存储在环境变量
- HTTPS 通信（生产环境强制）
- 请求超时控制
- 网络错误重试（4xx 不重试）

### 13.7 凭证管理（REQ-0001-005）

- 凭证加密存储（PostgreSQL + AES-256）
- 同步到 OpenClaw credentials 目录时保持加密
- 凭证轮换提醒
- 凭证变更审计日志

---

## 十四、依赖管理

### 14.1 后端

```toml
[project]
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn>=0.27.0",
    "sqlalchemy>=2.0.0",
    "asyncpg>=0.29.0",
    "pydantic>=2.5.0",
    "pyyaml>=6.0",
    "redis>=5.0.0",
    "httpx>=0.26.0",
    "structlog>=24.0.0",
]
```

### 14.2 前端

```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "@xyflow/react": "^12.0.0",
    "zustand": "^4.5.0",
    "@tanstack/react-query": "^5.0.0"
  }
}
```

---

## 十五、检查清单

| 阶段 | 检查项 |
|------|--------|
| 编码前 | 需求明确、TDD |
| 编码中 | 类型完整、长度限制 |
| 编码后 | 不可变、错误处理、日志 |
| 提交前 | 检查通过、覆盖率 ≥90% |

---

## 十六、禁止事项

- 禁止跳过测试提交
- 禁止 `except: pass`
- 禁止硬编码超时/重试
- 禁止前端直接调用外部 API
