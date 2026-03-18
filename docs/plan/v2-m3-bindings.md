# v2-m3: Bindings 配置支持

## Goal

支持多 Agent 路由，实现灵活的消息分发规则。

## PRD Trace

- **REQ-0001-028**: Bindings 配置支持

## Scope

**包含**：
- Binding 模型：type (route/acp), agent_id, match
- BindingMatch 规则：channel, account_id, peer, guild_id, team_id
- 优先级顺序：peer > guildId > teamId > accountId > default
- ACP 绑定配置：mode, label, cwd, backend
- Bindings CRUD API

**不包含**：
- ACP 后端的完整 UI
- 动态绑定热更新
- Binding 性能优化

## Acceptance

- [ ] `pytest tests/unit/test_binding_service.py` 全绿
- [ ] Binding CRUD API 可用
- [ ] 绑定规则正确写入 `openclaw.json`
- [ ] 优先级匹配逻辑正确
- [ ] 单元测试覆盖率 ≥80%

## Files

| 文件 | 操作 |
|------|------|
| `backend/app/models/binding.py` | 新增 - Binding 模型 |
| `backend/app/services/binding_service.py` | 新增 - Binding 服务 |
| `backend/app/api/bindings.py` | 新增 - Bindings API |
| `backend/app/main.py` | 修改 - 注册路由 |
| `backend/tests/unit/test_binding_service.py` | 新增 - 单元测试 |
| `frontend/lib/api-client.ts` | 修改 - 类型定义 |

## Steps

### Step 1: TDD Red - 测试 Binding 模型

**写失败测试**：
```python
# tests/unit/test_binding_service.py

def test_binding_to_openclaw():
    """Binding 应正确转换为 OpenClaw 格式"""
    binding = Binding(
        id="bind-1",
        type="route",
        agent_id="agent-1",
        match=BindingMatch(
            channel="telegram",
            peer={"kind": "direct", "id": "12345"},
        ),
    )

    result = binding.to_openclaw()

    assert result["type"] == "route"
    assert result["agentId"] == "agent-1"
    assert result["match"]["channel"] == "telegram"
    assert result["match"]["peer"]["kind"] == "direct"
```

**运行到红**：
```bash
cd backend && pytest tests/unit/test_binding_service.py::test_binding_to_openclaw -v
# 预期：FAIL - Binding 模型不存在
```

### Step 2: TDD Green - 实现 Binding 模型

**实现**：
```python
# backend/app/models/binding.py

class BindingMatch(Base):
    """绑定匹配规则"""
    channel: str
    account_id: str | None = None
    peer: dict[str, Any] | None = None
    guild_id: str | None = None
    team_id: str | None = None

    def to_openclaw(self) -> dict:
        result = {"channel": self.channel}
        if self.account_id:
            result["accountId"] = self.account_id
        if self.peer:
            result["peer"] = self.peer
        if self.guild_id:
            result["guildId"] = self.guild_id
        if self.team_id:
            result["teamId"] = self.team_id
        return result

class Binding(Base):
    """Agent 绑定"""
    id: str
    type: Literal["route", "acp"] = "route"
    agent_id: str
    match: BindingMatch
    acp: AcpBindingConfig | None = None

    def to_openclaw(self) -> dict:
        result = {
            "type": self.type,
            "agentId": self.agent_id,
            "match": self.match.to_openclaw(),
        }
        if self.acp and self.type == "acp":
            result["acp"] = self.acp.to_openclaw()
        return result
```

**运行到绿**：
```bash
cd backend && pytest tests/unit/test_binding_service.py::test_binding_to_openclaw -v
# 预期：PASS
```

### Step 3: TDD Red - 测试优先级匹配

**写失败测试**：
```python
def test_binding_priority_order():
    """绑定应按优先级匹配"""
    bindings = [
        Binding(agent_id="agent-1", match=BindingMatch(channel="telegram", peer={"kind": "direct", "id": "123"})),
        Binding(agent_id="agent-2", match=BindingMatch(channel="telegram", guild_id="456")),
        Binding(agent_id="agent-3", match=BindingMatch(channel="telegram")),
    ]

    # peer 级别匹配
    result = match_binding(bindings, channel="telegram", peer={"kind": "direct", "id": "123"})
    assert result.agent_id == "agent-1"

    # guildId 级别匹配
    result = match_binding(bindings, channel="telegram", guild_id="456")
    assert result.agent_id == "agent-2"

    # default 级别匹配
    result = match_binding(bindings, channel="telegram")
    assert result.agent_id == "agent-3"
```

### Step 4: TDD Green - 实现优先级匹配

**实现**：
```python
def match_binding(
    bindings: list[Binding],
    channel: str,
    peer: dict | None = None,
    guild_id: str | None = None,
    team_id: str | None = None,
    account_id: str | None = None,
) -> Binding | None:
    """按优先级匹配绑定

    优先级：peer > guildId > teamId > accountId > default
    """
    def priority(binding: Binding) -> int:
        m = binding.match
        if m.peer:
            return 5  # 最高优先级
        if m.guild_id:
            return 4
        if m.team_id:
            return 3
        if m.account_id:
            return 2
        return 1  # default

    # 过滤匹配 channel 的绑定
    candidates = [b for b in bindings if b.match.channel == channel]

    # 按优先级排序
    candidates.sort(key=priority, reverse=True)

    # 返回最高优先级的绑定
    for binding in candidates:
        if _matches(binding, peer, guild_id, team_id, account_id):
            return binding

    return None
```

### Step 5: TDD Red - 测试同步到 OpenClaw

**写失败测试**：
```python
def test_bindings_sync_to_openclaw():
    """绑定应正确同步到 openclaw.json"""
    bindings = [
        Binding(agent_id="agent-1", match=BindingMatch(channel="telegram")),
    ]

    service.sync_to_openclaw(bindings)
    result = read_openclaw_config()

    assert "bindings" in result
    assert len(result["bindings"]) == 1
    assert result["bindings"][0]["agentId"] == "agent-1"
```

### Step 6: TDD Green - 实现同步

**实现**：`BindingService.sync_to_openclaw()` 方法

### Step 7: 重构（仍绿）

- 提取匹配逻辑到独立函数
- 添加缓存优化
- 完善类型注解

### Step 8: 验证

```bash
cd backend && pytest tests/unit/test_binding_service.py -v --cov=app/services/binding_service
```

## Risks

| 风险 | 缓解方式 |
|------|----------|
| 匹配规则复杂 | 清晰的优先级文档和测试 |
| 性能问题 | 后续迭代添加缓存 |

## DoD 硬度自检

| 检查项 | 结果 |
|--------|------|
| DoD 可二元判定 | ✅ 测试通过/失败 |
| 有验证命令 | ✅ pytest 命令 |
| 有反作弊条款 | ✅ 优先级匹配验证 |
| Scope 明确 | ✅ 不包含动态热更新 |
