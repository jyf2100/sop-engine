# v1-m4: 核心服务

## Goal

实现流程编排的核心服务：模板解析器、事件总线和上下文管理。

## PRD Trace

- REQ-0001-006: YAML 模板解析器
- REQ-0001-007: EventBus 实现
- REQ-0001-008: Context 上下文管理

## Scope

**做**：
- TemplateParser: YAML 模板解析和验证
- EventBus: Redis Streams 事件发布/订阅
- ContextManager: 执行上下文变量管理
- 单元测试 + 集成测试

**不做**：
- 实际 Redis 连接（使用 mock 或内存实现）
- 流程执行逻辑（M5）
- 消费者组管理
- 事件重放

## Acceptance

| # | 验收标准 | 验证命令 |
|---|----------|----------|
| 1 | 合法 YAML 解析成功 | `pytest tests/unit/test_template_parser.py::test_parse_valid_yaml -v` |
| 2 | 缺少 start 节点抛出异常 | `pytest tests/unit/test_template_parser.py::test_missing_start_node -v` |
| 3 | 缺少 end 节点抛出异常 | `pytest tests/unit/test_template_parser.py::test_missing_end_node -v` |
| 4 | EventBus publish/consume 工作 | `pytest tests/unit/test_event_bus.py::test_publish_consume -v` |
| 5 | EventBus ack 工作 | `pytest tests/unit/test_event_bus.py::test_ack -v` |
| 6 | ContextManager get/set 工作 | `pytest tests/unit/test_context_manager.py::test_get_set -v` |
| 7 | resolve_variables 替换模板变量 | `pytest tests/unit/test_context_manager.py::test_resolve_variables -v` |

## Files

```
backend/
├── app/
│   ├── services/
│   │   ├── template_parser.py    # YAML 解析器
│   │   ├── event_bus.py          # Redis Streams 事件总线
│   │   └── context_manager.py    # 上下文管理
│   └── models/
│       └── flow_template.py      # 流程模板模型
└── tests/
    └── unit/
        ├── test_template_parser.py
        ├── test_event_bus.py
        └── test_context_manager.py
```

## Steps

### Step 1: 创建 FlowTemplate 模型
### Step 2: 实现 TemplateParser (TDD)
### Step 3: 实现 EventBus (TDD)
### Step 4: 实现 ContextManager (TDD)
### Step 5: 代码质量检查

## Risks

| 风险 | 缓解措施 |
|------|----------|
| Redis 连接不稳定 | 使用连接池、重试机制、mock 测试 |
| 模板变量注入 | 严格校验变量名格式 |

## DoD 自检

- [x] 每条验收标准可二元判定
- [x] 每条验收绑定验证命令
- [x] Scope 明确不做什么
- [x] 测试覆盖正常/异常/边界场景
