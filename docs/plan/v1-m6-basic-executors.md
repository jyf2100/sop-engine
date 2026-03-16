# v1-m6: 基础执行器

## Goal

实现 Script、 Agent、 Condition 三种基础节点执行器。

## PRD Trace

- REQ-0001-011: Script 节点执行器
- REQ-0001-012: Agent 节点执行器
- REQ-0001-013: Condition 节点执行器

## Scope

**做**：
- ScriptExecutor: shell 命令执行
- AgentExecutor: OpenClaw Agent 调用
- ConditionExecutor: 条件分支评估
- 单元测试

**不做**：
- 命令白名单安全特性
- 沙箱隔离
- 完整的 Agent 通信实现

- 完整的 Condition 表达式引擎

## Acceptance

| # | 验收标准 | 验证命令 |
|---|----------|----------|
| 1 | 执行 `echo hello` 返回 "hello" | `pytest tests/unit/test_script_executor.py::test_echo_hello -v` |
| 2 | 命令中的 {var} 被正确替换 | `pytest tests/unit/test_script_executor.py::test_variable_substitution -v` |
| 3 | 超时命令抛出异常 | `pytest tests/unit/test_script_executor.py::test_timeout -v` |
| 4 | 夣败命令返回 exit code | `pytest tests/unit/test_script_executor.py::test_failure -v` |
| 5 | Condition 成功匹配分支 | `pytest tests/unit/test_condition_executor.py::test_match_branch -v` |
| 6 | Condition 默认分支 | `pytest tests/unit/test_condition_executor.py::test_default_branch -v` |

## Files

```
backend/
├── app/executors/
│   ├── script_executor.py
│   ├── agent_executor.py
│   └── condition_executor.py
└── tests/
    └── unit/
        ├── test_script_executor.py
        ├── test_agent_executor.py
        └── test_condition_executor.py
```

## Steps

### Step 1: 实现 ScriptExecutor (TDD)
### Step 2: 实现 ConditionExecutor (TDD)
### Step 3: 实现 AgentExecutor (TDD - mock OpenClaw)
### Step 4: 代码质量检查

## Risks

| 风险 | 缓解措施 |
|------|----------|
| 命令注入 | 变量替换后验证命令格式 |
| OpenClaw 不可用 | 使用 mock 测试， |

## DoD 自检

- [x] 每条验收标准可二元判定
- [x] 每条验收绑定验证命令
- [x] Scope 明确不做什么
- [x] 测试覆盖正常/异常/边界场景
