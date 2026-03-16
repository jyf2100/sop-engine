# v1-m17: Agent 管理页

## Goal

管理 OpenClaw Agent 配置。

## PRD Trace

- REQ-0001-025: 前端 - Agent 管理页

## Scope

**做**：
- Agent 列表展示
- Agent 创建/编辑/删除
- Agent 配置文件查看
- Agent 同步触发

**不做**：
- Agent 配置文件编辑
- Agent 测试运行

## Acceptance

| # | 验收标准 |
|---|----------|
| 1 | 列表正确展示 Agent 数据 |
| 2 | 创建 Agent 成功后列表刷新 |
| 3 | 删除确认后刷新列表 |
| 4 | 同步操作正确触发 |

## Files

```
frontend/
├── app/agents/
│   └── page.tsx
└── components/agents/
    ├── agent-list.tsx
    ├── create-agent-dialog.tsx
    └── agent-detail-dialog.tsx
```
