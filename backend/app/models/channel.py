"""Channel 配置模型。

用于管理 OpenClaw 的 Channel 配置（Telegram、WhatsApp 等）。
"""
from datetime import datetime
from typing import Any, Literal

from .base import Base

ChannelType = Literal["telegram", "whatsapp", "discord", "slack", "feishu"]
DmPolicy = Literal["pairing", "allowlist", "open", "disabled"]
GroupPolicy = Literal["open", "allowlist", "disabled"]
StreamingMode = Literal["off", "partial", "block"]


class ChannelConfig(Base):
    """Channel 配置模型

    存储 OpenClaw Channel 的配置信息。
    所有配置变更通过 SOP Engine 进行，OpenClaw 被动接收。
    """

    id: str  # 唯一标识，如 "telegram-main"
    name: str  # 显示名称
    type: ChannelType  # 平台类型
    enabled: bool = True

    # Telegram 配置
    bot_token: str | None = None
    dm_policy: DmPolicy = "pairing"
    allow_from: list[str] = []  # DM 白名单（用户 ID）
    group_policy: GroupPolicy = "allowlist"
    group_allow_from: list[str] = []  # 群组发送者允许列表
    groups: dict[str, Any] = {}  # 群组配置 {groupId: {requireMention, allowFrom}}
    streaming: StreamingMode = "partial"
    media_max_mb: int = 100

    # WhatsApp 配置
    phone_id: str | None = None

    # 飞书配置
    app_id: str | None = None
    app_secret: str | None = None
    encrypt_key: str | None = None
    verification_token: str | None = None

    # 元数据
    created_at: datetime | None = None
    updated_at: datetime | None = None
