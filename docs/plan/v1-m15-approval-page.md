# v1-m15: 审批工作台

## Goal

处理待审批任务。

## PRD Trace

- REQ-0001-023: 前端 - 审批工作台

## Scope

**做**：
- 待审批列表展示
- 审批详情查看
- 批准/拒绝操作
- 实时待审批推送（WebSocket）

**不做**：
- 审批历史查询
- 审批统计报表

## Acceptance

| # | 验收标准 |
|---|----------|
| 1 | 待审批列表正确展示 |
| 2 | 批准后状态正确更新 |
| 3 | 拒绝后状态正确更新 |
| 4 | WebSocket 推送新待审批 |

## Files

```
frontend/
├── app/approvals/
│   └── page.tsx
└── components/approvals/
    ├── approval-list.tsx
    └── approval-dialog.tsx
```
