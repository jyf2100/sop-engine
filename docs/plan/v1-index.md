# v1-index: SOP 编排引擎 - 第一版本计划

## Vision

> 参考: [PRD-0001](../prd/PRD-0001-sop-engine.md)

构建一个基于 OpenClaw 的 SOP 编排平台，让用户能够通过 YAML 模板定义工作流，系统自动编排执行。

---

## 里程碑

| # | 里程碑 | 范围 | DoD | 状态 |
|---|--------|------|-----|------|
| M1 | 后端骨架 | REQ-0001-001, 002 | 服务启动成功，模型定义完成 | done |
| M2 | Agent 配置管理 | REQ-0001-003 | Agent CRUD + 配置文件管理 + 同步 | done |
| M3 | OpenClaw 配置管理 | REQ-0001-004, 005 | 主配置 + 凭证管理可用 | done |
| M4 | 核心服务 | REQ-0001-006, 007, 008 | 解析器/EventBus/Context 可用 | done |
| M5 | 流程引擎 | REQ-0001-009, 010 | FlowEngine 可执行流程 | done |
| M6 | 基础执行器 | REQ-0001-011, 012, 013 | Script/Agent/Condition 可用 | done |
| M7 | 审批执行器 | REQ-0001-014 | Human 节点可用 | done |
| M8 | Agent API | REQ-0001-015 | Agent CRUD API 可用 | todo |
| M9 | 模板 API | REQ-0001-016 | 模板 CRUD 可用 | todo |
| M10 | 执行 API | REQ-0001-017 | 执行控制可用 | todo |
| M11 | 审批 API | REQ-0001-018, 019 | 审批 + WebSocket 可用 | todo |
| M12 | 前端骨架 | REQ-0001-020 | 前端启动成功 | todo |
| M13 | 模板管理页 | REQ-0001-021 | 模板 CRUD 页面可用 | todo |
| M14 | 执行监控页 | REQ-0001-022 | 监控页面可用 | todo |
| M15 | 审批工作台 | REQ-0001-023 | 审批页面可用 | todo |
| M16 | 流程编辑器 | REQ-0001-024 | 可视化编辑器可用 | todo |
| M17 | Agent 管理页 | REQ-0001-025 | Agent 管理页面可用 | todo |

---

## 计划索引

| 文件 | 里程碑 | 状态 |
|------|--------|------|
| [v1-m1-backend-skeleton.md](./v1-m1-backend-skeleton.md) | M1 | todo |
| [v1-m2-agent-config.md](./v1-m2-agent-config.md) | M2 | todo |
| [v1-m3-openclaw-config.md](./v1-m3-openclaw-config.md) | M3 | todo |
| [v1-m4-core-services.md](./v1-m4-core-services.md) | M4 | todo |
| [v1-m5-flow-engine.md](./v1-m5-flow-engine.md) | M5 | done |
| [v1-m6-basic-executors.md](./v1-m6-basic-executors.md) | M6 | done |
| [v1-m7-human-executor.md](./v1-m7-human-executor.md) | M7 | done |
| [v1-m8-agent-api.md](./v1-m8-agent-api.md) | M8 | todo |
| [v1-m9-template-api.md](./v1-m9-template-api.md) | M9 | todo |
| [v1-m10-execution-api.md](./v1-m10-execution-api.md) | M10 | todo |
| [v1-m11-approval-api.md](./v1-m11-approval-api.md) | M11 | todo |
| [v1-m12-frontend-skeleton.md](./v1-m12-frontend-skeleton.md) | M12 | todo |
| [v1-m13-template-page.md](./v1-m13-template-page.md) | M13 | todo |
| [v1-m14-execution-page.md](./v1-m14-execution-page.md) | M14 | todo |
| [v1-m15-approval-page.md](./v1-m15-approval-page.md) | M15 | todo |
| [v1-m16-flow-editor.md](./v1-m16-flow-editor.md) | M16 | todo |
| [v1-m17-agent-page.md](./v1-m17-agent-page.md) | M17 | todo |

---

## 追溯矩阵

| Req ID | PRD | vN Plan | 单元测试 | E2E 测试 | 证据 | 状态 |
|--------|-----|---------|----------|----------|------|------|
| REQ-0001-001 | PRD-0001 §1 | v1-m1-backend-skeleton | — | — | — | todo |
| REQ-0001-002 | PRD-0001 §2 | v1-m1-backend-skeleton | — | — | — | todo |
| REQ-0001-003 | PRD-0001 §3 | v1-m2-agent-config | `test_agent_service.py`, `test_agent_sync.py` | — | 51 tests passed | done |
| REQ-0001-004 | PRD-0001 §4 | v1-m3-openclaw-config | `test_openclaw_config.py` | — | 85 tests passed | done |
| REQ-0001-005 | PRD-0001 §5 | v1-m3-openclaw-config | `test_credential_service.py`, `test_crypto.py` | `test_credential_sync.py` | 85 tests passed | done |
| REQ-0001-006 | PRD-0001 §6 | v1-m4-core-services | `test_template_parser.py` | — | 122 tests passed | done |
| REQ-0001-007 | PRD-0001 §7 | v1-m4-core-services | `test_event_bus.py` | — | 122 tests passed | done |
| REQ-0001-008 | PRD-0001 §8 | v1-m4-core-services | `test_context_manager.py` | — | 122 tests passed | done |
| REQ-0001-009 | PRD-0001 §9 | v1-m5-flow-engine | `test_flow_engine.py` | — | 166 tests passed | done |
| REQ-0001-010 | PRD-0001 §10 | v1-m5-flow-engine | `test_flow_engine.py` | — | 166 tests passed | done |
| REQ-0001-011 | PRD-0001 §11 | v1-m6-basic-executors | `test_script_executor.py` | — | 181 tests passed | done |
| REQ-0001-012 | PRD-0001 §12 | v1-m6-basic-executors | `test_script_executor.py` | — | 181 tests passed | done |
| REQ-0001-013 | PRD-0001 §13 | v1-m6-basic-executors | `test_script_executor.py` | — | 181 tests passed | done |
| REQ-0001-014 | PRD-0001 §14 | v1-m7-human-executor | `test_human_executor.py` | — | 181 tests passed | done |
| REQ-0001-015 | PRD-0001 §15 | v1-m8-agent-api | — | — | — | todo |
| REQ-0001-016 | PRD-0001 §16 | v1-m9-template-api | — | — | — | todo |
| REQ-0001-017 | PRD-0001 §17 | v1-m10-execution-api | — | — | — | todo |
| REQ-0001-018 | PRD-0001 §18 | v1-m11-approval-api | — | — | — | todo |
| REQ-0001-019 | PRD-0001 §19 | v1-m11-approval-api | — | — | — | todo |
| REQ-0001-020 | PRD-0001 §20 | v1-m12-frontend-skeleton | — | — | — | todo |
| REQ-0001-021 | PRD-0001 §21 | v1-m13-template-page | — | — | — | todo |
| REQ-0001-022 | PRD-0001 §22 | v1-m14-execution-page | — | — | — | todo |
| REQ-0001-023 | PRD-0001 §23 | v1-m15-approval-page | — | — | — | todo |
| REQ-0001-024 | PRD-0001 §24 | v1-m16-flow-editor | — | — | — | todo |
| REQ-0001-025 | PRD-0001 §25 | v1-m17-agent-page | — | — | — | todo |

---

## ECN 索引

（暂无）

---

## 差异列表

（第一轮结束后填写）

---

## 当前执行

**M8: Agent API** → [v1-m8-agent-api.md](./v1-m8-agent-api.md)
