# v1-m14: 执行监控页

## Goal

监控和管理流程执行状态。

## PRD Trace

- REQ-0001-022: 前端 - 执行监控页

## Scope

**做**：
- 执行列表展示（表格）
- 执行状态实时更新（WebSocket）
- 执行详情查看
- 取消执行功能
- 节点执行状态展示

**不做**：
- 执行历史分析
- 性能报表

## Acceptance

| # | 验收标准 |
|---|----------|
| 1 | 列表正确展示执行数据 |
| 2 | WebSocket 推送更新状态 |
| 3 | 取消执行后状态正确更新 |
| 4 | 节点执行详情正确展示 |

## Files

```
frontend/
├── app/executions/
│   └── page.tsx
└── components/executions/
    ├── execution-list.tsx
    └── execution-detail-dialog.tsx
```
