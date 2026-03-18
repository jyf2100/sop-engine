"""Channel Service 单元测试。

测试 Channel 配置管理服务的核心功能：
- CRUD 操作
- OpenClaw 同步（merge 策略）
- 多账号支持
- 完整字段映射

对应 REQ-0001-026: Channel 配置完整对齐
"""
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.models.channel import (
    ChannelAccount,
    ChannelConfig,
)
from app.services.channel_service import ChannelService


@pytest.fixture
def temp_config_path(tmp_path: Path) -> Path:
    """创建临时配置文件路径"""
    config_path = tmp_path / ".openclaw" / "openclaw.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    return config_path


@pytest.fixture
def service(temp_config_path: Path) -> ChannelService:
    """创建使用临时配置路径的 ChannelService"""
    service = ChannelService()
    service._openclaw_config_path = temp_config_path
    return service


class TestSyncPreservesNonManagedFields:
    """测试同步保留非管理字段（merge 策略）"""

    def test_sync_preserves_custom_field_in_telegram(
        self, service: ChannelService, temp_config_path: Path
    ):
        """同步应保留 Telegram 的非管理字段

        Given: OpenClaw 配置包含非管理字段 customField
        When: 同步 Channel
        Then: customField 应保留
        """
        # Given: 预设配置包含非管理字段
        existing_config = {
            "channels": {
                "telegram": {
                    "botToken": "old-token",
                    "customField": "should-be-preserved",
                    "anotherCustom": {"nested": "value"},
                }
            },
            "otherSection": "should-also-preserve",
        }
        temp_config_path.write_text(json.dumps(existing_config))

        # When: 创建/更新 Channel
        service.create_channel(
            channel_id="telegram-main",
            name="Main Telegram",
            type="telegram",
            bot_token="new-token",
        )

        # Then: 非管理字段保留
        result = json.loads(temp_config_path.read_text())
        assert result["channels"]["telegram"]["customField"] == "should-be-preserved"
        assert result["channels"]["telegram"]["anotherCustom"] == {"nested": "value"}
        assert result["channels"]["telegram"]["botToken"] == "new-token"
        assert result["otherSection"] == "should-also-preserve"

    def test_sync_preserves_custom_field_in_feishu(
        self, service: ChannelService, temp_config_path: Path
    ):
        """同步应保留 Feishu 的非管理字段"""
        # Given
        existing_config = {
            "channels": {
                "feishu": {
                    "appId": "old-app-id",
                    "customWebhook": "https://custom.webhook.url",
                }
            }
        }
        temp_config_path.write_text(json.dumps(existing_config))

        # When
        service.create_channel(
            channel_id="feishu-main",
            name="Main Feishu",
            type="feishu",
            app_id="new-app-id",
            app_secret="secret",
        )

        # Then
        result = json.loads(temp_config_path.read_text())
        assert result["channels"]["feishu"]["customWebhook"] == "https://custom.webhook.url"
        assert result["channels"]["feishu"]["appId"] == "new-app-id"

    def test_sync_preserves_custom_field_in_whatsapp(
        self, service: ChannelService, temp_config_path: Path
    ):
        """同步应保留 WhatsApp 的非管理字段"""
        # Given
        existing_config = {
            "channels": {
                "whatsapp": {
                    "phoneId": "old-phone-id",
                    "customIntegration": {"enabled": True},
                }
            }
        }
        temp_config_path.write_text(json.dumps(existing_config))

        # When
        service.create_channel(
            channel_id="whatsapp-main",
            name="Main WhatsApp",
            type="whatsapp",
            phone_id="new-phone-id",
        )

        # Then
        result = json.loads(temp_config_path.read_text())
        assert result["channels"]["whatsapp"]["customIntegration"] == {"enabled": True}
        assert result["channels"]["whatsapp"]["phoneId"] == "new-phone-id"


class TestMultiAccountSupport:
    """测试多账号支持"""

    def test_sync_multi_account_structure_telegram(
        self, service: ChannelService, temp_config_path: Path
    ):
        """Telegram 多账号结构应正确写入

        Given: 配置多个 Telegram 账号
        When: 同步到 OpenClaw
        Then: accounts 结构正确
        """
        # When
        channel = service.create_channel(
            channel_id="telegram-main",
            name="Multi-Account Telegram",
            type="telegram",
            accounts={
                "default": ChannelAccount(
                    name="Default Bot",
                    enabled=True,
                    bot_token="token-xxx",
                ),
                "alerts": ChannelAccount(
                    name="Alerts Bot",
                    enabled=True,
                    bot_token="token-yyy",
                ),
            },
            default_account="default",
        )

        # Then
        result = json.loads(temp_config_path.read_text())
        telegram_config = result["channels"]["telegram"]

        assert "accounts" in telegram_config
        assert "default" in telegram_config["accounts"]
        assert "alerts" in telegram_config["accounts"]
        assert telegram_config["accounts"]["default"]["botToken"] == "token-xxx"
        assert telegram_config["accounts"]["alerts"]["botToken"] == "token-yyy"
        assert telegram_config["defaultAccount"] == "default"

    def test_sync_multi_account_structure_feishu(
        self, service: ChannelService, temp_config_path: Path
    ):
        """Feishu 多账号结构应正确写入"""
        # When
        service.create_channel(
            channel_id="feishu-main",
            name="Multi-Account Feishu",
            type="feishu",
            accounts={
                "cn": ChannelAccount(
                    name="飞书（国内版）",
                    app_id="app-cn",
                    app_secret="secret-cn",
                    domain="feishu",
                ),
                "intl": ChannelAccount(
                    name="Lark（国际版）",
                    app_id="app-intl",
                    app_secret="secret-intl",
                    domain="lark",
                ),
            },
            default_account="cn",
        )

        # Then
        result = json.loads(temp_config_path.read_text())
        feishu_config = result["channels"]["feishu"]

        assert "accounts" in feishu_config
        assert feishu_config["accounts"]["cn"]["domain"] == "feishu"
        assert feishu_config["accounts"]["intl"]["domain"] == "lark"
        assert feishu_config["defaultAccount"] == "cn"

    def test_single_account_uses_default_structure(
        self, service: ChannelService, temp_config_path: Path
    ):
        """单账号时使用默认结构（不使用 accounts）"""
        # When
        service.create_channel(
            channel_id="telegram-simple",
            name="Simple Telegram",
            type="telegram",
            bot_token="single-token",
        )

        # Then: 单账号时直接使用 botToken，不使用 accounts 结构
        result = json.loads(temp_config_path.read_text())
        telegram_config = result["channels"]["telegram"]

        # 单账号模式：直接使用 botToken
        assert telegram_config["botToken"] == "single-token"
        # 不使用 accounts 结构
        assert "accounts" not in telegram_config


class TestTelegramFullFields:
    """测试 Telegram 完整字段映射"""

    def test_telegram_reaction_notifications(
        self, service: ChannelService, temp_config_path: Path
    ):
        """Telegram reaction_notifications 字段"""
        # When
        service.create_channel(
            channel_id="telegram-main",
            name="Telegram",
            type="telegram",
            bot_token="token",
            reaction_notifications="own",
            reaction_allowlist=["👍", "❤️"],
        )

        # Then
        result = json.loads(temp_config_path.read_text())
        tg = result["channels"]["telegram"]
        assert tg["reactionNotifications"] == "own"
        assert tg["reactionAllowlist"] == ["👍", "❤️"]

    def test_telegram_history_limits(
        self, service: ChannelService, temp_config_path: Path
    ):
        """Telegram 历史消息限制字段"""
        # When
        service.create_channel(
            channel_id="telegram-main",
            name="Telegram",
            type="telegram",
            bot_token="token",
            history_limit=100,
            dm_history_limit=50,
        )

        # Then
        result = json.loads(temp_config_path.read_text())
        tg = result["channels"]["telegram"]
        assert tg["historyLimit"] == 100
        assert tg["dmHistoryLimit"] == 50

    def test_telegram_webhook_config(
        self, service: ChannelService, temp_config_path: Path
    ):
        """Telegram Webhook 配置字段"""
        # When
        service.create_channel(
            channel_id="telegram-main",
            name="Telegram",
            type="telegram",
            bot_token="token",
            webhook_url="https://example.com/webhook/telegram",
            webhook_secret="secret123",
        )

        # Then
        result = json.loads(temp_config_path.read_text())
        tg = result["channels"]["telegram"]
        assert tg["webhookUrl"] == "https://example.com/webhook/telegram"
        assert tg["webhookSecret"] == "secret123"

    def test_telegram_network_config(
        self, service: ChannelService, temp_config_path: Path
    ):
        """Telegram 网络配置字段"""
        # When
        service.create_channel(
            channel_id="telegram-main",
            name="Telegram",
            type="telegram",
            bot_token="token",
            network={"autoSelectFamily": True, "dnsResultOrder": "ipv4first"},
            proxy="http://proxy.example.com:8080",
        )

        # Then
        result = json.loads(temp_config_path.read_text())
        tg = result["channels"]["telegram"]
        assert tg["network"]["autoSelectFamily"] == True
        assert tg["proxy"] == "http://proxy.example.com:8080"


class TestFeishuFullFields:
    """测试 Feishu 完整字段映射"""

    def test_feishu_domain_and_connection_mode(
        self, service: ChannelService, temp_config_path: Path
    ):
        """Feishu domain 和 connection_mode 字段"""
        # When
        service.create_channel(
            channel_id="feishu-main",
            name="Lark",
            type="feishu",
            app_id="app123",
            app_secret="secret",
            domain="lark",  # 国际版
            connection_mode="webhook",
        )

        # Then
        result = json.loads(temp_config_path.read_text())
        fs = result["channels"]["feishu"]
        assert fs["domain"] == "lark"
        assert fs["connectionMode"] == "webhook"

    def test_feishu_webhook_config(
        self, service: ChannelService, temp_config_path: Path
    ):
        """Feishu Webhook 配置字段"""
        # When
        service.create_channel(
            channel_id="feishu-main",
            name="Feishu",
            type="feishu",
            app_id="app123",
            app_secret="secret",
            webhook_host="0.0.0.0",
            webhook_port=8080,
            webhook_path="/feishu/events",
        )

        # Then
        result = json.loads(temp_config_path.read_text())
        fs = result["channels"]["feishu"]
        assert fs["webhookHost"] == "0.0.0.0"
        assert fs["webhookPort"] == 8080
        assert fs["webhookPath"] == "/feishu/events"

    def test_feishu_typing_and_sender_config(
        self, service: ChannelService, temp_config_path: Path
    ):
        """Feishu 输入提示和发送者解析配置"""
        # When
        service.create_channel(
            channel_id="feishu-main",
            name="Feishu",
            type="feishu",
            app_id="app123",
            app_secret="secret",
            typing_indicator=False,
            resolve_sender_names=True,
            bot_name="助手Bot",
        )

        # Then
        result = json.loads(temp_config_path.read_text())
        fs = result["channels"]["feishu"]
        assert fs["typingIndicator"] == False
        assert fs["resolveSenderNames"] == True
        assert fs["botName"] == "助手Bot"


class TestWhatsAppFullFields:
    """测试 WhatsApp 完整字段映射"""

    def test_whatsapp_ack_reaction(
        self, service: ChannelService, temp_config_path: Path
    ):
        """WhatsApp 确认反应配置"""
        # When
        service.create_channel(
            channel_id="whatsapp-main",
            name="WhatsApp",
            type="whatsapp",
            phone_id="phone123",
            ack_reaction={"emoji": "✅", "scope": "all"},
        )

        # Then
        result = json.loads(temp_config_path.read_text())
        wa = result["channels"]["whatsapp"]
        assert wa["ackReaction"]["emoji"] == "✅"
        assert wa["ackReaction"]["scope"] == "all"

    def test_whatsapp_streaming_config(
        self, service: ChannelService, temp_config_path: Path
    ):
        """WhatsApp 流式和分块配置"""
        # When
        service.create_channel(
            channel_id="whatsapp-main",
            name="WhatsApp",
            type="whatsapp",
            phone_id="phone123",
            send_read_receipts=True,
            chunk_mode="sentence",
            debounce_ms=500,
        )

        # Then
        result = json.loads(temp_config_path.read_text())
        wa = result["channels"]["whatsapp"]
        assert wa["sendReadReceipts"] == True
        assert wa["chunkMode"] == "sentence"
        assert wa["debounceMs"] == 500


class TestCommonFields:
    """测试通用字段"""

    def test_common_streaming_and_chunk_limit(
        self, service: ChannelService, temp_config_path: Path
    ):
        """通用流式和分块限制字段"""
        # When
        service.create_channel(
            channel_id="telegram-main",
            name="Telegram",
            type="telegram",
            bot_token="token",
            streaming="block",
            text_chunk_limit=4000,
            media_max_mb=50,
        )

        # Then
        result = json.loads(temp_config_path.read_text())
        tg = result["channels"]["telegram"]
        assert tg["streaming"] == "block"
        assert tg["textChunkLimit"] == 4000
        assert tg["mediaMaxMb"] == 50

    def test_config_writes_field(
        self, service: ChannelService, temp_config_path: Path
    ):
        """config_writes 字段"""
        # When
        service.create_channel(
            channel_id="telegram-main",
            name="Telegram",
            type="telegram",
            bot_token="token",
            config_writes=False,
        )

        # Then
        result = json.loads(temp_config_path.read_text())
        tg = result["channels"]["telegram"]
        assert tg["configWrites"] == False


class TestUpdateChannel:
    """测试更新 Channel 时保留非管理字段"""

    def test_update_preserves_non_managed_fields(
        self, service: ChannelService, temp_config_path: Path
    ):
        """更新 Channel 时应保留非管理字段"""
        # Given: 先创建一个 Channel
        temp_config_path.write_text(json.dumps({
            "channels": {
                "telegram": {
                    "botToken": "old-token",
                    "customField": "preserved",
                }
            }
        }))

        service.create_channel(
            channel_id="telegram-main",
            name="Telegram",
            type="telegram",
            bot_token="old-token",
        )

        # When: 更新 Channel
        service.update_channel(
            channel_id="telegram-main",
            bot_token="new-token",
            streaming="block",
        )

        # Then: 非管理字段保留
        result = json.loads(temp_config_path.read_text())
        tg = result["channels"]["telegram"]
        assert tg["botToken"] == "new-token"
        assert tg["streaming"] == "block"
        assert tg["customField"] == "preserved"


class TestDeleteChannel:
    """测试删除 Channel"""

    def test_delete_removes_from_config(
        self, service: ChannelService, temp_config_path: Path
    ):
        """删除 Channel 应从配置中移除"""
        # Given
        service.create_channel(
            channel_id="telegram-main",
            name="Telegram",
            type="telegram",
            bot_token="token",
        )

        # When
        service.delete_channel("telegram-main")

        # Then
        result = json.loads(temp_config_path.read_text())
        assert "telegram" not in result["channels"]
