# v1-m13: 模板管理页

## Goal

展示和管理流程模板。

## PRD Trace

- REQ-0001-021: 前端 - 模板列表页

## Scope

**做**：
- 模板列表展示（表格）
- 创建模板对话框
- YAML 上传功能
- 模板详情查看
- 删除确认

**不做**：
- 模板编辑器
- 模板版本管理

## Acceptance

| # | 验收标准 |
|---|----------|
| 1 | 列表正确展示模板数据 |
| 2 | 创建模板成功后列表刷新 |
| 3 | YAML 上传触发验证 |
| 4 | 删除确认后刷新列表 |

## Files

```
frontend/
├── app/templates/
│   └── page.tsx
└── components/templates/
    ├── template-list.tsx
    ├── create-template-dialog.tsx
    └── template-detail-dialog.tsx
```
