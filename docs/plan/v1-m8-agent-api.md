# v1-m8: Agent REST API

## Goal

实现 Agent 管理的 REST API 端点，提供 CRUD 接口。

## PRD Trace

- REQ-0001-015: REST API - Agent 管理

## Scope

**做**：
- GET /api/agents - Agent 列表
- POST /api/agents - 创建 Agent
- GET /api/agents/{id} - Agent 详情
- PATCH /api/agents/{id} - 更新 Agent 元数据
- DELETE /api/agents/{id} - 删除 Agent
- GET /api/agents/{id}/files - 配置文件列表
- GET /api/agents/{id}/files/{file_type} - 获取配置文件内容
- PUT /api/agents/{id}/files/{file_type} - 更新配置文件
- POST /api/agents/{id}/sync - 手动同步到 OpenClaw
- 单元测试

**不做**：
- OpenClaw 主配置管理
- OpenClaw 凭证管理
- 数据库持久化（使用内存存储）

## Acceptance

| # | 验收标准 | 验证命令 |
|---|----------|----------|
| 1 | GET /api/agents 返回 Agent 列表 | `pytest tests/unit/test_agent_api.py::test_list_agents -v` |
| 2 | POST /api/agents 创建 Agent | `pytest tests/unit/test_agent_api.py::test_create_agent -v` |
| 3 | GET /api/agents/{id} 返回详情 | `pytest tests/unit/test_agent_api.py::test_get_agent -v` |
| 4 | PATCH /api/agents/{id} 更新 Agent | `pytest tests/unit/test_agent_api.py::test_update_agent -v` |
| 5 | DELETE /api/agents/{id} 删除 Agent | `pytest tests/unit/test_agent_api.py::test_delete_agent -v` |
| 6 | 配置文件 CRUD 可用 | `pytest tests/unit/test_agent_api.py::test_config_files -v` |

## Files

```
backend/
├── app/api/
│   ├── __init__.py
│   └── agents.py
└── tests/
    └── unit/
        └── test_agent_api.py
```

## Steps

### Step 1: 写测试 (TDD Red)
### Step 2: 实现 API (TDD Green)
### Step 3: 代码质量检查

## Risks

| 风险 | 缓解措施 |
|------|----------|
| API 响应格式不一致 | 使用统一的响应模型 |

## DoD 自检

- [x] 每条验收标准可二元判定
- [x] 每条验收绑定验证命令
- [x] Scope 明确不做什么
- [x] 测试覆盖正常/异常/边界场景
