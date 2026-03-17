"""Channel 配置管理服务。

提供 Channel 的 CRUD 操作和配置文件管理。
SOP Engine 是 Channel 配置的唯一来源（Source of Truth）。
"""
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from app.models import ChannelConfig


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
        bot_token: str | None = None,
        dm_policy: str = "pairing",
        allow_from: list[str] | None = None,
        group_policy: str = "allowlist",
        group_allow_from: list[str] | None = None,
        groups: dict[str, Any] | None = None,
        streaming: str = "partial",
        media_max_mb: int = 100,
        phone_id: str | None = None,
        # 飞书配置
        app_id: str | None = None,
        app_secret: str | None = None,
        encrypt_key: str | None = None,
        verification_token: str | None = None,
    ) -> ChannelConfig:
        """创建 Channel

        Args:
            channel_id: Channel 唯一标识
            name: 显示名称
            type: 平台类型 (telegram, whatsapp, discord, slack, feishu)
            enabled: 是否启用
            bot_token: Telegram Bot Token
            dm_policy: DM 策略 (pairing, allowlist, open, disabled)
            allow_from: DM 白名单
            group_policy: 群组策略 (open, allowlist, disabled)
            group_allow_from: 群组发送者白名单
            groups: 群组配置
            streaming: 流式输出模式 (off, partial, block)
            media_max_mb: 媒体文件最大大小
            phone_id: WhatsApp Phone ID
            app_id: 飞书 App ID
            app_secret: 飞书 App Secret
            encrypt_key: 飞书 Encrypt Key
            verification_token: 飞书 Verification Token

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
            bot_token=bot_token,
            dm_policy=dm_policy,
            allow_from=allow_from or [],
            group_policy=group_policy,
            group_allow_from=group_allow_from or [],
            groups=groups or {},
            streaming=streaming,
            media_max_mb=media_max_mb,
            phone_id=phone_id,
            app_id=app_id,
            app_secret=app_secret,
            encrypt_key=encrypt_key,
            verification_token=verification_token,
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
        bot_token: str | None = None,
        dm_policy: str | None = None,
        allow_from: list[str] | None = None,
        group_policy: str | None = None,
        group_allow_from: list[str] | None = None,
        groups: dict[str, Any] | None = None,
        streaming: str | None = None,
        media_max_mb: int | None = None,
        phone_id: str | None = None,
        # 飞书配置
        app_id: str | None = None,
        app_secret: str | None = None,
        encrypt_key: str | None = None,
        verification_token: str | None = None,
    ) -> ChannelConfig:
        """更新 Channel

        Args:
            channel_id: Channel 唯一标识
            name: 新的显示名称
            enabled: 是否启用
            bot_token: Telegram Bot Token
            dm_policy: DM 策略
            allow_from: DM 白名单
            group_policy: 群组策略
            group_allow_from: 群组发送者白名单
            groups: 群组配置
            streaming: 流式输出模式
            media_max_mb: 媒体文件最大大小
            phone_id: WhatsApp Phone ID
            app_id: 飞书 App ID
            app_secret: 飞书 App Secret
            encrypt_key: 飞书 Encrypt Key
            verification_token: 飞书 Verification Token

        Returns:
            更新后的 Channel 实例
        """
        channel = self.get_channel(channel_id)

        # 构建更新后的 Channel（不可变模式）
        updated_channel = ChannelConfig(
            id=channel.id,
            name=name if name is not None else channel.name,
            type=channel.type,
            enabled=enabled if enabled is not None else channel.enabled,
            bot_token=bot_token if bot_token is not None else channel.bot_token,
            dm_policy=dm_policy if dm_policy is not None else channel.dm_policy,
            allow_from=allow_from if allow_from is not None else channel.allow_from,
            group_policy=group_policy if group_policy is not None else channel.group_policy,
            group_allow_from=group_allow_from if group_allow_from is not None else channel.group_allow_from,
            groups=groups if groups is not None else channel.groups,
            streaming=streaming if streaming is not None else channel.streaming,
            media_max_mb=media_max_mb if media_max_mb is not None else channel.media_max_mb,
            phone_id=phone_id if phone_id is not None else channel.phone_id,
            app_id=app_id if app_id is not None else channel.app_id,
            app_secret=app_secret if app_secret is not None else channel.app_secret,
            encrypt_key=encrypt_key if encrypt_key is not None else channel.encrypt_key,
            verification_token=verification_token if verification_token is not None else channel.verification_token,
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

    def _sync_to_openclaw(self) -> None:
        """同步所有 Channel 到 ~/.openclaw/openclaw.json"""
        # 1. 备份现有配置
        self._backup_openclaw_config()

        config = self._read_openclaw_config()

        # 2. 构建 channels 配置
        channels_config: dict[str, Any] = {}
        for channel in self._channels.values():
            channel_key = channel.type  # 使用 type 作为 key（如 "telegram", "whatsapp"）
            channels_config[channel_key] = self._channel_to_openclaw_format(channel)

        config["channels"] = channels_config

        # 写回配置
        self._write_openclaw_config(config)

    def _channel_to_openclaw_format(self, channel: ChannelConfig) -> dict[str, Any]:
        """将 Channel 转换为 OpenClaw 格式

        Args:
            channel: Channel 实例

        Returns:
            OpenClaw 格式的配置字典
        """
        if channel.type == "telegram":
            return {
                "enabled": channel.enabled,
                "botToken": channel.bot_token,
                "dmPolicy": channel.dm_policy,
                "allowFrom": channel.allow_from,
                "groupPolicy": channel.group_policy,
                "groupAllowFrom": channel.group_allow_from,
                "groups": channel.groups,
                "streaming": channel.streaming,
                "mediaMaxMb": channel.media_max_mb,
            }
        elif channel.type == "whatsapp":
            return {
                "enabled": channel.enabled,
                "phoneId": channel.phone_id,
                "allowFrom": channel.allow_from,
                "groups": channel.groups,
            }
        elif channel.type == "discord":
            return {
                "enabled": channel.enabled,
                "allowFrom": channel.allow_from,
                "groups": channel.groups,
            }
        elif channel.type == "slack":
            return {
                "enabled": channel.enabled,
                "allowFrom": channel.allow_from,
                "groups": channel.groups,
            }
        elif channel.type == "feishu":
            return {
                "enabled": channel.enabled,
                "appId": channel.app_id,
                "appSecret": channel.app_secret,
                "encryptKey": channel.encrypt_key,
                "verificationToken": channel.verification_token,
                "allowFrom": channel.allow_from,
                "groups": channel.groups,
            }
        else:
            # 未知类型，返回基本配置
            return {
                "enabled": channel.enabled,
                "allowFrom": channel.allow_from,
                "groups": channel.groups,
            }

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
