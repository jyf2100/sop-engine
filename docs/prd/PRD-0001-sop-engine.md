# PRD-0001: SOP 编排引擎

## Vision

构建一个基于 OpenClaw 的 SOP（标准作业流程）编排平台，让用户能够通过 YAML 模板定义工作流，系统自动编排执行，支持条件分支、并行执行、循环重试、人工审批等高级特性。

**最终用户**：运维工程师、开发团队、业务流程管理员
**核心价值**：将复杂的手动流程自动化、可追溯、可审批
**成功标准**：用户能通过 YAML 定义一个完整流程，一键执行，实时监控，按需审批

---

## REQ-0001-001: 项目骨架搭建

**动机**：建立可运行的项目结构，为后续开发提供基础

**范围**：
- 后端目录结构（app/models, services, executors, api, utils）
- 前端目录结构（src/app, components, features, hooks, stores, lib）
- 配置文件（pyproject.toml, package.json, docker-compose.yml）
- 开发工具配置（ruff, pyright, eslint, prettier）

**非目标**：
- 不包含业务逻辑实现
- 不包含数据库迁移

**验收口径**：
- [ ] `uvicorn app.main:app` 启动成功，返回 200
- [ ] `pnpm dev` 启动成功，访问 localhost:3000 返回页面
- [ ] `pytest` 运行成功（可无测试用例）
- [ ] `ruff check .` 通过
- [ ] `pyright` 通过

---

## REQ-0001-002: 数据库模型定义

**动机**：定义核心数据结构，为流程模板、执行记录、Agent 配置提供持久化

**范围**：
- Template 模型（id, name, version, yaml_content, created_at, updated_at）
- Execution 模型（id, template_id, status, params, started_at, completed_at）
- NodeExecution 模型（id, execution_id, node_id, status, input, output, started_at, completed_at）
- **Agent 模型**（id, name, workspace_path, model_config, sandbox_config, tools_config, created_at, updated_at）
- **AgentConfigFile 模型**（id, agent_id, file_type, content, created_at, updated_at）
- SQLAlchemy 异步配置
- PostgreSQL 连接

**非目标**：
- 不包含复杂查询
- 不包含数据迁移脚本

**验收口径**：
- [ ] 模型定义符合 Pydantic v2 规范
- [ ] 异步数据库连接可建立
- [ ] 单元测试验证模型字段存在

---

## REQ-0001-003: Agent 配置管理

**动机**：SOP Engine 统一管理 OpenClaw Agent 的所有配置，OpenClaw 只负责加载

**设计原则**：
- SOP Engine 是 Agent 配置的唯一来源（Source of Truth）
- OpenClaw workspace 只是运行时加载目录
- 所有配置变更通过 SOP Engine 进行，OpenClaw 被动接收

**Agent 配置文件**：

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

**Agent 元数据**（对应 openclaw.json 的 agents.list[]）：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | Agent 唯一标识 |
| name | string | 显示名称 |
| workspace | string | 工作空间路径（自动生成） |
| default | boolean | 是否为默认 Agent |
| model.primary | string | 主模型 |
| model.fallbacks | string[] | 备选模型 |
| memorySearch.enabled | boolean | 是否启用记忆搜索 |
| memorySearch.provider | string | 向量提供商 |
| memorySearch.model | string | 嵌入模型 |
| heartbeat.every | string | 心跳间隔 |
| heartbeat.target | string | 心跳目标 |
| sandbox.mode | string | 沙箱模式（off/non-main/all） |
| sandbox.workspaceAccess | string | 工作空间访问（none/ro/rw） |
| sandbox.scope | string | 隔离范围（session/agent/shared） |
| sandbox.docker | object | Docker 容器配置 |
| tools.profile | string | 工具配置集 |
| tools.allow | string[] | 允许的工具 |
| tools.deny | string[] | 禁用的工具 |
| tools.exec.host | string | 执行位置 |
| tools.exec.security | string | 安全模式 |
| tools.exec.safeBins | string[] | 允许执行的命令 |
| groupChat.mentionPatterns | string[] | 群聊触发模式 |

**范围**：
- Agent CRUD API
- 配置文件存储（PostgreSQL）
- 配置文件版本管理
- Agent 元数据管理（完整的 openclaw.json agents.list[] 配置）
- 同步到 OpenClaw：
  - 写入 workspace 文件到 `{OPENCLAW_WORKSPACE_ROOT}/{agent_id}/`
  - 更新 openclaw.json 的 agents.list[] 和 bindings
- 自动生成 openclaw.json 绑定规则

**验收口径**：
- [ ] 创建 Agent 时生成默认配置文件和元数据
- [ ] 更新配置文件后同步到 OpenClaw workspace
- [ ] 更新元数据后同步到 openclaw.json
- [ ] 删除 Agent 时清理 workspace 和 openclaw.json 条目
- [ ] 单元测试覆盖 CRUD 和同步流程

---

## REQ-0001-004: OpenClaw 主配置管理

**动机**：SOP Engine 统一管理 OpenClaw 的主配置文件（openclaw.json）

**openclaw.json 配置结构**：

| 字段 | 类型 | 说明 |
|------|------|------|
| env.vars | object | 环境变量 |
| logging.* | object | 日志配置 |
| agents.defaults.* | object | Agent 默认配置 |
| agents.list[] | array | Agent 列表（由 Agent 配置管理生成） |
| bindings[] | array | 路由绑定（由 Agent 配置管理生成） |
| channels.* | object | 渠道配置（WhatsApp/Telegram/Discord...） |
| commands.* | object | 命令配置 |
| gateway.* | object | 网关配置 |
| messages.* | object | 消息配置 |
| hooks.* | object | Webhook 配置 |
| cron.* | object | 定时任务配置 |
| sandbox.* | object | 沙箱全局配置 |
| tools.* | object | 工具全局配置 |
| discovery.* | object | 发现服务配置 |

**范围**：
- openclaw.json CRUD API
- 配置验证（符合 OpenClaw schema）
- 配置版本管理
- 热重载通知（通知 OpenClaw 重新加载配置）
- 与 Agent 配置联动的自动更新

**验收口径**：
- [ ] 读取 openclaw.json 并解析为结构化对象
- [ ] 更新配置后写入文件并通知 OpenClaw
- [ ] 配置验证失败时拒绝更新
- [ ] Agent 变更时自动更新 agents.list[] 和 bindings
- [ ] 单元测试覆盖 CRUD 和联动流程

---

## REQ-0001-005: OpenClaw 凭证管理

**动机**：SOP Engine 统一管理 OpenClaw 的凭证（credentials/）

**凭证类型**：

| 凭证 | 路径 | 用途 |
|------|------|------|
| WhatsApp 凭证 | `credentials/whatsapp/` | WhatsApp 登录信息 |
| Telegram Bot Token | `credentials/telegram/` | Telegram Bot 凭证 |
| Discord Bot Token | `credentials/discord/` | Discord Bot 凭证 |
| Slack Token | `credentials/slack/` | Slack App 凭证 |
| Signal 凭证 | `credentials/signal/` | Signal 登录信息 |
| iMessage 凭证 | `credentials/imessage/` | iMessage 配置 |
| 配对允许列表 | `credentials/*-allowFrom.json` | DM 配对审批列表 |
| OAuth 导入 | `credentials/oauth.json` | OAuth 令牌 |
| 模型认证配置 | `agents/{agent_id}/agent/auth-profiles.json` | API Keys |

**范围**：
- 凭证 CRUD API
- 凭证加密存储（PostgreSQL + AES-256）
- 同步到 OpenClaw credentials 目录
- 凭证轮换提醒
- 敏感信息脱敏（日志/API 响应）

**安全要求**：
- 所有凭证加密存储
- API 响应中凭证值显示为 `***`
- 凭证变更审计日志
- 支持凭证测试验证

**验收口径**：
- [ ] 创建凭证时加密存储
- [ ] 同步凭证到 OpenClaw credentials 目录
- [ ] API 响应中凭证值脱敏
- [ ] 删除凭证时清理文件
- [ ] 单元测试覆盖 CRUD 和同步流程

---

## REQ-0001-006: YAML 模板解析器

**动机**：将 YAML 格式的流程定义解析为可执行的内部结构

**范围**：
- 解析 YAML 为 FlowTemplate 对象
- 验证节点类型合法性（start, end, agent, script, condition, parallel, loop, human, wait）
- 验证节点引用完整性（next 引用必须存在）
- 验证必须有 start 和 end 节点
- 参数定义解析

**非目标**：
- 不执行流程
- 不验证循环依赖（后续迭代）

**验收口径**：
- [ ] 合法 YAML 解析成功，返回 FlowTemplate
- [ ] 缺少 start 节点抛出 TemplateValidationError
- [ ] 缺少 end 节点抛出 TemplateValidationError
- [ ] 无效节点类型抛出 TemplateValidationError
- [ ] next 引用不存在抛出 TemplateValidationError
- [ ] 单元测试覆盖正常/异常/边界场景

---

## REQ-0001-007: EventBus 实现

**动机**：提供事件发布/订阅机制，支持异步流程执行

**范围**：
- 基于 Redis Streams 实现
- publish(stream, event) 方法
- consume(stream, group) 方法
- ack(stream, group, event_id) 方法
- 事件类型定义（node.started, node.completed, node.failed, execution.started, execution.completed）

**非目标**：
- 不包含消费者组管理（后续迭代）
- 不包含事件重放

**验收口径**：
- [ ] publish 后可通过 consume 读取
- [ ] ack 后事件标记为已处理
- [ ] 事件包含 execution_id, node_id, type, timestamp
- [ ] 单元测试覆盖发布/消费/确认流程

---

## REQ-0001-008: Context 上下文管理

**动机**：管理执行过程中的变量和状态

**范围**：
- ContextManager 服务
- get(execution_id) 获取完整上下文
- set(execution_id, key, value) 设置变量
- resolve_variables(execution_id, text) 解析模板变量 {var_name}
- Redis 存储

**非目标**：
- 不包含持久化到数据库
- 不包含上下文版本控制

**验收口径**：
- [ ] set 后 get 可读取
- [ ] resolve_variables 正确替换 {var_name}
- [ ] 变量不存在时抛出 ContextVariableError
- [ ] 单元测试覆盖变量存取和解析

---

## REQ-0001-009: FlowEngine 核心

**动机**：流程编排的核心引擎，控制节点执行和状态转换

**范围**：
- start_execution(template_id, params) 启动执行
- execute_node(execution, node) 执行单个节点
- transition(execution, result) 状态转换
- handle_failure(execution, error) 错误处理
- 与 EventBus、ContextManager 集成

**非目标**：
- 不包含具体节点执行器实现
- 不包含并行执行（后续迭代）

**验收口径**：
- [ ] start_execution 创建 Execution 记录并发布 execution.started 事件
- [ ] execute_node 更新 current_node 并发布 node.started/completed 事件
- [ ] transition 正确计算下一节点
- [ ] handle_failure 正确处理异常并更新状态
- [ ] 单元测试覆盖核心流程

---

## REQ-0001-010: BaseExecutor 抽象基类

**动机**：定义节点执行器的统一接口

**范围**：
- BaseExecutor 抽象类
- execute(node, context) -> NodeResult 抽象方法
- NodeResult 数据类（status, output, error）
- 执行器注册表（按节点类型查找执行器）

**非目标**：
- 不包含具体执行器实现

**验收口径**：
- [ ] BaseExecutor 无法直接实例化
- [ ] 子类必须实现 execute 方法
- [ ] 注册表可按类型获取执行器
- [ ] 单元测试覆盖注册和查找

---

## REQ-0001-011: Script 节点执行器

**动机**：执行 shell 命令作为流程节点

**范围**：
- ScriptExecutor 实现
- 解析命令中的模板变量
- 使用 subprocess 执行
- 捕获 stdout/stderr
- 超时控制

**非目标**：
- 不包含命令白名单（安全特性后续迭代）
- 不包含沙箱隔离

**验收口径**：
- [ ] 执行 `echo hello` 返回 "hello"
- [ ] 命令中的 {var} 被正确替换
- [ ] 超时命令抛出 NodeExecutionError
- [ ] 失败命令返回非零 exit code 和 stderr
- [ ] 单元测试覆盖正常/异常/边界场景

---

## REQ-0001-012: Agent 节点执行器

**动机**：调用 OpenClaw Agent 执行任务，执行前确保配置已同步

**配置同步流程**：
1. 从数据库加载 Agent 配置（AgentConfigFile 表）
2. 写入 OpenClaw workspace 目录：`{OPENCLAW_WORKSPACE_ROOT}/{agent_id}/`
3. 同步文件：AGENTS.md, SOUL.md, USER.md, IDENTITY.md, TOOLS.md, HEARTBEAT.md
4. 首次执行时创建 workspace 目录

**OpenClaw Agent 元数据**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string | Agent 唯一标识（如 `security-scanner`） |
| identity.name | string | 显示名称 |
| identity.theme | string | 主题/风格描述 |
| identity.emoji | string | 表情图标 |
| identity.avatar | string | 头像路径 |
| model.primary | string | 主模型 |
| model.fallbacks | string[] | 备选模型 |
| sandbox.mode | string | 沙箱模式（off/non-main/all） |
| tools.allow | string[] | 允许的工具 |
| tools.deny | string[] | 禁用的工具 |

**OpenClaw Webhook 规范**：
- 端点：`POST {OPENCLAW_URL}/hooks/agent`
- 认证：`Authorization: Bearer {token}` 或 `x-openclaw-token: {token}`

**请求格式**：
```json
{
  "message": "string (required) - 发送给 Agent 的提示词",
  "agentId": "string (optional) - 目标 Agent ID，如 'security-scanner'",
  "name": "string (optional) - Hook 名称，用于日志标识",
  "sessionKey": "string (optional) - 会话标识",
  "wakeMode": "now | next-heartbeat (optional, default: now)",
  "model": "string (optional) - 模型覆盖，如 'anthropic/claude-3-5-sonnet'",
  "thinking": "low | medium | high (optional) - 思考深度",
  "timeoutSeconds": "number (optional) - 超时秒数"
}
```

**响应**：
- `200` - 请求已接受（异步执行）
- `401` - 认证失败
- `400` - 无效请求
- `429` - 限流

**范围**：
- AgentExecutor 实现
- **配置同步**：执行前从数据库加载配置，写入 OpenClaw workspace
- 解析 message 中的模板变量 `{var_name}`
- POST 请求到 OpenClaw `/hooks/agent` 端点
- 支持 agentId、model、thinking、timeout 配置
- 超时和重试（3 次，指数退避：1s, 2s, 4s）
- 异步执行模式（不等待 Agent 完成，仅确认请求已接受）

**非目标**：
- 不同步等待 Agent 执行结果（OpenClaw 是异步的）
- 不包含消息回传（deliver/channel/to 配置）
- 不包含会话管理（sessionKey 由调用方管理）
- 不管理 OpenClaw 主配置（openclaw.json）

**验收口径**：
- [ ] 执行前检查并同步配置文件到 OpenClaw workspace
- [ ] 正确构造 `/hooks/agent` 请求
- [ ] Authorization header 正确设置
- [ ] message 中的 `{var}` 被正确替换
- [ ] 200 响应返回 success
- [ ] 401/400 抛出 NodeExecutionError
- [ ] 网络超时触发重试
- [ ] 单元测试覆盖成功/失败/重试场景

---

## REQ-0001-013: Condition 节点执行器

**动机**：根据条件选择执行分支

**范围**：
- ConditionExecutor 实现
- 条件表达式解析
- 返回匹配的分支 ID

**非目标**：
- 不包含复杂表达式（仅支持简单比较）
- 不包含嵌套条件

**验收口径**：
- [ ] 条件匹配时返回对应分支
- [ ] 无匹配时返回默认分支（如有）
- [ ] 无匹配且无默认分支时抛出错误
- [ ] 单元测试覆盖多分支场景

---

## REQ-0001-014: Human 审批节点执行器

**动机**：暂停流程等待人工审批

**范围**：
- HumanExecutor 实现
- 发布 human.approval_required 事件
- 暂停执行状态
- 提供恢复接口
- 超时处理

**非目标**：
- 不包含审批 UI
- 不包含多级审批

**验收口径**：
- [ ] 执行时状态变为 paused
- [ ] 发布 human.approval_required 事件
- [ ] 审批通过后继续执行
- [ ] 审批拒绝后走拒绝分支
- [ ] 超时后执行超时动作
- [ ] 单元测试覆盖通过/拒绝/超时

---

## REQ-0001-015: REST API - Agent 管理

**动机**：提供 Agent 配置的 CRUD 接口

**范围**：
- GET /api/agents - Agent 列表
- POST /api/agents - 创建 Agent
- GET /api/agents/{id} - Agent 详情
- PATCH /api/agents/{id} - 更新 Agent 元数据
- DELETE /api/agents/{id} - 删除 Agent
- GET /api/agents/{id}/files - 配置文件列表
- GET /api/agents/{id}/files/{file_type} - 获取配置文件内容
- PUT /api/agents/{id}/files/{file_type} - 更新配置文件
- POST /api/agents/{id}/sync - 手动同步到 OpenClaw

**非目标**：
- 不管理 OpenClaw 主配置
- 不管理 OpenClaw 凭证

**验收口径**：
- [ ] 创建 Agent 时生成默认配置文件
- [ ] 更新配置文件后自动同步到 OpenClaw
- [ ] 删除 Agent 时清理对应 workspace
- [ ] 集成测试覆盖 CRUD 和同步流程

---

## REQ-0001-016: REST API - 模板管理

**动机**：提供模板 CRUD 接口

**范围**：
- GET /api/templates - 模板列表（分页）
- POST /api/templates - 创建模板
- GET /api/templates/{id} - 模板详情
- POST /api/templates/upload - 上传 YAML
- DELETE /api/templates/{id} - 删除模板

**非目标**：
- 不包含模板版本管理
- 不包含模板权限控制

**验收口径**：
- [ ] 所有接口返回统一响应格式
- [ ] 分页参数正确工作
- [ ] YAML 上传触发解析验证
- [ ] 集成测试覆盖 CRUD 流程

---

## REQ-0001-017: REST API - 执行管理

**动机**：提供执行控制接口

**范围**：
- POST /api/executions - 启动执行
- GET /api/executions - 执行列表（分页、过滤）
- GET /api/executions/{id} - 执行详情
- POST /api/executions/{id}/cancel - 取消执行
- GET /api/executions/{id}/nodes - 节点执行列表

**非目标**：
- 不包含执行回滚
- 不包含执行重试（单独接口）

**验收口径**：
- [ ] 启动执行返回 execution_id
- [ ] 详情包含当前状态和节点列表
- [ ] 取消后状态变为 cancelled
- [ ] 集成测试覆盖执行生命周期

---

## REQ-0001-018: REST API - 审批管理

**动机**：提供审批操作接口

**范围**：
- GET /api/approvals/pending - 待审批列表
- POST /api/approvals/{exec_id}/{node_id} - 提交审批

**非目标**：
- 不包含审批历史查询
- 不包含批量审批

**验收口径**：
- [ ] 待审批列表正确返回 paused 状态的 human 节点
- [ ] 提交审批后流程继续执行
- [ ] 集成测试覆盖审批流程

---

## REQ-0001-019: WebSocket 实时推送

**动机**：实时推送执行状态变化

**范围**：
- WS /ws - WebSocket 端点
- 订阅 execution_id
- 推送 node.started, node.completed, execution.completed 等事件

**非目标**：
- 不包含房间管理
- 不包含认证（后续迭代）

**验收口径**：
- [ ] 连接成功返回连接确认
- [ ] 订阅后收到相关事件
- [ ] 事件格式符合规范
- [ ] E2E 测试覆盖实时推送

---

## REQ-0001-020: 前端 - 项目骨架

**动机**：建立可运行的前端项目

**范围**：
- Next.js 14 App Router 配置
- shadcn/ui 初始化
- TailwindCSS 配置
- 基础布局组件
- API 客户端封装

**非目标**：
- 不包含具体页面实现
- 不包含状态管理

**验收口径**：
- [ ] `pnpm dev` 启动成功
- [ ] 访问根路由返回页面
- [ ] 基础组件可渲染
- [ ] API 客户端可调用后端

---

## REQ-0001-021: 前端 - 模板列表页

**动机**：展示和管理流程模板

**范围**：
- 模板列表展示（表格）
- 创建模板对话框
- YAML 上传功能
- 模板详情查看
- 删除确认

**非目标**：
- 不包含模板编辑器
- 不包含模板版本管理

**验收口径**：
- [ ] 列表正确展示模板数据
- [ ] 创建模板成功后列表刷新
- [ ] YAML 上传触发验证
- [ ] E2E 测试覆盖 CRUD 流程

---

## REQ-0001-022: 前端 - 执行监控页

**动机**：实时监控流程执行状态

**范围**：
- 执行列表展示
- 执行详情页
- 节点执行状态展示
- WebSocket 实时更新
- 启动/取消执行操作

**非目标**：
- 不包含执行日志详情
- 不包含执行重试

**验收口径**：
- [ ] 列表正确展示执行数据
- [ ] 详情页展示节点执行状态
- [ ] 实时更新生效
- [ ] E2E 测试覆盖监控流程

---

## REQ-0001-023: 前端 - 审批工作台

**动机**：提供审批操作界面

**范围**：
- 待审批列表
- 审批操作（通过/拒绝）
- 审批备注
- 操作结果反馈

**非目标**：
- 不包含审批历史
- 不包含批量审批

**验收口径**：
- [ ] 列表正确展示待审批数据
- [ ] 通过/拒绝操作成功
- [ ] 操作后列表刷新
- [ ] E2E 测试覆盖审批流程

---

## REQ-0001-024: 前端 - 流程编辑器

**动机**：可视化编辑流程模板

**范围**：
- React Flow 集成
- 节点拖拽
- 节点连线
- 节点配置面板
- YAML 导出

**非目标**：
- 不包含 YAML 导入转流程图
- 不包含流程验证

**验收口径**：
- [ ] 可拖拽添加节点
- [ ] 可连接节点
- [ ] 可配置节点属性
- [ ] 可导出为 YAML
- [ ] E2E 测试覆盖编辑流程

---

## REQ-0001-025: 前端 - Agent 管理页

**动机**：管理 Agent 配置和人设文件

**范围**：
- Agent 列表展示
- 创建 Agent 对话框
- Agent 详情页
- 配置文件编辑器（AGENTS.md, SOUL.md, USER.md, IDENTITY.md）
- 同步状态展示
- 手动同步按钮

**非目标**：
- 不编辑 OpenClaw 主配置
- 不管理 OpenClaw 凭证

**验收口径**：
- [ ] 列表正确展示 Agent 数据
- [ ] 创建 Agent 成功后列表刷新
- [ ] 配置文件编辑器可用
- [ ] 同步状态正确展示
- [ ] E2E 测试覆盖管理流程

---

## REQ-0001-026: Channel 配置完整对齐

**动机**：与 OpenClaw 官方配置规范完全对齐，支持所有 Channel 类型的完整字段

**范围**：
- 同步逻辑修复：采用 merge 策略，保留非管理字段
- 多账号支持：`accounts` 和 `default_account` 结构
- Telegram 完整字段：reaction_notifications, history_limit, webhook, network, proxy 等
- Feishu 完整字段：domain, connection_mode, webhook_path, typing_indicator 等
- WhatsApp 完整字段：ack_reaction, send_read_receipts, chunk_mode 等
- 通用字段：streaming, text_chunk_limit, media_max_mb, config_writes

**非目标**：
- 不支持 Discord/Slack（后续迭代）
- 不实现高级网络配置的 UI

**验收口径**：
- [ ] Channel 同步后非管理字段保留
- [ ] 多账号结构正确写入 openclaw.json
- [ ] 所有 Channel 类型完整字段可配置
- [ ] 单元测试覆盖率 ≥80%
- [ ] E2E 测试覆盖同步流程

---

## REQ-0001-027: Agent 配置完整对齐

**动机**：与 OpenClaw 官方配置规范完全对齐，支持 Agent 完整配置

**范围**：
- Session 配置：dm_scope, reset, maintenance, thread_bindings, send_policy
- Messages 配置：queue modes, inbound debounce, TTS
- Commands 配置：native, text, bash, permissions
- Compaction 配置：mode, reserveTokensFloor, memoryFlush
- 模型配置增强：models catalog, image_model, pdf_model
- 沙箱配置增强：docker 后端完整配置

**非目标**：
- 不支持 SSH/openshell 后端（后续迭代）
- 不实现 TTS 的 UI 配置

**验收口径**：
- [ ] Session 配置正确同步到 openclaw.json
- [ ] Messages/Commands 配置完整支持
- [ ] 模型目录配置可用
- [ ] 单元测试覆盖率 ≥80%
- [ ] 配置变更后 Agent 运行正常

---

## REQ-0001-028: Bindings 配置支持

**动机**：支持多 Agent 路由，实现灵活的消息分发

**范围**：
- Binding 模型：type (route/acp), agent_id, match
- BindingMatch 规则：channel, account_id, peer, guild_id, team_id
- 优先级顺序：peer > guildId > teamId > accountId > default
- ACP 绑定配置：mode, label, cwd, backend

**非目标**：
- 不支持 ACP 后端的完整 UI
- 不实现动态绑定热更新

**验收口径**：
- [ ] Binding CRUD API 可用
- [ ] 绑定规则正确写入 openclaw.json
- [ ] 优先级匹配逻辑正确
- [ ] 单元测试覆盖所有匹配场景
- [ ] E2E 测试覆盖路由流程

---

## REQ-0001-029: 前端适配 - 高级配置

**动机**：前端 UI 支持完整配置字段的编辑

**范围**：
- Channel 高级配置 Tab：完整字段编辑
- Agent 高级配置 Tab：Session/Messages/Commands 配置
- 多账号管理 UI：账号列表、切换、配置
- 配置预设：常用配置快速应用
- JSON 编辑器：高级用户直接编辑 JSON

**非目标**：
- 不实现所有高级字段的 UI（部分通过 JSON 编辑器）
- 不实现配置版本对比 UI

**验收口径**：
- [ ] Channel 高级配置 Tab 可用
- [ ] Agent 高级配置 Tab 可用
- [ ] JSON 编辑器可用且验证通过
- [ ] 配置预设可一键应用
- [ ] E2E 测试覆盖配置流程

---

## REQ-0001-030: E2E 测试完善

**动机**：确保完整用户流程可自动化验证

**范围**：
- Channel 配置流程 E2E：创建 → 配置 → 同步 → 验证
- Agent 配置流程 E2E：创建 → 高级配置 → 同步 → 验证
- Bindings 流程 E2E：创建 → 配置 → 路由验证
- 回归测试：v1 功能不受影响

**非目标**：
- 不覆盖所有边界场景（单元测试覆盖）
- 不实现性能测试

**验收口径**：
- [ ] 所有 E2E 测试通过
- [ ] 覆盖核心用户流程
- [ ] 测试可重复运行
- [ ] CI 集成成功
