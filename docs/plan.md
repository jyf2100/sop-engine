# SOP 编排引擎 - 实现计划

## 概述

基于 OpenClaw 构建的 SOP（标准作业流程）编排系统。每个节点是一个 Agent，支持：
- **数据流转**: 消息队列（Redis Streams）
- **模板格式**: YAML
- **高级特性**: 条件分支、并行执行、循环/重试、人工审批

**项目位置**: `~/workspace/sop-engine`

## 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      OpenClaw Flow                               │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐     ┌──────────────┐     ┌────────────────┐  │
│  │   Template   │     │    Engine    │────>│  Node Executors│  │
│  │    Parser    │────>│     Core     │     │ Agent/Script/  │  │
│  │   (YAML)     │     │              │     │ Human/Wait     │  │
│  └──────────────┘     └──────┬───────┘     └────────────────┘  │
│                              ▼                     │            │
│                    ┌─────────────────┐            │            │
│                    │  EventBus       │◄───────────┘            │
│                    │  (Redis Streams)│                         │
│                    └────────┬────────┘                         │
│              ┌──────────────┼──────────────┐                  │
│              ▼              ▼              ▼                  │
│        ┌──────────┐  ┌──────────┐  ┌──────────────┐          │
│        │  Flow    │  │ Instance │  │   Context    │          │
│        │ Template │  │ Execution│  │   (Redis)    │          │
│        │(PostgreSQL)│  │(PostgreSQL)│  │              │          │
│        └──────────┘  └──────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   OpenClaw      │
                    │   (Webhook)     │
                    └─────────────────┘
```

## 项目结构

```
~/workspace/sop-engine/
├── README.md
├── pyproject.toml
├── config/
│   └── settings.yaml
├── flow/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── template.py
│   │   ├── execution.py
│   │   └── node.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── event_bus.py
│   │   ├── template_parser.py
│   │   ├── engine.py
│   │   ├── context.py
│   │   └── openclaw.py
│   ├── executors/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── agent.py
│   │   ├── script.py
│   │   ├── condition.py
│   │   ├── parallel.py
│   │   ├── loop.py
│   │   ├── human.py
│   │   └── wait.py
│   ├── workers/
│   │   ├── __init__.py
│   │   └── flow_worker.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── templates.py
│   │   ├── executions.py
│   │   ├── approvals.py
│   │   └── websocket.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── templates/
│   └── example.yaml
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_parser.py
    └── test_engine.py
```

## 节点类型

| 类型 | 说明 | 输出 |
|------|------|------|
| start | 开始节点 | - |
| end | 结束节点 | - |
| agent | 调用 OpenClaw Agent | agent 执行结果 |
| script | 执行脚本/命令 | 命令输出 |
| condition | 条件分支 | 匹配的分支 |
| parallel | 并行执行 | 所有分支结果 |
| loop | 循环执行 | 每次迭代结果 |
| human | 人工审批 | 审批决策 |
| wait | 等待/定时 | - |

## YAML 模板示例

```yaml
# templates/code-review.yaml
id: code-review-flow
name: 代码审查流程
version: "1.0.0"

parameters:
  repo_url:
    type: string
    required: true
  branch:
    type: string
    default: main

nodes:
  start:
    type: start
    next: fetch_code

  fetch_code:
    type: script
    command: "git clone {repo_url} -b {branch} /tmp/repo"
    output_var: clone_result
    next: parallel_analysis

  parallel_analysis:
    type: parallel
    branches:
      - id: security
        next: security_check
      - id: performance
        next: perf_check
    join: aggregate

  security_check:
    type: agent
    agentId: security-scanner      # OpenClaw agent ID（对应 agents.list[].id）
    message: "扫描 /tmp/repo 的安全漏洞"
    model: "anthropic/claude-3-5-sonnet"  # 可选：覆盖模型
    thinking: high                 # 可选：思考深度 (low/medium/high)
    timeoutSeconds: 120            # 可选：超时秒数
    output_var: security_report

  perf_check:
    type: agent
    agentId: performance-analyzer  # OpenClaw agent ID
    message: "分析 /tmp/repo 的性能问题"
    output_var: perf_report

  aggregate:
    type: agent
    agentId: main                  # OpenClaw agent ID
    message: |
      汇总审查结果：
      - 安全: {security_report}
      - 性能: {perf_report}
    output_var: final_report
    next: human_review

  human_review:
    type: human
    approvers: [tech_lead]
    timeout_hours: 24
    actions:
      approve: cleanup
      reject: notify_author

  cleanup:
    type: script
    command: "rm -rf /tmp/repo"
    next: end

  notify_author:
    type: agent
    agentId: notification-bot     # OpenClaw agent ID
    message: "通知作者审查未通过"
    next: end

  end:
    type: end

# OpenClaw Agent 元数据说明
# agentId 对应 OpenClaw 配置中的 agents.list[].id
# Agent 身份信息在 OpenClaw 侧配置：
# - identity.name: 显示名称
# - identity.theme: 主题/风格
# - identity.emoji: 表情图标
# - identity.avatar: 头像
# - model.primary: 主模型
# - sandbox.mode: 沙箱模式
# - tools.allow/deny: 工具权限
```

## API 设计

### 模板管理
- `GET /api/templates` - 模板列表
- `POST /api/templates` - 创建模板
- `GET /api/templates/{id}` - 模板详情
- `POST /api/templates/upload` - 上传 YAML

### 执行管理
- `POST /api/executions` - 启动执行
- `GET /api/executions` - 执行列表
- `GET /api/executions/{id}` - 执行详情
- `POST /api/executions/{id}/cancel` - 取消执行

### 审批管理
- `GET /api/approvals/pending` - 待审批列表
- `POST /api/approvals/{exec_id}/{node_id}` - 提交审批

### WebSocket
- `WS /ws` - 实时事件推送

## 技术栈

| 组件 | 技术 |
|------|------|
| Web 框架 | FastAPI |
| 数据库 | PostgreSQL |
| ORM | SQLAlchemy 2.0 |
| 消息队列 | Redis Streams |
| YAML 解析 | PyYAML |

---

## 实现步骤

### Phase 1: 项目骨架 (0.5天)

#### 1.1 目录结构
```
~/workspace/sop-engine/
├── pyproject.toml
├── config/
│   └── settings.yaml
├── flow/
│   ├── __init__.py
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置加载
│   ├── models/
│   ├── services/
│   ├── executors/
│   ├── workers/
│   ├── api/
│   └── utils/
├── templates/
└── tests/
```

#### 1.2 pyproject.toml
- Python 3.11+
- FastAPI, SQLAlchemy 2.0, PyYAML, redis, pydantic, uvicorn

#### 1.3 配置文件
- Redis 连接
- PostgreSQL 连接
- OpenClaw webhook URL

---

### Phase 2: 核心模型 (0.5天)

#### 2.1 Template 模型
```python
# flow/models/template.py
class FlowTemplate:
    id: str
    name: str
    version: str
    parameters: dict          # 输入参数定义
    nodes: dict[str, Node]    # 节点定义
    created_at: datetime
```

#### 2.2 Execution 模型
```python
# flow/models/execution.py
class Execution:
    id: UUID
    template_id: str
    status: Enum              # pending/running/paused/completed/failed
    context: dict             # 执行上下文 (变量)
    current_node: str
    started_at: datetime
    completed_at: datetime
```

#### 2.3 Node 模型
```python
# flow/models/node.py
class Node:
    id: str
    type: Enum                # start/end/agent/script/condition/parallel/loop/human/wait
    config: dict              # 节点配置
    next: str | dict          # 下一节点或分支
    output_var: str           # 输出变量名
```

---

### Phase 3: EventBus & Context (1天)

#### 3.1 EventBus (Redis Streams)
```python
# flow/services/event_bus.py
class EventBus:
    def publish(stream: str, event: dict)
    def consume(stream: str, group: str) -> Event
    def ack(stream: str, group: str, event_id: str)

# 事件类型
- node.started
- node.completed
- node.failed
- execution.started
- execution.completed
- human.approval_required
```

#### 3.2 Context 服务
```python
# flow/services/context.py
class ContextManager:
    def get(execution_id: UUID) -> dict
    def set(execution_id: UUID, key: str, value: Any)
    def resolve_variables(execution_id: UUID, text: str) -> str
```

---

### Phase 4: Template Parser (0.5天)

#### 4.1 YAML 解析器
```python
# flow/services/template_parser.py
class TemplateParser:
    def parse(yaml_content: str) -> FlowTemplate
    def validate(template: FlowTemplate) -> list[ValidationError]
```

#### 4.2 验证规则
- 必须有 start 和 end 节点
- next 引用必须存在
- 参数类型校验
- 循环依赖检测

---

### Phase 5: Flow Engine (1天)

#### 5.1 引擎核心
```python
# flow/services/engine.py
class FlowEngine:
    async def start_execution(template_id: str, params: dict) -> Execution
    async def execute_node(execution: Execution, node: Node) -> NodeResult
    async def transition(execution: Execution, result: NodeResult)
    async def handle_failure(execution: Execution, error: Exception)
```

#### 5.2 执行流程
```
start_execution()
  → 解析模板 + 验证参数
  → 创建 Execution 记录
  → 发布 execution.started 事件
  → 从 start 节点开始执行

execute_node()
  → 更新 current_node
  → 发布 node.started
  → 调用对应 Executor
  → 保存输出到 context
  → 发布 node.completed
  → 计算下一节点

transition()
  → 有 next 则继续执行
  → 无 next 则结束
```

---

### Phase 6: 节点执行器 (2天)

#### 6.1 Base Executor
```python
# flow/executors/base.py
class BaseExecutor(ABC):
    @abstractmethod
    async def execute(node: Node, context: dict) -> NodeResult
```

#### 6.2 Agent Executor
```python
# flow/executors/agent.py
class AgentExecutor(BaseExecutor):
    """调用 OpenClaw Agent"""
    async def execute(node, context):
        # 解析 message 中的变量
        # POST 到 OpenClaw webhook
        # 返回执行结果
```

#### 6.3 Script Executor
```python
# flow/executors/script.py
class ScriptExecutor(BaseExecutor):
    """执行 shell 命令"""
    async def execute(node, context):
        # 解析 command 中的变量
        # subprocess 执行
        # 返回 stdout/stderr
```

#### 6.4 Condition Executor
```python
# flow/executors/condition.py
class ConditionExecutor(BaseExecutor):
    """条件分支"""
    async def execute(node, context):
        # 评估 conditions
        # 返回匹配的分支 ID
```

#### 6.5 Parallel Executor
```python
# flow/executors/parallel.py
class ParallelExecutor(BaseExecutor):
    """并行执行"""
    async def execute(node, context):
        # asyncio.gather 所有分支
        # 汇总结果到 join 节点
```

#### 6.6 Loop Executor
```python
# flow/executors/loop.py
class LoopExecutor(BaseExecutor):
    """循环执行"""
    async def execute(node, context):
        # 遍历 items
        # 每次迭代执行子节点
        # 支持 max_retries
```

#### 6.7 Human Executor
```python
# flow/executors/human.py
class HumanExecutor(BaseExecutor):
    """人工审批"""
    async def execute(node, context):
        # 发布 human.approval_required 事件
        # 暂停执行，等待审批
        # 返回审批结果
```

#### 6.8 Wait Executor
```python
# flow/executors/wait.py
class WaitExecutor(BaseExecutor):
    """等待/定时"""
    async def execute(node, context):
        # 支持 duration / until
        # asyncio.sleep
```

---

### Phase 7: REST API (1天)

#### 7.1 模板 API
```
GET    /api/templates           # 列表
POST   /api/templates           # 创建
GET    /api/templates/{id}      # 详情
POST   /api/templates/upload    # 上传 YAML
DELETE /api/templates/{id}      # 删除
```

#### 7.2 执行 API
```
POST   /api/executions                     # 启动执行
GET    /api/executions                     # 列表 (支持过滤)
GET    /api/executions/{id}                # 详情
POST   /api/executions/{id}/cancel         # 取消
GET    /api/executions/{id}/nodes/{node}   # 节点详情
```

#### 7.3 审批 API
```
GET    /api/approvals/pending              # 待审批列表
POST   /api/approvals/{exec_id}/{node_id}  # 提交审批
```

#### 7.4 WebSocket
```
WS /ws
# 事件推送
- execution.started
- execution.completed
- node.started
- node.completed
- human.approval_required
```

---

### Phase 8: Flow Worker (0.5天)

#### 8.1 Worker 实现
```python
# flow/workers/flow_worker.py
class FlowWorker:
    def run():
        # 消费 Redis Streams 事件
        # 调用 FlowEngine 处理

    async def handle_event(event):
        match event.type:
            case "node.completed": transition()
            case "human.approval_submitted": resume_execution()
```

---

### Phase 9: 测试 & 文档 (1天)

#### 9.1 单元测试
- `test_parser.py` - 模板解析测试
- `test_engine.py` - 引擎逻辑测试
- `test_executors.py` - 各执行器测试

#### 9.2 集成测试
- 端到端流程测试
- Redis 连接测试
- OpenClaw 集成测试

#### 9.3 示例模板
- `templates/hello-world.yaml` - 简单流程
- `templates/code-review.yaml` - 复杂流程 (并行+审批)
- `templates/deployment.yaml` - 条件+回滚

---

## 依赖清单

```toml
[project]
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn>=0.27.0",
    "sqlalchemy>=2.0.0",
    "pydantic>=2.5.0",
    "pyyaml>=6.0",
    "redis>=5.0.0",
    "httpx>=0.26.0",
    "python-multipart>=0.0.6",
]
```

---

## 时间估算

| Phase | 任务 | 估时 |
|-------|------|------|
| 1 | 项目骨架 | 0.5天 |
| 2 | 核心模型 | 0.5天 |
| 3 | EventBus & Context | 1天 |
| 4 | Template Parser | 0.5天 |
| 5 | Flow Engine | 1天 |
| 6 | 节点执行器 | 2天 |
| 7 | REST API | 1天 |
| 8 | Flow Worker | 0.5天 |
| 9 | 测试 & 文档 | 1天 |
| **总计** | | **8天** |
