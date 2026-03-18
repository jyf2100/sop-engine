"""Channel 配置管理服务。

提供 Channel 的 CRUD 操作和配置文件管理。
SOP Engine 是 Channel 配置的唯一来源（Source of Truth）。

关键特性：
- Merge 策略：同步时保留非管理字段
- 多账号支持：支持多账号配置结构
- 完整字段：支持 OpenClaw 所有配置字段

对应 REQ-0001-026: Channel 配置完整对齐
"""
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from app.models.channel import (
    AckReactionConfig,
    ChannelAccount,
    ChannelConfig,
    NetworkConfig,
)


@dataclass
class ChannelService:
    """Channel 配置管理服务

    负责 Channel 的创建、更新、删除和配置文件管理。
    所有配置变更都会同步到 OpenClaw 配置文件。
    """

    _channels: dict[str, ChannelConfig] = field(default_factory=dict)
    _openclaw_config_path: Path | None = field(default=None, repr=False)

    def __post_init__(self):
        """初始化 OpenClaw 配置路径"""
        self._openclaw_config_path = Path.home() / ".openclaw" / "openclaw.json"

    def create_channel(
        self,
        channel_id: str,
        name: str,
        type: str,
        enabled: bool = True,
        # 多账号支持
        accounts: dict[str, ChannelAccount] | None = None,
        default_account: str | None = None,
        # 通用配置
        dm_policy: str = "pairing",
        allow_from: list[str] | None = None,
        group_policy: str = "allowlist",
        group_allow_from: list[str] | None = None,
        groups: dict[str, Any] | None = None,
        # 流式配置
        streaming: str = "partial",
        block_streaming: bool | None = None,
        # 消息限制
        text_chunk_limit: int | None = None,
        media_max_mb: int = 100,
        history_limit: int | None = None,
        # 通用高级配置
        config_writes: bool | None = None,
        # Telegram 配置
        bot_token: str | None = None,
        reaction_notifications: str | None = None,
        reaction_allowlist: list[str] | None = None,
        dm_history_limit: int | None = None,
        webhook_url: str | None = None,
        webhook_secret: str | None = None,
        network: NetworkConfig | None = None,
        proxy: str | None = None,
        timeout_seconds: int | None = None,
        link_preview: bool | None = None,
        reply_to_mode: str | None = None,
        custom_commands: dict[str, Any] | None = None,
        dms: dict[str, Any] | None = None,
        # WhatsApp 配置
        phone_id: str | None = None,
        ack_reaction: AckReactionConfig | None = None,
        send_read_receipts: bool | None = None,
        chunk_mode: str | None = None,
        debounce_ms: int | None = None,
        self_chat_mode: bool | None = None,
        # Feishu 配置
        app_id: str | None = None,
        app_secret: str | None = None,
        encrypt_key: str | None = None,
        verification_token: str | None = None,
        domain: str | None = None,
        connection_mode: str | None = None,
        bot_name: str | None = None,
        typing_indicator: bool | None = None,
        resolve_sender_names: bool | None = None,
        webhook_host: str | None = None,
        webhook_port: int | None = None,
        webhook_path: str | None = None,
        **kwargs,  # 接受额外参数以保持向前兼容
    ) -> ChannelConfig:
        """创建 Channel

        Args:
            channel_id: Channel 唯一标识
            name: 显示名称
            type: 平台类型 (telegram, whatsapp, discord, slack, feishu)
            enabled: 是否启用
            accounts: 多账号配置
            default_account: 默认账号
            dm_policy: DM 策略 (pairing, allowlist, open, disabled)
            allow_from: DM 白名单
            group_policy: 群组策略 (open, allowlist, disabled)
            group_allow_from: 群组发送者白名单
            groups: 群组配置
            streaming: 流式输出模式 (off, partial, block)
            text_chunk_limit: 文本分块限制
            media_max_mb: 媒体文件最大大小
            history_limit: 历史消息限制
            config_writes: 是否允许配置写入

        Returns:
            创建的 Channel 实例
        """
        if channel_id in self._channels:
            raise ValueError(f"Channel '{channel_id}' already exists")

        channel = ChannelConfig(
            id=channel_id,
            name=name,
            type=type,
            enabled=enabled,
            accounts=accounts,
            default_account=default_account,
            dm_policy=dm_policy,
            allow_from=allow_from or [],
            group_policy=group_policy,
            group_allow_from=group_allow_from or [],
            groups=groups or {},
            streaming=streaming,
            block_streaming=block_streaming,
            text_chunk_limit=text_chunk_limit,
            media_max_mb=media_max_mb,
            history_limit=history_limit,
            config_writes=config_writes,
            bot_token=bot_token,
            reaction_notifications=reaction_notifications,
            reaction_allowlist=reaction_allowlist,
            dm_history_limit=dm_history_limit,
            webhook_url=webhook_url,
            webhook_secret=webhook_secret,
            network=network,
            proxy=proxy,
            timeout_seconds=timeout_seconds,
            link_preview=link_preview,
            reply_to_mode=reply_to_mode,
            custom_commands=custom_commands,
            dms=dms,
            phone_id=phone_id,
            ack_reaction=ack_reaction,
            send_read_receipts=send_read_receipts,
            chunk_mode=chunk_mode,
            debounce_ms=debounce_ms,
            self_chat_mode=self_chat_mode,
            app_id=app_id,
            app_secret=app_secret,
            encrypt_key=encrypt_key,
            verification_token=verification_token,
            domain=domain,
            connection_mode=connection_mode,
            bot_name=bot_name,
            typing_indicator=typing_indicator,
            resolve_sender_names=resolve_sender_names,
            webhook_host=webhook_host,
            webhook_port=webhook_port,
            webhook_path=webhook_path,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self._channels[channel_id] = channel

        # 同步到 OpenClaw
        self._sync_to_openclaw()

        return channel

    def get_channel(self, channel_id: str) -> ChannelConfig:
        """获取 Channel

        Args:
            channel_id: Channel 唯一标识

        Returns:
            Channel 实例

        Raises:
            KeyError: Channel 不存在
        """
        if channel_id not in self._channels:
            raise KeyError(f"Channel '{channel_id}' not found")
        return self._channels[channel_id]

    def list_channels(self) -> list[ChannelConfig]:
        """列出所有 Channel

        Returns:
            Channel 列表
        """
        return list(self._channels.values())

    def update_channel(
        self,
        channel_id: str,
        name: str | None = None,
        enabled: bool | None = None,
        # 多账号支持
        accounts: dict[str, ChannelAccount] | None = None,
        default_account: str | None = None,
        # 通用配置
        dm_policy: str | None = None,
        allow_from: list[str] | None = None,
        group_policy: str | None = None,
        group_allow_from: list[str] | None = None,
        groups: dict[str, Any] | None = None,
        # 流式配置
        streaming: str | None = None,
        block_streaming: bool | None = None,
        # 消息限制
        text_chunk_limit: int | None = None,
        media_max_mb: int | None = None,
        history_limit: int | None = None,
        # 通用高级配置
        config_writes: bool | None = None,
        # Telegram 配置
        bot_token: str | None = None,
        reaction_notifications: str | None = None,
        reaction_allowlist: list[str] | None = None,
        dm_history_limit: int | None = None,
        webhook_url: str | None = None,
        webhook_secret: str | None = None,
        network: NetworkConfig | None = None,
        proxy: str | None = None,
        # WhatsApp 配置
        phone_id: str | None = None,
        ack_reaction: AckReactionConfig | None = None,
        send_read_receipts: bool | None = None,
        chunk_mode: str | None = None,
        debounce_ms: int | None = None,
        # Feishu 配置
        app_id: str | None = None,
        app_secret: str | None = None,
        encrypt_key: str | None = None,
        verification_token: str | None = None,
        domain: str | None = None,
        connection_mode: str | None = None,
        typing_indicator: bool | None = None,
        webhook_path: str | None = None,
        **kwargs,
    ) -> ChannelConfig:
        """更新 Channel

        Args:
            channel_id: Channel 唯一标识
            name: 新的显示名称
            enabled: 是否启用
            其他参数同 create_channel

        Returns:
            更新后的 Channel 实例
        """
        channel = self.get_channel(channel_id)

        # 辅助函数：获取更新值或保留原值
        def get_value(new_val, old_val):
            return new_val if new_val is not None else old_val

        # 构建更新后的 Channel（不可变模式）
        updated_channel = ChannelConfig(
            id=channel.id,
            name=get_value(name, channel.name),
            type=channel.type,
            enabled=get_value(enabled, channel.enabled),
            accounts=get_value(accounts, channel.accounts),
            default_account=get_value(default_account, channel.default_account),
            dm_policy=get_value(dm_policy, channel.dm_policy),
            allow_from=get_value(allow_from, channel.allow_from),
            group_policy=get_value(group_policy, channel.group_policy),
            group_allow_from=get_value(group_allow_from, channel.group_allow_from),
            groups=get_value(groups, channel.groups),
            streaming=get_value(streaming, channel.streaming),
            block_streaming=get_value(block_streaming, channel.block_streaming),
            text_chunk_limit=get_value(text_chunk_limit, channel.text_chunk_limit),
            media_max_mb=get_value(media_max_mb, channel.media_max_mb),
            history_limit=get_value(history_limit, channel.history_limit),
            config_writes=get_value(config_writes, channel.config_writes),
            bot_token=get_value(bot_token, channel.bot_token),
            reaction_notifications=get_value(reaction_notifications, channel.reaction_notifications),
            reaction_allowlist=get_value(reaction_allowlist, channel.reaction_allowlist),
            dm_history_limit=get_value(dm_history_limit, channel.dm_history_limit),
            webhook_url=get_value(webhook_url, channel.webhook_url),
            webhook_secret=get_value(webhook_secret, channel.webhook_secret),
            network=get_value(network, channel.network),
            proxy=get_value(proxy, channel.proxy),
            phone_id=get_value(phone_id, channel.phone_id),
            ack_reaction=get_value(ack_reaction, channel.ack_reaction),
            send_read_receipts=get_value(send_read_receipts, channel.send_read_receipts),
            chunk_mode=get_value(chunk_mode, channel.chunk_mode),
            debounce_ms=get_value(debounce_ms, channel.debounce_ms),
            app_id=get_value(app_id, channel.app_id),
            app_secret=get_value(app_secret, channel.app_secret),
            encrypt_key=get_value(encrypt_key, channel.encrypt_key),
            verification_token=get_value(verification_token, channel.verification_token),
            domain=get_value(domain, channel.domain),
            connection_mode=get_value(connection_mode, channel.connection_mode),
            typing_indicator=get_value(typing_indicator, channel.typing_indicator),
            webhook_path=get_value(webhook_path, channel.webhook_path),
            created_at=channel.created_at,
            updated_at=datetime.utcnow(),
        )

        self._channels[channel_id] = updated_channel

        # 同步到 OpenClaw
        self._sync_to_openclaw()

        return updated_channel

    def delete_channel(self, channel_id: str) -> None:
        """删除 Channel

        Args:
            channel_id: Channel 唯一标识

        Raises:
            KeyError: Channel 不存在
        """
        if channel_id not in self._channels:
            raise KeyError(f"Channel '{channel_id}' not found")

        del self._channels[channel_id]

        # 同步到 OpenClaw
        self._sync_to_openclaw()

    # ==================== OpenClaw 同步相关方法 ====================

    def _get_managed_fields(self, channel_type: str) -> set[str]:
        """返回 SOP Engine 管理的字段列表

        这些字段在同步时会被 SOP Engine 覆盖。
        非管理字段会被保留。

        Args:
            channel_type: 平台类型

        Returns:
            管理字段集合（OpenClaw 格式，camelCase）
        """
        # 通用管理字段
        common_fields = {
            "enabled",
            "dmPolicy",
            "allowFrom",
            "groupPolicy",
            "groupAllowFrom",
            "groups",
            "streaming",
            "blockStreaming",
            "textChunkLimit",
            "mediaMaxMb",
            "historyLimit",
            "configWrites",
            "accounts",
            "defaultAccount",
        }

        # 平台专属管理字段
        type_specific_fields: dict[str, set[str]] = {
            "telegram": {
                "botToken",
                "reactionNotifications",
                "reactionAllowlist",
                "dmHistoryLimit",
                "webhookUrl",
                "webhookSecret",
                "network",
                "proxy",
                "timeoutSeconds",
                "linkPreview",
                "replyToMode",
                "customCommands",
                "dms",
            },
            "whatsapp": {
                "phoneId",
                "ackReaction",
                "sendReadReceipts",
                "chunkMode",
                "debounceMs",
                "selfChatMode",
            },
            "feishu": {
                "appId",
                "appSecret",
                "encryptKey",
                "verificationToken",
                "domain",
                "connectionMode",
                "botName",
                "typingIndicator",
                "resolveSenderNames",
                "webhookHost",
                "webhookPort",
                "webhookPath",
            },
            "discord": set(),
            "slack": set(),
        }

        return common_fields | type_specific_fields.get(channel_type, set())

    def _sync_to_openclaw(self) -> None:
        """同步所有 Channel 到 ~/.openclaw/openclaw.json

        使用 merge 策略：保留非管理字段，只更新管理字段。
        删除不存在的 Channel。
        """
        # 1. 备份现有配置
        self._backup_openclaw_config()

        config = self._read_openclaw_config()

        # 2. 确保 channels 节点存在
        if "channels" not in config:
            config["channels"] = {}

        # 3. 获取所有已管理的 channel types
        managed_channel_types = {channel.type for channel in self._channels.values()}

        # 4. 删除已不存在的 Channel（只删除 SOP Engine 管理的）
        for channel_type in list(config["channels"].keys()):
            if channel_type not in managed_channel_types:
                # 检查是否是 SOP Engine 管理的 Channel（有 enabled 字段表示被管理过）
                if "enabled" in config["channels"][channel_type]:
                    del config["channels"][channel_type]

        # 5. 使用 merge 策略同步每个 Channel
        for channel in self._channels.values():
            channel_key = channel.type  # 使用 type 作为 key（如 "telegram", "whatsapp"）

            # 获取现有配置
            existing = config["channels"].get(channel_key, {})

            # 获取管理字段
            managed_fields = self._get_managed_fields(channel.type)

            # 保留非管理字段
            unmanaged = {
                k: v for k, v in existing.items()
                if k not in managed_fields
            }

            # 合并：非管理字段 + 新的管理字段
            new_config = unmanaged.copy()
            new_config.update(channel.to_openclaw())

            config["channels"][channel_key] = new_config

        # 写回配置
        self._write_openclaw_config(config)

    def _backup_openclaw_config(self) -> None:
        """备份 openclaw.json

        在每次修改前创建时间戳备份文件。
        """
        if self._openclaw_config_path and self._openclaw_config_path.exists():
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_path = self._openclaw_config_path.with_suffix(
                f".json.backup.{timestamp}"
            )
            import shutil
            shutil.copy2(self._openclaw_config_path, backup_path)

    def _read_openclaw_config(self) -> dict[str, Any]:
        """读取 OpenClaw 配置文件

        Returns:
            配置字典
        """
        if self._openclaw_config_path and self._openclaw_config_path.exists():
            try:
                content = self._openclaw_config_path.read_text()
                return json.loads(content)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _write_openclaw_config(self, config: dict[str, Any]) -> None:
        """写入 OpenClaw 配置文件

        Args:
            config: 配置字典
        """
        if self._openclaw_config_path:
            self._openclaw_config_path.parent.mkdir(parents=True, exist_ok=True)
            self._openclaw_config_path.write_text(
                json.dumps(config, indent=2, ensure_ascii=False) + "\n"
            )
