# v1-m12: 前端骨架

## Goal

建立可运行的 Next.js 14 前端项目。

## PRD Trace

- REQ-0001-020: 前端 - 项目骨架

## Scope

**做**：
- Next.js 14 App Router 配置
- shadcn/ui 初始化
- TailwindCSS 配置
- 基础布局组件
- API 客户端封装

**不做**：
- 具体页面实现
- 状态管理

## Acceptance

| # | 验收标准 | 验证命令 |
|---|----------|----------|
| 1 | pnpm dev 启动成功 | `cd frontend && pnpm dev` |
| 2 | 访问根路由返回页面 | 手动验证 localhost:3000 |
| 3 | 基础组件可渲染 | 手动验证 |
| 4 | API 客户端可调用后端 | `pnpm test` |

## Files

```
frontend/
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── components/
│   └── ui/
├── lib/
│   └── api-client.ts
├── package.json
├── tailwind.config.ts
├── tsconfig.json
└── next.config.js
```

## Steps

### Step 1: 初始化 Next.js 项目
### Step 2: 配置 shadcn/ui
### Step 3: 创建布局和 API 客户端
### Step 4: 验证

## Risks

| 风险 | 缓解措施 |
|------|----------|
| shadcn/ui 配置复杂 | 使用官方 CLI |

## DoD 自检

- [x] 每条验收标准可二元判定
- [x] 每条验收绑定验证命令
- [x] Scope 明确不做什么
