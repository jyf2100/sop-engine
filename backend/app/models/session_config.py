"""Session 配置模型。

控制 OpenClaw 的会话管理，包括：
- DM 隔离策略
- 会话重置
- 存储维护
- 线程绑定
- 发送策略

对应 OpenClaw: session.*

参考:
- /Users/roc/workspace/openclaw/docs/concepts/session.md
- /Users/roc/workspace/openclaw/docs/reference/session-management-compaction.md
"""
from datetime import datetime
from typing import Any, Literal

from pydantic import Field

from .base import Base


# ==================== 类型定义 ====================

DmScope = Literal["main", "per-peer", "per-channel-peer", "per-account-channel-peer"]
ResetMode = Literal["daily", "idle"]
MaintenanceMode = Literal["warn", "enforce"]
ChatType = Literal["direct", "group", "thread"]


# ==================== 重置配置 ====================


class SessionResetConfig(Base):
    """会话重置配置

    对应 OpenClaw: session.reset

    Examples:
        # 每日 4:00 AM 重置
        {"mode": "daily", "atHour": 4}

        # 空闲 2 小时重置
        {"mode": "idle", "idleMinutes": 120}
    """
    mode: ResetMode = "daily"
    at_hour: int = Field(default=4, ge=0, le=23, description="每日重置时间（0-23，本地时区）")
    idle_minutes: int | None = Field(default=None, ge=1, description="空闲超时分钟数")

    def to_openclaw(self) -> dict:
        result: dict[str, Any] = {"mode": self.mode}
        if self.mode == "daily" or self.at_hour != 4:
            result["atHour"] = self.at_hour
        if self.idle_minutes is not None:
            result["idleMinutes"] = self.idle_minutes
        return result

    @classmethod
    def from_openclaw(cls, data: dict) -> "SessionResetConfig":
        return cls(
            mode=data.get("mode", "daily"),
            at_hour=data.get("atHour", 4),
            idle_minutes=data.get("idleMinutes"),
        )


class SessionResetByTypeConfig(Base):
    """按会话类型的重置配置

    对应 OpenClaw: session.resetByType

    可为不同会话类型设置不同的重置策略：
    - direct: 私聊
    - group: 群组
    - thread: 话题/线程
    """
    direct: SessionResetConfig | None = None
    group: SessionResetConfig | None = None
    thread: SessionResetConfig | None = None

    def to_openclaw(self) -> dict:
        result: dict[str, Any] = {}
        if self.direct:
            result["direct"] = self.direct.to_openclaw()
        if self.group:
            result["group"] = self.group.to_openclaw()
        if self.thread:
            result["thread"] = self.thread.to_openclaw()
        return result

    @classmethod
    def from_openclaw(cls, data: dict) -> "SessionResetByTypeConfig":
        return cls(
            direct=SessionResetConfig.from_openclaw(data["direct"]) if "direct" in data else None,
            group=SessionResetConfig.from_openclaw(data["group"]) if "group" in data else None,
            thread=SessionResetConfig.from_openclaw(data["thread"]) if "thread" in data else None,
        )


class SessionResetByChannelConfig(Base):
    """按渠道的重置配置

    对应 OpenClaw: session.resetByChannel
    """
    channels: dict[str, SessionResetConfig] = Field(default_factory=dict)

    def to_openclaw(self) -> dict:
        return {k: v.to_openclaw() for k, v in self.channels.items()}


# ==================== 维护配置 ====================


class SessionMaintenanceConfig(Base):
    """会话维护配置

    对应 OpenClaw: session.maintenance

    控制 sessions.json 和 transcript 文件的自动维护。
    """
    mode: MaintenanceMode = "warn"
    prune_after: str = "30d"
    max_entries: int = Field(default=500, ge=1, description="最大会话条目数")
    rotate_bytes: str = "10mb"
    reset_archive_retention: str | bool = "30d"
    max_disk_bytes: str | None = None
    high_water_bytes: str | None = None

    def to_openclaw(self) -> dict:
        result: dict[str, Any] = {
            "mode": self.mode,
            "pruneAfter": self.prune_after,
            "maxEntries": self.max_entries,
            "rotateBytes": self.rotate_bytes,
        }
        if self.reset_archive_retention is not None:
            result["resetArchiveRetention"] = self.reset_archive_retention
        if self.max_disk_bytes:
            result["maxDiskBytes"] = self.max_disk_bytes
        if self.high_water_bytes:
            result["highWaterBytes"] = self.high_water_bytes
        return result

    @classmethod
    def from_openclaw(cls, data: dict) -> "SessionMaintenanceConfig":
        return cls(
            mode=data.get("mode", "warn"),
            prune_after=data.get("pruneAfter", "30d"),
            max_entries=data.get("maxEntries", 500),
            rotate_bytes=data.get("rotateBytes", "10mb"),
            reset_archive_retention=data.get("resetArchiveRetention", "30d"),
            max_disk_bytes=data.get("maxDiskBytes"),
            high_water_bytes=data.get("highWaterBytes"),
        )


# ==================== 线程绑定配置 ====================


class SessionThreadBindingsConfig(Base):
    """线程绑定配置

    对应 OpenClaw: session.threadBindings
    """
    enabled: bool = True
    idle_hours: int = Field(default=24, ge=0, description="不活动自动解绑小时数，0 禁用")
    max_age_hours: int = Field(default=0, ge=0, description="硬性最大存活小时数，0 禁用")

    def to_openclaw(self) -> dict:
        return {
            "enabled": self.enabled,
            "idleHours": self.idle_hours,
            "maxAgeHours": self.max_age_hours,
        }

    @classmethod
    def from_openclaw(cls, data: dict) -> "SessionThreadBindingsConfig":
        return cls(
            enabled=data.get("enabled", True),
            idle_hours=data.get("idleHours", 24),
            max_age_hours=data.get("maxAgeHours", 0),
        )


# ==================== 发送策略配置 ====================


class SendPolicyMatch(Base):
    """发送策略匹配规则"""
    channel: str | None = None
    chat_type: str | None = None  # direct | group | channel
    key_prefix: str | None = None
    raw_key_prefix: str | None = None


class SendPolicyRule(Base):
    """发送策略规则"""
    action: Literal["allow", "deny"]
    match: SendPolicyMatch


class SessionSendPolicyConfig(Base):
    """发送策略配置

    对应 OpenClaw: session.sendPolicy
    """
    rules: list[SendPolicyRule] = Field(default_factory=list)
    default: Literal["allow", "deny"] = "allow"

    def to_openclaw(self) -> dict:
        return {
            "rules": [
                {
                    "action": rule.action,
                    "match": rule.match.model_dump(exclude_none=True)
                }
                for rule in self.rules
            ],
            "default": self.default,
        }


# ==================== Agent 间通信配置 ====================


class SessionAgentToAgentConfig(Base):
    """Agent 间通信配置

    对应 OpenClaw: session.agentToAgent
    """
    max_ping_pong_turns: int = Field(default=5, ge=0, description="最大乒乓交互轮数")

    def to_openclaw(self) -> dict:
        return {"maxPingPongTurns": self.max_ping_pong_turns}


# ==================== 主配置模型 ====================


class SessionConfig(Base):
    """Session 配置模型

    对应 OpenClaw: session.*

    完整的会话管理配置。
    """

    # === DM 隔离策略 ===
    dm_scope: DmScope = "main"

    # === 身份映射 ===
    identity_links: dict[str, list[str]] = Field(default_factory=dict)

    # === 重置策略 ===
    reset: SessionResetConfig = Field(default_factory=SessionResetConfig)
    reset_by_type: SessionResetByTypeConfig | None = None
    reset_by_channel: SessionResetByChannelConfig | None = None
    reset_triggers: list[str] = Field(default_factory=lambda: ["/new", "/reset"])

    # === 存储配置 ===
    store: str = "~/.openclaw/agents/{agentId}/sessions/sessions.json"
    main_key: str = "main"
    parent_fork_max_tokens: int = Field(default=100000, ge=0)

    # === 维护配置 ===
    maintenance: SessionMaintenanceConfig | None = None

    # === 线程绑定 ===
    thread_bindings: SessionThreadBindingsConfig | None = None

    # === Agent 间通信 ===
    agent_to_agent: SessionAgentToAgentConfig | None = None

    # === 发送策略 ===
    send_policy: SessionSendPolicyConfig | None = None

    # === 元数据 ===
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def to_openclaw(self) -> dict:
        """转换为 OpenClaw 配置格式（camelCase）"""
        result: dict[str, Any] = {}

        # 基础字段
        result["dmScope"] = self.dm_scope

        # 身份映射
        if self.identity_links:
            result["identityLinks"] = self.identity_links

        # 重置策略
        result["reset"] = self.reset.to_openclaw()
        if self.reset_by_type:
            result["resetByType"] = self.reset_by_type.to_openclaw()
        if self.reset_by_channel:
            result["resetByChannel"] = self.reset_by_channel.to_openclaw()

        # 重置触发器
        if self.reset_triggers:
            result["resetTriggers"] = self.reset_triggers

        # 存储配置
        result["store"] = self.store
        result["mainKey"] = self.main_key
        result["parentForkMaxTokens"] = self.parent_fork_max_tokens

        # 维护配置
        if self.maintenance:
            result["maintenance"] = self.maintenance.to_openclaw()

        # 线程绑定
        if self.thread_bindings:
            result["threadBindings"] = self.thread_bindings.to_openclaw()

        # Agent 间通信
        if self.agent_to_agent:
            result["agentToAgent"] = self.agent_to_agent.to_openclaw()

        # 发送策略
        if self.send_policy:
            result["sendPolicy"] = self.send_policy.to_openclaw()

        return result

    @classmethod
    def from_openclaw(cls, data: dict) -> "SessionConfig":
        """从 OpenClaw 配置格式解析"""
        # 解析嵌套配置
        reset = None
        if "reset" in data:
            reset = SessionResetConfig.from_openclaw(data["reset"])
        else:
            reset = SessionResetConfig()

        reset_by_type = None
        if "resetByType" in data:
            reset_by_type = SessionResetByTypeConfig.from_openclaw(data["resetByType"])

        maintenance = None
        if "maintenance" in data:
            maintenance = SessionMaintenanceConfig.from_openclaw(data["maintenance"])

        thread_bindings = None
        if "threadBindings" in data:
            thread_bindings = SessionThreadBindingsConfig.from_openclaw(data["threadBindings"])

        return cls(
            dm_scope=data.get("dmScope", "main"),
            identity_links=data.get("identityLinks", {}),
            reset=reset,
            reset_by_type=reset_by_type,
            reset_triggers=data.get("resetTriggers", ["/new", "/reset"]),
            store=data.get("store", "~/.openclaw/agents/{agentId}/sessions/sessions.json"),
            main_key=data.get("mainKey", "main"),
            parent_fork_max_tokens=data.get("parentForkMaxTokens", 100000),
            maintenance=maintenance,
            thread_bindings=thread_bindings,
        )
