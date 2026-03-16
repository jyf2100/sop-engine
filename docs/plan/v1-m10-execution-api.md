# v1-m10: Execution REST API

## Goal

实现执行管理的 REST API 端点，提供执行控制接口。

## PRD Trace

- REQ-0001-017: REST API - 执行管理

## Scope

**做**：
- POST /api/executions - 启动执行
- GET /api/executions - 执行列表（分页、过滤）
- GET /api/executions/{id} - 执行详情
- POST /api/executions/{id}/cancel - 取消执行
- GET /api/executions/{id}/nodes - 节点执行列表
- 单元测试

**不做**：
- 执行回滚
- 执行重试（单独接口）
- 数据库持久化（使用内存存储）

## Acceptance

| # | 验收标准 | 验证命令 |
|---|----------|----------|
| 1 | POST /api/executions 返回 execution_id | `pytest tests/unit/test_execution_api.py::test_start_execution -v` |
| 2 | GET /api/executions 返回分页列表 | `pytest tests/unit/test_execution_api.py::test_list_executions -v` |
| 3 | GET /api/executions/{id} 返回详情 | `pytest tests/unit/test_execution_api.py::test_get_execution -v` |
| 4 | POST /api/executions/{id}/cancel 取消执行 | `pytest tests/unit/test_execution_api.py::test_cancel_execution -v` |
| 5 | GET /api/executions/{id}/nodes 返回节点列表 | `pytest tests/unit/test_execution_api.py::test_list_nodes -v` |

## Files

```
backend/
├── app/api/
│   └── executions.py
├── app/services/
│   └── execution_service.py
└── tests/
    └── unit/
        └── test_execution_api.py
```

## Steps

### Step 1: 写测试 (TDD Red)
### Step 2: 实现 Service 和 API (TDD Green)
### Step 3: 代码质量检查

## Risks

| 风险 | 缓解措施 |
|------|----------|
| 执行状态转换复杂 | 使用明确的枚举状态 |

## DoD 自检

- [x] 每条验收标准可二元判定
- [x] 每条验收绑定验证命令
- [x] Scope 明确不做什么
- [x] 测试覆盖正常/异常/边界场景
