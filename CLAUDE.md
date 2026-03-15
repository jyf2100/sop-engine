# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

SOP（标准作业流程）编排引擎，基于 OpenClaw 构建。每个节点是一个 Agent，支持条件分支、并行执行、循环/重试、人工审批等高级特性。

## 技术栈

| 层面 | 技术 |
|------|------|
| 后端框架 | FastAPI |
| 后端语言 | Python 3.11+ |
| 数据库 | PostgreSQL + SQLAlchemy 2.0 |
| 消息队列 | Redis Streams |
| 前端框架 | Next.js 14 (App Router) |
| 前端语言 | React 18 + TypeScript |
| UI 组件 | shadcn/ui + TailwindCSS |
| 状态管理 | Zustand + TanStack Query |
| 流程编辑 | React Flow |

## 常用命令

### 后端

```bash
# 安装依赖
pip install -e .

# 运行开发服务器
uvicorn app.main:app --reload

# 运行测试
pytest

# 运行单个测试
pytest tests/unit/test_parser.py -v

# 覆盖率检查
pytest --cov=app --cov-fail-under=90
```

### 前端

```bash
# 安装依赖
pnpm install

# 运行开发服务器
pnpm dev

# 运行测试
pnpm test

# E2E 测试
pnpm test:e2e
```

## 项目结构

```
sop-engine/
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── main.py         # FastAPI 入口
│   │   ├── config.py       # 配置加载
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 核心服务
│   │   ├── executors/      # 节点执行器
│   │   ├── api/            # 路由处理
│   │   └── utils/          # 工具函数
│   ├── tests/
│   └── templates/          # YAML 流程模板
│
├── frontend/               # Next.js 前端
│   ├── src/
│   │   ├── app/            # App Router 路由
│   │   ├── components/     # UI 组件
│   │   ├── features/       # 功能模块
│   │   ├── hooks/          # 自定义 Hooks
│   │   ├── stores/         # Zustand 状态
│   │   └── lib/            # API 客户端
│   └── tests/
│
├── docs/
│   ├── plan.md             # 实现计划
│   └── rules/              # 开发规范
│
└── CLAUDE.md
```

## 架构说明

```
Template Parser → Engine Core → Node Executors
                      ↓
                EventBus (Redis Streams)
                      ↓
     ┌────────────────┼────────────────┐
     ↓                ↓                ↓
Flow Template    Instance        Context
 (PostgreSQL)   Execution        (Redis)
                (PostgreSQL)
```

## 节点类型

| 类型 | 说明 | 输出 |
|------|------|------|
| start | 开始节点 | - |
| end | 结束节点 | - |
| agent | 调用 OpenClaw Agent | agent 执行结果 |
| script | 执行脚本/命令 | 命令输出 |
| condition | 条件分支 | 匹配的分支 |
| parallel | 并行执行 | 所有分支结果 |
| loop | 循环执行 | 每次迭代结果 |
| human | 人工审批 | 审批决策 |
| wait | 等待/定时 | - |

## 开发军规

**详见**: [docs/rules/development-rules.md](docs/rules/development-rules.md)

核心要点：
- **数据不可变**：使用 `model_copy()` 而非直接修改
- **测试先行**：TDD 红→绿→重构，覆盖率 ≥90%
- **错误转换**：外部异常转为项目异常
- **日志结构化**：包含 `execution_id` + `node_id`
