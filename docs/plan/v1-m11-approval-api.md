# v1-m11: Approval REST API + WebSocket

## Goal

实现审批管理 API 和 WebSocket 实时推送。

## PRD Trace

- REQ-0001-018: REST API - 审批管理
- REQ-0001-019: WebSocket 实时推送

## Scope

**做**：
- GET /api/approvals/pending - 待审批列表
- POST /api/approvals/{exec_id}/{node_id} - 提交审批
- WS /ws - WebSocket 端点
- 单元测试

**不做**：
- 审批历史查询
- 批量审批
- 房间管理
- 认证

## Acceptance

| # | 验收标准 | 验证命令 |
|---|----------|----------|
| 1 | 待审批列表正确返回 | `pytest tests/unit/test_approval_api.py::test_list_pending -v` |
| 2 | 提交审批后流程继续 | `pytest tests/unit/test_approval_api.py::test_submit_approval -v` |
| 3 | WebSocket 连接可建立 | `pytest tests/unit/test_approval_api.py::test_websocket -v` |

## Files

```
backend/
├── app/api/
│   └── approvals.py
└── tests/
    └── unit/
        └── test_approval_api.py
```

## Steps

### Step 1: 写测试 (TDD Red)
### Step 2: 实现 API (TDD Green)
### Step 3: 代码质量检查

## Risks

| 风险 | 缓解措施 |
|------|----------|
| WebSocket 测试复杂 | 使用 FastAPI TestClient 的 WebSocket 支持 |

## DoD 自检

- [x] 每条验收标准可二元判定
- [x] 每条验收绑定验证命令
- [x] Scope 明确不做什么
- [x] 测试覆盖正常/异常/边界场景
