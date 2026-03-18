"""Messages 配置模型。

控制 OpenClaw 的消息处理，包括：
- 消息队列
- 入站防抖
- 响应前缀
- 确认反应

对应 OpenClaw: messages.*

参考:
- /Users/roc/workspace/openclaw/docs/concepts/messages.md
- /Users/roc/workspace/openclaw/docs/concepts/queue.md
"""
from typing import Any, Literal

from pydantic import Field

from .base import Base


# ==================== 类型定义 ====================

QueueMode = Literal["steer", "followup", "collect", "steer-backlog", "queue", "interrupt"]
AckReactionScope = Literal["group-mentions", "group-all", "direct", "all"]
DropPolicy = Literal["old", "new", "summarize"]


# ==================== 队列配置 ====================


class MessageQueueConfig(Base):
    """消息队列配置

    对应 OpenClaw: messages.queue

    控制并发消息的处理策略。

    模式说明:
    - steer: 立即注入当前运行（在下一个工具边界取消待处理工具调用）
    - followup: 当前运行结束后排队等待下一轮
    - collect: 将所有排队消息合并为单个 followup 轮次（默认）
    - steer-backlog: 立即转向 + 保留消息用于 followup
    - interrupt: 中止当前运行，运行最新消息
    - queue: steer 的别名
    """
    mode: QueueMode = "collect"
    debounce_ms: int = Field(default=1000, ge=0, description="followup 前等待静默的毫秒数")
    cap: int = Field(default=20, ge=1, description="每会话最大排队消息数")
    drop: DropPolicy = "summarize"  # 溢出策略
    by_channel: dict[str, QueueMode] = Field(default_factory=dict)  # 按渠道覆盖

    def to_openclaw(self) -> dict:
        result: dict[str, Any] = {
            "mode": self.mode,
            "debounceMs": self.debounce_ms,
            "cap": self.cap,
            "drop": self.drop,
        }
        if self.by_channel:
            result["byChannel"] = self.by_channel
        return result

    @classmethod
    def from_openclaw(cls, data: dict) -> "MessageQueueConfig":
        return cls(
            mode=data.get("mode", "collect"),
            debounce_ms=data.get("debounceMs", 1000),
            cap=data.get("cap", 20),
            drop=data.get("drop", "summarize"),
            by_channel=data.get("byChannel", {}),
        )


# ==================== 入站防抖配置 ====================


class InboundConfig(Base):
    """入站防抖配置

    对应 OpenClaw: messages.inbound

    将同一发送者的快速连续消息批量为单个 Agent 轮次。
    """
    debounce_ms: int = Field(default=0, ge=0, description="防抖毫秒数，0 禁用")

    def to_openclaw(self) -> dict:
        return {"debounceMs": self.debounce_ms}

    @classmethod
    def from_openclaw(cls, data: dict) -> "InboundConfig":
        return cls(debounce_ms=data.get("debounceMs", 0))


# ==================== 响应前缀配置 ====================


class ResponsePrefixConfig(Base):
    """响应前缀配置

    对应 OpenClaw: messages.responsePrefix

    支持模板变量:
    - {model} - 短模型名
    - {modelFull} - 完整模型标识
    - {provider} - 提供商名
    - {thinkingLevel} - 思考级别
    - {identity.name} - Agent 身份名称

    特殊值:
    - "auto" - 自动生成为 [{identity.name}]
    - "" - 禁用
    """
    prefix: str | None = None  # None = "auto"

    def to_openclaw(self) -> str | None:
        return self.prefix

    @classmethod
    def from_openclaw(cls, data: str | None) -> "ResponsePrefixConfig":
        return cls(prefix=data)


# ==================== 确认反应配置 ====================


class AckReactionConfig(Base):
    """确认反应配置

    对应 OpenClaw: messages.ackReaction, ackReactionScope, removeAckAfterReply

    Agent 收到消息后立即发送确认反应。
    """
    emoji: str = "👀"  # 确认反应 emoji
    scope: AckReactionScope = "group-mentions"
    remove_after_reply: bool = False

    def to_openclaw(self) -> dict:
        return {
            "ackReaction": self.emoji,
            "ackReactionScope": self.scope,
            "removeAckAfterReply": self.remove_after_reply,
        }

    @classmethod
    def from_openclaw(cls, data: dict) -> "AckReactionConfig":
        return cls(
            emoji=data.get("ackReaction", "👀"),
            scope=data.get("ackReactionScope", "group-mentions"),
            remove_after_reply=data.get("removeAckAfterReply", False),
        )


# ==================== 主配置模型 ====================


class MessagesConfig(Base):
    """Messages 配置模型

    对应 OpenClaw: messages.*

    完整的消息处理配置。
    """

    # === 消息队列 ===
    queue: MessageQueueConfig = Field(default_factory=MessageQueueConfig)

    # === 入站配置 ===
    inbound: InboundConfig = Field(default_factory=InboundConfig)

    # === 响应格式 ===
    response_prefix: ResponsePrefixConfig | None = None

    # === 确认反应 ===
    ack_reaction: AckReactionConfig | None = None

    def to_openclaw(self) -> dict:
        """转换为 OpenClaw 配置格式（camelCase）"""
        result: dict[str, Any] = {}

        # 队列配置
        result["queue"] = self.queue.to_openclaw()

        # 入站配置
        result["inbound"] = self.inbound.to_openclaw()

        # 响应前缀
        if self.response_prefix:
            prefix = self.response_prefix.to_openclaw()
            if prefix is not None:
                result["responsePrefix"] = prefix

        # 确认反应
        if self.ack_reaction:
            result.update(self.ack_reaction.to_openclaw())

        return result

    @classmethod
    def from_openclaw(cls, data: dict) -> "MessagesConfig":
        """从 OpenClaw 配置格式解析"""
        queue = MessageQueueConfig.from_openclaw(data.get("queue", {}))
        inbound = InboundConfig.from_openclaw(data.get("inbound", {}))
        response_prefix = None
        if "responsePrefix" in data:
            response_prefix = ResponsePrefixConfig.from_openclaw(data["responsePrefix"])

        ack_reaction = None
        if "ackReaction" in data:
            ack_reaction = AckReactionConfig.from_openclaw(data)

        return cls(
            queue=queue,
            inbound=inbound,
            response_prefix=response_prefix,
            ack_reaction=ack_reaction,
        )
