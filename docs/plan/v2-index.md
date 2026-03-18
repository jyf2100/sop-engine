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
| M1 | Channel 配置对齐 | REQ-0001-026 | 同步保留非管理字段，多账号可用 | todo |
| M2 | Agent 配置对齐 | REQ-0001-027 | Session/Messages/Commands 配置完整 | todo |
| M3 | Bindings 支持 | REQ-0001-028 | 多 Agent 路由可用 | todo |
| M4 | 前端适配 | REQ-0001-029 | 高级配置 Tab 可用 | todo |
| M5 | E2E 测试完善 | REQ-0001-030 | 所有 E2E 测试通过 | todo |

---

## 计划索引

| 文件 | 里程碑 | 状态 |
|------|--------|------|
| [v2-m1-channel-alignment.md](./v2-m1-channel-alignment.md) | M1 | todo |
| [v2-m2-agent-alignment.md](./v2-m2-agent-alignment.md) | M2 | todo |
| [v2-m3-bindings.md](./v2-m3-bindings.md) | M3 | todo |
| [v2-m4-frontend-adaptation.md](./v2-m4-frontend-adaptation.md) | M4 | todo |
| [v2-m5-e2e-tests.md](./v2-m5-e2e-tests.md) | M5 | todo |

---

## 追溯矩阵

| Req ID | PRD | vN Plan | 单元测试 | E2E 测试 | 证据 | 状态 |
|--------|-----|---------|----------|----------|------|------|
| REQ-0001-026 | PRD-0001 §26 | v2-m1-channel-alignment | — | — | — | todo |
| REQ-0001-027 | PRD-0001 §27 | v2-m2-agent-alignment | — | — | — | todo |
| REQ-0001-028 | PRD-0001 §28 | v2-m3-bindings | — | — | — | todo |
| REQ-0001-029 | PRD-0001 §29 | v2-m4-frontend-adaptation | — | — | — | todo |
| REQ-0001-030 | PRD-0001 §30 | v2-m5-e2e-tests | — | — | — | todo |

---

## ECN 索引

（暂无）

---

## 差异列表

（本轮结束后填写）

---

## 当前执行

**v2 规划中** - 等待 v2-m1 开始

详细设计已完成：
- Channel 完整模型（多账号、完整字段）
- Agent 完整模型（Session、Messages、Commands、Compaction）
- Bindings 配置（route/acp 类型）
- 同步策略（merge + 管理字段标记）
