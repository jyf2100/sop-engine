# v1-m5: 流程引擎

## Goal

实现流程编排的核心引擎和执行器抽象基类。

## PRD Trace

- REQ-0001-009: FlowEngine 核心
- REQ-0001-010: BaseExecutor 抽象基类

## Scope

**做**：
- FlowEngine: 流程编排核心引擎
- BaseExecutor: 执行器抽象基类
- NodeResult: 节点执行结果
- ExecutorRegistry: 执行器注册表
- 单元测试

**不做**：
- 具体节点执行器实现（M6）
- 并行执行
- 持久化存储

## Acceptance

| # | 验收标准 | 验证命令 |
|---|----------|----------|
| 1 | start_execution 创建执行并发布事件 | `pytest tests/unit/test_flow_engine.py::test_start_execution -v` |
| 2 | execute_node 更新状态并发布事件 | `pytest tests/unit/test_flow_engine.py::test_execute_node -v` |
| 3 | transition 正确计算下一节点 | `pytest tests/unit/test_flow_engine.py::test_transition -v` |
| 4 | handle_failure 正确处理异常 | `pytest tests/unit/test_flow_engine.py::test_handle_failure -v` |
| 5 | BaseExecutor 无法直接实例化 | `pytest tests/unit/test_base_executor.py::test_cannot_instantiate -v` |
| 6 | 注册表可按类型获取执行器 | `pytest tests/unit/test_base_executor.py::test_registry -v` |

## Files

```
backend/
├── app/
│   ├── services/
│   │   └── flow_engine.py        # 流程引擎
│   └── executors/
│       ├── __init__.py
│       ├── base.py              # BaseExecutor 抽象基类
│       └── registry.py          # 执行器注册表
└── tests/
    └── unit/
        ├── test_flow_engine.py
        └── test_base_executor.py
```

## Steps

### Step 1: 创建 BaseExecutor 和 NodeResult (TDD)
### Step 2: 创建 ExecutorRegistry (TDD)
### Step 3: 实现 FlowEngine (TDD)
### Step 4: 代码质量检查

## Risks

| 风险 | 缓解措施 |
|------|----------|
| 状态转换复杂 | 使用状态机模式，明确状态定义 |
| 执行器查找失败 | 提供默认执行器，抛出明确异常 |

## DoD 自检

- [x] 每条验收标准可二元判定
- [x] 每条验收绑定验证命令
- [x] Scope 明确不做什么
- [x] 测试覆盖正常/异常/边界场景
