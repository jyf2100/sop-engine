# v2-index: OpenClaw 配置完整对齐

## Vision

> 参考: [PRD-0001](../prd/PRD-0001-sop-engine.md) REQ-0001-026 ~ REQ-0001-030

SOP Engine 与 OpenClaw 官方配置规范完全对齐，确保 Channel 和 Agent 配置的完整性和兼容性。

**核心目标**：
1. Channel 配置支持 OpenClaw 完整字段
2. Agent 配置支持 OpenClaw 完整字段（Session/Messages/Commands）
3. 同步逻辑采用 merge 策略，不覆盖非管理字段
4. 支持多账号配置

---

## 设计文档索引

| 文档 | 内容 |
|------|------|
| [openclaw-config-alignment-design.md](../design/openclaw-config-alignment-design.md) | 主设计文档 + Gap 分析 |
| [session-config-detailed-design.md](../design/session-config-detailed-design.md) | Session 配置详细设计 |
| [messages-commands-bindings-detailed-design.md](../design/messages-commands-bindings-detailed-design.md) | Messages/Commands/Bindings 详细设计 |

---

## 里程碑

| # | 里程碑 | 范围 | DoD | 状态 |
|---|--------|------|-----|------|
| M1 | Channel 配置对齐 | REQ-0001-026 | 同步保留非管理字段，多账号可用 | **done** |
| M2 | Agent 配置对齐 | REQ-0001-027 | Session/Messages/Commands 配置完整 | **done** |
| M3 | Bindings 支持 | REQ-0001-028 | 多 Agent 路由可用 | **done** |
| M4 | 前端适配 | REQ-0001-029 | 高级配置 Tab 可用 | **done** |
| M5 | E2E 测试完善 | REQ-0001-030 | 所有 E2E 测试通过 | **in_progress** |

---

## 计划索引

| 文件 | 里程碑 | 状态 |
|------|--------|------|
| [v2-m1-channel-alignment.md](./v2-m1-channel-alignment.md) | M1 | **done** |
| [v2-m2-agent-alignment.md](./v2-m2-agent-alignment.md) | M2 | **done** |
| [v2-m3-bindings.md](./v2-m3-bindings.md) | M3 | **done** |
| [v2-m4-frontend-adaptation.md](./v2-m4-frontend-adaptation.md) | M4 | **done** |
| [v2-m5-e2e-tests.md](./v2-m5-e2e-tests.md) | M5 | **in_progress** |

---

## 追溯矩阵

| Req ID | PRD | vN Plan | 单元测试 | E2E 测试 | 证据 | 状态 |
|--------|-----|---------|----------|----------|------|------|
| REQ-0001-026 | PRD-0001 §26 | v2-m1-channel-alignment | `test_channel_service.py` (19 tests) | — | 19 tests passed | ✅ done |
| REQ-0001-027 | PRD-0001 §27 | v2-m2-agent-alignment | `test_agent_config_alignment.py` (30 tests) | `agent-advanced-config-flow.spec.ts` | 30 tests passed | ✅ done |
| REQ-0001-028 | PRD-0001 §28 | v2-m3-bindings | `test_binding_service.py` (38 tests) | `bindings-flow.spec.ts` | 38 tests passed | ✅ done |
| REQ-0001-029 | PRD-0001 §29 | v2-m4-frontend-adaptation | — | — | TypeScript + build 通过 | ✅ done |
| REQ-0001-030 | PRD-0001 §30 | v2-m5-e2e-tests | — | `regression-v1.spec.ts`, `agent-advanced-config-flow.spec.ts` | — | 🟡 in_progress |

---

## ECN 索引

（暂无）

---

## 差异列表

（本轮结束后填写）

---

## 当前执行

**v2-m5 进行中** - E2E 测试完善

完成内容：
- ✅ `agent-advanced-config-flow.spec.ts`：Agent 高级配置流程 E2E
- ✅ `bindings-flow.spec.ts`：Bindings 配置流程 E2E
- ✅ `regression-v1.spec.ts`：v1 功能回归测试

待完成：
- [ ] 运行所有 E2E 测试验证通过
- [ ] CI 集成配置

下一步：运行 E2E 测试，验证所有流程
