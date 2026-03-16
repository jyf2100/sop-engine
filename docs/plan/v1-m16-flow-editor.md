# v1-m16: 流程编辑器

## Goal

可视化编辑流程模板。

## PRD Trace

- REQ-0001-024: 前端 - 流程编辑器

## Scope

**做**：
- 流程可视化展示（React Flow）
- 节点拖拽创建
- 节点连线
- YAML 导出

**不做**：
- YAML 导入解析
- 流程模板保存
- 节点配置详细编辑

## Acceptance

| # | 验收标准 |
|---|----------|
| 1 | 节点可拖拽创建 |
| 2 | 节点可连线 |
| 3 | 可导出 YAML |
| 4 | 流程图正确渲染 |

## Files

```
frontend/
├── app/editor/
│   └── page.tsx
└── components/editor/
    ├── flow-canvas.tsx
    ├── node-palette.tsx
    └── yaml-export-dialog.tsx
```
