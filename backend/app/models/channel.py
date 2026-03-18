"""Channel 配置模型。

用于管理 OpenClaw 的 Channel 配置（Telegram、WhatsApp、Feishu 等）。
完全对齐 OpenClaw 官方配置规范。

参考:
- /Users/roc/workspace/openclaw/docs/gateway/configuration-reference.md
- /Users/roc/workspace/openclaw/docs/channels/*.md
"""
from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from .base import Base

# ==================== 类型定义 ====================

ChannelType = Literal["telegram", "whatsapp", "discord", "slack", "feishu"]
DmPolicy = Literal["pairing", "allowlist", "open", "disabled"]
GroupPolicy = Literal["open", "allowlist", "disabled"]
StreamingMode = Literal["off", "partial", "block"]
ConnectionMode = Literal["websocket", "webhook"]
FeishuDomain = Literal["feishu", "lark"]
ReactionNotificationMode = Literal["own", "all", "off"]
ChunkMode = Literal["paragraph", "sentence", "word"]


# ==================== 子模型 ====================


class NetworkConfig(Base):
    """网络配置

    对应 OpenClaw: channels.<type>.network
    """
    auto_select_family: bool | None = Field(default=None, alias="autoSelectFamily")
    dns_result_order: str | None = Field(default=None, alias="dnsResultOrder")

    class Config:
        populate_by_name = True


class AckReactionConfig(Base):
    """确认反应配置

    对应 OpenClaw: channels.<type>.ackReaction
    """
    emoji: str = "👀"
    scope: Literal["group-mentions", "group-all", "direct", "all"] = "group-mentions"


class ChannelAccount(Base):
    """Channel 账号配置

    用于多账号场景，每个账号有独立的认证和配置。

    对应 OpenClaw: channels.<type>.accounts.<account_id>
    """
    name: str | None = None
    enabled: bool = True

    # Telegram 专属
    bot_token: str | None = Field(default=None, alias="botToken")

    # Feishu 专属
    app_id: str | None = Field(default=None, alias="appId")
    app_secret: str | None = Field(default=None, alias="appSecret")
    encrypt_key: str | None = Field(default=None, alias="encryptKey")
    verification_token: str | None = Field(default=None, alias="verificationToken")
    domain: FeishuDomain | None = None

    # WhatsApp 专属
    phone_id: str | None = Field(default=None, alias="phoneId")

    class Config:
        populate_by_name = True

    def to_openclaw(self) -> dict[str, Any]:
        """转换为 OpenClaw 格式（camelCase）"""
        result: dict[str, Any] = {"enabled": self.enabled}
        if self.name:
            result["name"] = self.name
        if self.bot_token:
            result["botToken"] = self.bot_token
        if self.app_id:
            result["appId"] = self.app_id
        if self.app_secret:
            result["appSecret"] = self.app_secret
        if self.encrypt_key:
            result["encryptKey"] = self.encrypt_key
        if self.verification_token:
            result["verificationToken"] = self.verification_token
        if self.domain:
            result["domain"] = self.domain
        if self.phone_id:
            result["phoneId"] = self.phone_id
        return result


class GroupConfig(Base):
    """群组配置

    对应 OpenClaw: channels.<type>.groups.<groupId>
    """
    enabled: bool = True
    require_mention: bool = True
    allow_from: list[str] = Field(default_factory=list, alias="allowFrom")

    class Config:
        populate_by_name = True


class ChannelConfig(Base):
    """Channel 配置模型

    存储 OpenClaw Channel 的配置信息。
    所有配置变更通过 SOP Engine 进行，OpenClaw 被动接收。

    完全对齐 OpenClaw 官方配置规范。
    """

    id: str  # 唯一标识，如 "telegram-main"
    name: str  # 显示名称
    type: ChannelType  # 平台类型
    enabled: bool = True

    # ==================== 多账号支持 ====================
    accounts: dict[str, ChannelAccount] | None = None
    default_account: str | None = Field(default=None, alias="defaultAccount")

    # ==================== 通用配置 ====================
    dm_policy: DmPolicy = Field(default="pairing", alias="dmPolicy")
    allow_from: list[str] = Field(default_factory=list, alias="allowFrom")
    group_policy: GroupPolicy = Field(default="allowlist", alias="groupPolicy")
    group_allow_from: list[str] = Field(default_factory=list, alias="groupAllowFrom")
    groups: dict[str, Any] = Field(default_factory=dict)

    # 流式配置
    streaming: StreamingMode = "partial"
    block_streaming: bool | None = Field(default=None, alias="blockStreaming")

    # 消息限制
    text_chunk_limit: int | None = Field(default=None, alias="textChunkLimit")
    media_max_mb: int = Field(default=100, alias="mediaMaxMb")
    history_limit: int | None = Field(default=None, alias="historyLimit")

    # 通用高级配置
    config_writes: bool | None = Field(default=None, alias="configWrites")

    # ==================== Telegram 专属配置 ====================
    bot_token: str | None = Field(default=None, alias="botToken")

    # 反应通知
    reaction_notifications: ReactionNotificationMode | None = Field(
        default=None, alias="reactionNotifications"
    )
    reaction_allowlist: list[str] | None = Field(default=None, alias="reactionAllowlist")

    # 历史消息
    dm_history_limit: int | None = Field(default=None, alias="dmHistoryLimit")

    # Webhook 配置
    webhook_url: str | None = Field(default=None, alias="webhookUrl")
    webhook_secret: str | None = Field(default=None, alias="webhookSecret")

    # 网络配置
    network: NetworkConfig | None = None
    proxy: str | None = None

    # 超时和重试
    timeout_seconds: int | None = Field(default=None, alias="timeoutSeconds")

    # 链接预览
    link_preview: bool | None = Field(default=None, alias="linkPreview")

    # 回复模式
    reply_to_mode: str | None = Field(default=None, alias="replyToMode")

    # 自定义命令
    custom_commands: dict[str, Any] | None = Field(default=None, alias="customCommands")

    # DM 配置
    dms: dict[str, Any] | None = None

    # ==================== WhatsApp 专属配置 ====================
    phone_id: str | None = Field(default=None, alias="phoneId")

    # 确认反应
    ack_reaction: AckReactionConfig | None = Field(default=None, alias="ackReaction")

    # 已读回执
    send_read_receipts: bool | None = Field(default=None, alias="sendReadReceipts")

    # 分块模式
    chunk_mode: ChunkMode | None = Field(default=None, alias="chunkMode")

    # 防抖
    debounce_ms: int | None = Field(default=None, alias="debounceMs")

    # 自聊模式
    self_chat_mode: bool | None = Field(default=None, alias="selfChatMode")

    # ==================== Feishu 专属配置 ====================
    app_id: str | None = Field(default=None, alias="appId")
    app_secret: str | None = Field(default=None, alias="appSecret")
    encrypt_key: str | None = Field(default=None, alias="encryptKey")
    verification_token: str | None = Field(default=None, alias="verificationToken")

    # 域名（国内版 feishu 或国际版 lark）
    domain: FeishuDomain | None = None

    # 连接模式
    connection_mode: ConnectionMode | None = Field(default=None, alias="connectionMode")

    # Bot 名称
    bot_name: str | None = Field(default=None, alias="botName")

    # 输入提示
    typing_indicator: bool | None = Field(default=None, alias="typingIndicator")

    # 发送者名称解析
    resolve_sender_names: bool | None = Field(default=None, alias="resolveSenderNames")

    # Webhook 配置
    webhook_host: str | None = Field(default=None, alias="webhookHost")
    webhook_port: int | None = Field(default=None, alias="webhookPort")
    webhook_path: str | None = Field(default=None, alias="webhookPath")

    # ==================== 元数据 ====================
    created_at: datetime | None = Field(default=None, alias="createdAt")
    updated_at: datetime | None = Field(default=None, alias="updatedAt")

    class Config:
        populate_by_name = True

    def to_openclaw(self) -> dict[str, Any]:
        """转换为 OpenClaw 格式（camelCase）

        Returns:
            OpenClaw 格式的配置字典
        """
        result: dict[str, Any] = {"enabled": self.enabled}

        # 多账号支持
        if self.accounts:
            result["accounts"] = {
                acc_id: acc.to_openclaw() for acc_id, acc in self.accounts.items()
            }
        if self.default_account:
            result["defaultAccount"] = self.default_account

        # 通用配置
        result["dmPolicy"] = self.dm_policy
        result["allowFrom"] = self.allow_from
        result["groupPolicy"] = self.group_policy
        result["groupAllowFrom"] = self.group_allow_from
        if self.groups:
            result["groups"] = self.groups

        # 流式配置
        result["streaming"] = self.streaming
        if self.block_streaming is not None:
            result["blockStreaming"] = self.block_streaming

        # 消息限制
        if self.text_chunk_limit is not None:
            result["textChunkLimit"] = self.text_chunk_limit
        result["mediaMaxMb"] = self.media_max_mb
        if self.history_limit is not None:
            result["historyLimit"] = self.history_limit

        # 通用高级配置
        if self.config_writes is not None:
            result["configWrites"] = self.config_writes

        # 根据平台类型添加专属配置
        if self.type == "telegram":
            result.update(self._telegram_to_openclaw())
        elif self.type == "whatsapp":
            result.update(self._whatsapp_to_openclaw())
        elif self.type == "feishu":
            result.update(self._feishu_to_openclaw())

        return result

    def _telegram_to_openclaw(self) -> dict[str, Any]:
        """Telegram 专属配置转换"""
        result: dict[str, Any] = {}

        # 基础认证
        if self.bot_token:
            result["botToken"] = self.bot_token

        # 反应通知
        if self.reaction_notifications is not None:
            result["reactionNotifications"] = self.reaction_notifications
        if self.reaction_allowlist is not None:
            result["reactionAllowlist"] = self.reaction_allowlist

        # 历史消息
        if self.dm_history_limit is not None:
            result["dmHistoryLimit"] = self.dm_history_limit

        # Webhook
        if self.webhook_url is not None:
            result["webhookUrl"] = self.webhook_url
        if self.webhook_secret is not None:
            result["webhookSecret"] = self.webhook_secret

        # 网络
        if self.network is not None:
            result["network"] = {
                "autoSelectFamily": self.network.auto_select_family,
                "dnsResultOrder": self.network.dns_result_order,
            }
        if self.proxy is not None:
            result["proxy"] = self.proxy

        # 超时
        if self.timeout_seconds is not None:
            result["timeoutSeconds"] = self.timeout_seconds

        # 链接预览
        if self.link_preview is not None:
            result["linkPreview"] = self.link_preview

        # 回复模式
        if self.reply_to_mode is not None:
            result["replyToMode"] = self.reply_to_mode

        # 自定义命令
        if self.custom_commands is not None:
            result["customCommands"] = self.custom_commands

        # DM 配置
        if self.dms is not None:
            result["dms"] = self.dms

        return result

    def _whatsapp_to_openclaw(self) -> dict[str, Any]:
        """WhatsApp 专属配置转换"""
        result: dict[str, Any] = {}

        # 基础认证
        if self.phone_id:
            result["phoneId"] = self.phone_id

        # 确认反应
        if self.ack_reaction is not None:
            result["ackReaction"] = {
                "emoji": self.ack_reaction.emoji,
                "scope": self.ack_reaction.scope,
            }

        # 已读回执
        if self.send_read_receipts is not None:
            result["sendReadReceipts"] = self.send_read_receipts

        # 分块模式
        if self.chunk_mode is not None:
            result["chunkMode"] = self.chunk_mode

        # 防抖
        if self.debounce_ms is not None:
            result["debounceMs"] = self.debounce_ms

        # 自聊模式
        if self.self_chat_mode is not None:
            result["selfChatMode"] = self.self_chat_mode

        return result

    def _feishu_to_openclaw(self) -> dict[str, Any]:
        """Feishu 专属配置转换"""
        result: dict[str, Any] = {}

        # 基础认证
        if self.app_id:
            result["appId"] = self.app_id
        if self.app_secret:
            result["appSecret"] = self.app_secret
        if self.encrypt_key:
            result["encryptKey"] = self.encrypt_key
        if self.verification_token:
            result["verificationToken"] = self.verification_token

        # 域名
        if self.domain is not None:
            result["domain"] = self.domain

        # 连接模式
        if self.connection_mode is not None:
            result["connectionMode"] = self.connection_mode

        # Bot 名称
        if self.bot_name is not None:
            result["botName"] = self.bot_name

        # 输入提示
        if self.typing_indicator is not None:
            result["typingIndicator"] = self.typing_indicator

        # 发送者名称解析
        if self.resolve_sender_names is not None:
            result["resolveSenderNames"] = self.resolve_sender_names

        # Webhook
        if self.webhook_host is not None:
            result["webhookHost"] = self.webhook_host
        if self.webhook_port is not None:
            result["webhookPort"] = self.webhook_port
        if self.webhook_path is not None:
            result["webhookPath"] = self.webhook_path

        return result
