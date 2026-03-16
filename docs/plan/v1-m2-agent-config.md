# v1-m2: Agent 配置管理

## Goal

实现 Agent 配置的完整生命周期管理，包括 CRUD、配置文件管理、与 OpenClaw 的同步机制。SOP Engine 作为 OpenClaw Agent 配置的唯一来源（Source of Truth）。

## PRD Trace

- REQ-0001-003: Agent 配置管理

## Scope

**做**：
- Agent CRUD Service 层实现
- AgentConfigFile 管理（AGENTS.md, SOUL.md, USER.md, IDENTITY.md 等）
- 同步到 OpenClaw workspace 目录
- 更新 openclaw.json 的 agents.list[] 和 bindings
- 默认配置文件模板生成
- 单元测试 + 集成测试

**不做**：
- REST API 端点（M8: REQ-0001-015）
- 前端页面（M17: REQ-0001-025）
- OpenClaw webhook 调用（M6: REQ-0001-012）
- 数据库迁移脚本

## Acceptance

| # | 验收标准 | 验证命令 |
|---|----------|----------|
| 1 | 创建 Agent 时生成默认配置文件 | `pytest tests/unit/test_agent_service.py::test_create_agent_generates_default_files -v` |
| 2 | 更新配置文件后同步到 workspace | `pytest tests/integration/test_agent_sync.py::test_sync_config_files_to_workspace -v` |
| 3 | 删除 Agent 时清理 workspace 和 openclaw.json | `pytest tests/integration/test_agent_sync.py::test_delete_agent_cleans_up -v` |
| 4 | Agent 元数据可完整存储 | `pytest tests/unit/test_agent_service.py::test_agent_metadata_storage -v` |
| 5 | 覆盖率 ≥ 90% | `pytest --cov=app/services --cov-fail-under=90` |

## Files

```
backend/
├── app/
│   ├── services/
│   │   ├── __init__.py
│   │   ├── agent_service.py      # Agent CRUD 逻辑
│   │   └── openclaw_sync.py      # 同步到 OpenClaw
│   ├── templates/
│   │   └── agent_defaults/       # 默认配置文件模板
│   │       ├── AGENTS.md.jinja
│   │       ├── SOUL.md.jinja
│   │       ├── USER.md.jinja
│   │       └── IDENTITY.md.jinja
│   └── models/
│       └── (已存在)
└── tests/
    ├── unit/
    │   └── test_agent_service.py
    └── integration/
        └── test_agent_sync.py
```

## Steps

### Step 1: 创建目录结构

```bash
mkdir -p backend/app/services backend/app/templates/agent_defaults backend/tests/integration
```

### Step 2: 创建默认配置文件模板

AGENTS.md, SOUL.md, USER.md, IDENTITY.md 的 Jinja2 模板。

### Step 3: 实现 AgentService (TDD Red)

写失败测试：创建 Agent、更新、删除、生成默认文件。

### Step 4: 实现 AgentService (TDD Green)

实现服务逻辑，使用文件系统操作。

### Step 5: 实现 OpenClawSync (TDD Red)

写失败测试：同步到 workspace、更新 openclaw.json。

### Step 6: 实现 OpenClawSync (TDD Green)

实现同步逻辑，处理文件写入和 JSON 更新。

### Step 7: 集成测试

测试完整流程：创建 → 同步 → 验证文件 → 删除 → 验证清理。

### Step 8: 代码质量检查

```bash
ruff check app/ tests/
pytest --cov=app/services --cov-fail-under=90
```

## Risks

| 风险 | 缓解措施 |
|------|----------|
| 文件系统权限问题 | 使用 os.makedirs(exist_ok=True)，捕获 PermissionError |
| openclaw.json 并发写入 | 使用文件锁或原子写入 |
| workspace 路径不存在 | 自动创建，记录警告日志 |

## DoD 自检

- [x] 每条验收标准可二元判定
- [x] 每条验收绑定验证命令
- [x] Scope 明确不做什么
- [x] 测试覆盖正常/异常/边界场景
