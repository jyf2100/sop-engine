---
name: superpowers
description: 综合开发技能集合。TRIGGER when 用户请求开发流程指导、调试帮助、代码审查、计划编写、测试策略等。包含 15 个子技能：brainstorming, dispatching-parallel-agents, executing-plans, finishing-a-development-branch, receiving-code-review, requesting-code-review, subagent-driven-development, systematic-debugging, test-driven-development, using-git-worktrees, using-superpowers, verification-before-completion, writing-plans, writing-skills
---

# Superpowers 开发技能集合

本技能集包含 15 个经过实战验证的开发流程技能。

## 快速导航

| 技能 | 用途 | 触发场景 |
|------|------|---------|
| `brainstorming` | 头脑风暴 | 需要生成创意、探索方案 |
| `systematic-debugging` | 系统化调试 | 遇到 bug、测试失败、异常行为 |
| `test-driven-development` | 测试驱动开发 | 编写新功能、重构代码 |
| `writing-plans` | 编写计划 | 需要制定实施方案 |
| `executing-plans` | 执行计划 | 按计划实施功能 |
| `requesting-code-review` | 请求代码审查 | 完成代码后需要审查 |
| `receiving-code-review` | 接收代码审查 | 处理审查反馈 |
| `subagent-driven-development` | 子代理驱动开发 | 复杂任务分解执行 |
| `dispatching-parallel-agents` | 并行代理调度 | 需要并行处理多个任务 |
| `verification-before-completion` | 完成前验证 | 提交前的质量检查 |
| `finishing-a-development-branch` | 完成开发分支 | 分支合并前的流程 |
| `using-git-worktrees` | 使用 Git Worktrees | 多分支并行开发 |
| `writing-skills` | 编写技能 | 创建新的 Claude 技能 |
| `using-superpowers` | 使用本技能集 | 了解如何使用 superpowers |

## 子技能详情

每个子技能都有独立的 SKILL.md，包含完整的流程指导。

### 调试相关
- **systematic-debugging** - 根因分析法，禁止在没有调查前直接修复

### 开发流程
- **test-driven-development** - Red-Green-Refactor 循环
- **writing-plans** → **executing-plans** - 计划驱动开发
- **subagent-driven-development** - 分解任务给子代理

### 代码质量
- **requesting-code-review** - 发起代码审查
- **receiving-code-review** - 处理审查意见
- **verification-before-completion** - 完成前自检

### 并行开发
- **using-git-worktrees** - 多分支并行
- **dispatching-parallel-agents** - 多代理并行

## 使用方式

直接调用子技能名称，例如：

```
/systematic-debugging
/test-driven-development
/writing-plans
```

或描述需求，Claude 会自动匹配对应技能。
