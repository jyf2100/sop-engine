# v2-m1: Channel 配置完整对齐

## Goal

与 OpenClaw 官方配置规范完全对齐 Channel 配置，支持所有字段类型、多账号结构，并采用 merge 策略保留非管理字段。

## PRD Trace

- **REQ-0001-026**: Channel 配置完整对齐

## Scope

**包含**：
- 同步逻辑修复：merge 策略替代直接覆盖
- 多账号支持：`accounts` 和 `default_account` 结构
- Telegram 完整字段（30+ 字段）
- Feishu 完整字段（15+ 字段）
- WhatsApp 完整字段（15+ 字段）
- 通用字段（streaming, text_chunk_limit, media_max_mb）

**不包含**：
- Discord/Slack 支持（后续迭代）
- 高级网络配置的 UI（仅 API）
- Webhook 服务的实现（仅配置管理）

## Acceptance

- [ ] `pytest tests/unit/test_channel_service.py` 全绿
- [ ] 同步后 `openclaw.json` 保留非管理字段
- [ ] 多账号结构正确：`channels.telegram.accounts.default.botToken`
- [ ] 所有 Channel 类型字段完整映射
- [ ] 单元测试覆盖率 ≥80%

## Files

| 文件 | 操作 |
|------|------|
| `backend/app/models/channel.py` | 修改 - 添加完整字段 |
| `backend/app/services/channel_service.py` | 修改 - merge 策略 |
| `backend/app/api/channels.py` | 修改 - 新字段 API |
| `backend/tests/unit/test_channel_service.py` | 修改 - 新测试 |
| `frontend/lib/api-client.ts` | 修改 - 类型定义 |

## Steps

### Step 1: TDD Red - 测试同步逻辑

**写失败测试**：
```python
# tests/unit/test_channel_service.py

def test_sync_preserves_non_managed_fields():
    """同步应保留非管理字段"""
    # 给定：OpenClaw 配置包含非管理字段
    existing_config = {
        "channels": {
            "telegram": {
                "botToken": "xxx",
                "customField": "should-be-preserved",  # 非管理字段
            }
        }
    }

    # 当：同步 Channel
    channel = Channel(id="1", type="telegram", bot_token="yyy")
    service._sync_to_openclaw(channel)

    # 则：非管理字段保留
    result = read_openclaw_config()
    assert result["channels"]["telegram"]["customField"] == "should-be-preserved"
    assert result["channels"]["telegram"]["botToken"] == "yyy"

def test_sync_multi_account_structure():
    """多账号结构应正确写入"""
    channel = Channel(
        id="1",
        type="telegram",
        accounts={
            "default": ChannelAccount(bot_token="xxx"),
            "alerts": ChannelAccount(bot_token="yyy"),
        },
        default_account="default",
    )
    service._sync_to_openclaw(channel)

    result = read_openclaw_config()
    assert "accounts" in result["channels"]["telegram"]
    assert result["channels"]["telegram"]["accounts"]["default"]["botToken"] == "xxx"
```

**运行到红**：
```bash
cd backend && pytest tests/unit/test_channel_service.py::test_sync_preserves_non_managed_fields -v
# 预期：FAIL - 当前实现直接覆盖
```

### Step 2: TDD Green - 实现 merge 策略

**实现**：
```python
# backend/app/services/channel_service.py

def _sync_to_openclaw(self) -> None:
    """同步 Channel 到 OpenClaw（merge 策略）"""
    self._backup_openclaw_config()
    config = self._read_openclaw_config()

    if "channels" not in config:
        config["channels"] = {}

    for channel in self._channels.values():
        channel_key = channel.type
        existing = config["channels"].get(channel_key, {})

        # 标记 SOP Engine 管理的字段
        managed_fields = self._get_managed_fields(channel.type)

        # 保留非管理字段，更新管理字段
        new_config = {
            k: v for k, v in existing.items()
            if k not in managed_fields
        }
        new_config.update(self._channel_to_openclaw_format(channel))

        config["channels"][channel_key] = new_config

    self._write_openclaw_config(config)

def _get_managed_fields(self, channel_type: str) -> set[str]:
    """返回 SOP Engine 管理的字段列表"""
    common = {
        "enabled", "dmPolicy", "allowFrom", "groups", "accounts",
        "defaultAccount", "streaming", "textChunkLimit", "mediaMaxMb",
    }
    type_specific = {
        "telegram": {
            "botToken", "groupPolicy", "reactionNotifications",
            "historyLimit", "webhookUrl", "proxy", "network",
        },
        "feishu": {
            "appId", "appSecret", "encryptKey", "verificationToken",
            "domain", "connectionMode", "webhookPath",
        },
        "whatsapp": {
            "phoneId", "ackReaction", "sendReadReceipts",
            "chunkMode", "debounceMs",
        },
    }
    return common | type_specific.get(channel_type, set())
```

**运行到绿**：
```bash
cd backend && pytest tests/unit/test_channel_service.py -v
# 预期：PASS
```

### Step 3: TDD Red - 测试完整字段映射

**写失败测试**：
```python
def test_feishu_full_fields():
    """Feishu 完整字段映射"""
    channel = Channel(
        id="1",
        type="feishu",
        app_id="app123",
        app_secret="secret",
        domain="lark",  # 国际版
        connection_mode="webhook",
        webhook_path="/feishu/events",
        typing_indicator=True,
    )
    result = service._channel_to_openclaw_format(channel)

    assert result["domain"] == "lark"
    assert result["connectionMode"] == "webhook"
    assert result["webhookPath"] == "/feishu/events"
    assert result["typingIndicator"] == True
```

### Step 4: TDD Green - 实现完整字段

**实现**：更新 `Channel` 模型和 `_channel_to_openclaw_format` 方法。

**运行到绿**：
```bash
cd backend && pytest tests/unit/test_channel_service.py -v
# 预期：PASS
```

### Step 5: 重构（仍绿）

- 提取 `_get_managed_fields` 到配置文件
- 优化字段映射逻辑
- 添加类型注解

### Step 6: 验证

```bash
# 后端测试
cd backend && pytest tests/unit/test_channel_service.py -v --cov=app/services/channel_service

# 验证覆盖率
pytest --cov=app/services/channel_service --cov-fail-under=80
```

## Risks

| 风险 | 缓解方式 |
|------|----------|
| OpenClaw 配置格式变化 | 参考 OpenClaw 文档，版本锁定 |
| 多账号逻辑复杂 | 充分测试边界场景 |
| 向后兼容性 | 新字段有默认值，旧配置无需迁移 |

## DoD 硬度自检

| 检查项 | 结果 |
|--------|------|
| DoD 可二元判定 | ✅ 测试通过/失败 |
| 有验证命令 | ✅ pytest 命令 |
| 有反作弊条款 | ✅ 非管理字段保留验证 |
| Scope 明确 | ✅ 不包含 Discord/Slack |
