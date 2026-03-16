# v1-m7: 审批执行器

## Goal

实现 Human 审批节点执行器，支持流程暂停和人工审批。

## PRD Trace

- REQ-0001-014: Human 审批节点执行器

## Scope

**做**：
- HumanExecutor: 审批节点执行
- 审批状态管理
- 超时处理
- 恢复接口
- 单元测试

**不做**：
- 审批 UI
- 多级审批
- 审批历史持久化

## Acceptance

| # | 验收标准 | 验证命令 |
|---|----------|----------|
| 1 | 执行时状态变为 paused | `pytest tests/unit/test_human_executor.py::test_pause_on_approval -v` |
| 2 | 发布 human.approval_required 事件 | `pytest tests/unit/test_human_executor.py::test_approval_event -v` |
| 3 | 审批通过后继续执行 | `pytest tests/unit/test_human_executor.py::test_approve -v` |
| 4 | 审批拒绝后走拒绝分支 | `pytest tests/unit/test_human_executor.py::test_reject -v` |
| 5 | 超时后执行超时动作 | `pytest tests/unit/test_human_executor.py::test_timeout -v` |

## Files

```
backend/
├── app/executors/
│   └── human_executor.py
├── app/services/
│   └── approval_service.py
└── tests/
    └── unit/
        └── test_human_executor.py
```

## Steps

### Step 1: 创建 ApprovalService (TDD)
### Step 2: 实现 HumanExecutor (TDD)
### Step 3: 代码质量检查

## Risks

| 风险 | 缓解措施 |
|------|----------|
| 审批状态丢失 | 使用持久化存储 |
| 超时处理不当 | 明确超时策略 |

## DoD 自检

- [x] 每条验收标准可二元判定
- [x] 每条验收绑定验证命令
- [x] Scope 明确不做什么
- [x] 测试覆盖正常/异常/边界场景
