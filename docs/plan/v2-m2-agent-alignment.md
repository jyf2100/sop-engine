# v2-m2: Agent 配置完整对齐

## Goal

与 OpenClaw 官方配置规范完全对齐 Agent 配置，支持 Session、Messages、Commands、Compaction 等完整配置。

## PRD Trace

- **REQ-0001-027**: Agent 配置完整对齐

## Scope

**包含**：
- Session 配置：dm_scope, reset, maintenance, thread_bindings, send_policy
- Messages 配置：queue modes, inbound debounce, TTS 配置
- Commands 配置：native, text, bash, permissions
- Compaction 配置：mode, reserveTokensFloor, memoryFlush
- 模型配置增强：models catalog, image_model, pdf_model
- 沙箱配置增强：docker 后端完整配置

**不包含**：
- SSH/openshell 后端支持（后续迭代）
- TTS 的 UI 配置（仅 API）
- Heartbeat 完整配置（已在 v1 支持）

## Acceptance

- [ ] `pytest tests/unit/test_agent_service.py` 全绿
- [ ] Session 配置正确同步到 `openclaw.json`
- [ ] Messages/Commands 配置完整支持
- [ ] 模型目录配置可用
- [ ] 配置变更后 Agent 运行正常
- [ ] 单元测试覆盖率 ≥80%

## Files

| 文件 | 操作 |
|------|------|
| `backend/app/models/agent.py` | 修改 - 添加完整配置模型 |
| `backend/app/models/session_config.py` | 新增 - Session 配置模型 |
| `backend/app/models/messages_config.py` | 新增 - Messages 配置模型 |
| `backend/app/models/commands_config.py` | 新增 - Commands 配置模型 |
| `backend/app/services/agent_service.py` | 修改 - 新配置同步 |
| `backend/app/api/agents.py` | 修改 - 新字段 API |
| `backend/tests/unit/test_agent_service.py` | 修改 - 新测试 |

## Steps

### Step 1: TDD Red - 测试 Session 配置

**写失败测试**：
```python
# tests/unit/test_agent_service.py

def test_session_config_sync():
    """Session 配置应正确同步"""
    agent = Agent(
        id="test-agent",
        name="Test",
        workspace_path="/tmp/test",
        session_config=SessionConfig(
            dm_scope="per-peer",
            reset=SessionResetConfig(mode="daily", at_hour=4),
            maintenance=SessionMaintenanceConfig(mode="enforce"),
        ),
    )

    service._sync_to_openclaw(agent)
    result = read_openclaw_config()

    agent_config = result["agents"]["list"][0]
    assert agent_config["session"]["dmScope"] == "per-peer"
    assert agent_config["session"]["reset"]["mode"] == "daily"
    assert agent_config["session"]["reset"]["atHour"] == 4
    assert agent_config["session"]["maintenance"]["mode"] == "enforce"
```

**运行到红**：
```bash
cd backend && pytest tests/unit/test_agent_service.py::test_session_config_sync -v
# 预期：FAIL - SessionConfig 模型不存在
```

### Step 2: TDD Green - 实现 Session 配置

**实现**：
```python
# backend/app/models/session_config.py

class SessionConfig(Base):
    """完整 Session 配置"""
    dm_scope: DmScope = "main"
    reset: SessionResetConfig = Field(default_factory=SessionResetConfig)
    reset_by_type: SessionResetByTypeConfig | None = None
    maintenance: SessionMaintenanceConfig | None = None
    thread_bindings: SessionThreadBindingsConfig | None = None
    send_policy: SessionSendPolicyConfig | None = None

    def to_openclaw(self) -> dict:
        result = {"dmScope": self.dm_scope}
        result["reset"] = self.reset.to_openclaw()
        # ... 其他字段
        return result
```

**运行到绿**：
```bash
cd backend && pytest tests/unit/test_agent_service.py::test_session_config_sync -v
# 预期：PASS
```

### Step 3: TDD Red - 测试 Messages 配置

**写失败测试**：
```python
def test_messages_config_sync():
    """Messages 配置应正确同步"""
    agent = Agent(
        id="test-agent",
        messages_config=MessagesConfig(
            queue=QueueConfig(mode="steer"),
            inbound=InboundConfig(debounce_ms=500),
        ),
    )

    service._sync_to_openclaw(agent)
    result = read_openclaw_config()

    assert result["agents"]["defaults"]["messages"]["queue"]["mode"] == "steer"
    assert result["agents"]["defaults"]["messages"]["inbound"]["debounceMs"] == 500
```

### Step 4: TDD Green - 实现 Messages 配置

**实现**：参考 `docs/design/messages-commands-bindings-detailed-design.md`

### Step 5: TDD Red - 测试 Commands 配置

**写失败测试**：
```python
def test_commands_config_sync():
    """Commands 配置应正确同步"""
    agent = Agent(
        id="test-agent",
        commands_config=CommandsConfig(
            native=NativeCommandsConfig(enabled=True),
            text=TextCommandsConfig(prefix="!"),
        ),
    )

    service._sync_to_openclaw(agent)
    result = read_openclaw_config()

    assert result["agents"]["defaults"]["commands"]["native"]["enabled"] == True
    assert result["agents"]["defaults"]["commands"]["text"]["prefix"] == "!"
```

### Step 6: TDD Green - 实现 Commands 配置

**实现**：参考 `docs/design/messages-commands-bindings-detailed-design.md`

### Step 7: 重构（仍绿）

- 统一配置转换逻辑
- 提取公共字段映射
- 添加配置验证

### Step 8: 验证

```bash
# 后端测试
cd backend && pytest tests/unit/test_agent_service.py -v --cov=app/services/agent_service

# 验证覆盖率
pytest --cov=app/services/agent_service --cov-fail-under=80
```

## Risks

| 风险 | 缓解方式 |
|------|----------|
| 配置字段过多 | 按模块分文件，职责清晰 |
| OpenClaw 版本差异 | 参考 stable 分支文档 |
| 测试复杂度高 | 使用 factory_boy 生成测试数据 |

## DoD 硬度自检

| 检查项 | 结果 |
|--------|------|
| DoD 可二元判定 | ✅ 测试通过/失败 |
| 有验证命令 | ✅ pytest 命令 |
| 有反作弊条款 | ✅ 配置同步验证 |
| Scope 明确 | ✅ 不包含 SSH/openshell |
