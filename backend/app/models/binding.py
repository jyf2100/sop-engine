"""Bindings 配置模型。

REQ-0001-028: Bindings 配置支持

控制多 Agent 路由，实现灵活的消息分发规则。

对应 OpenClaw: bindings[]

参考:
- /Users/roc/workspace/openclaw/docs/concepts/bindings.md
"""
from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import Field

from .base import Base


# ==================== 类型定义 ====================

BindingType = Literal["route", "acp"]
PeerKind = Literal["direct", "group", "channel"]
AcpMode = Literal["persistent", "ephemeral"]
AcpBackend = Literal["acpx"]


# ==================== 对等体匹配配置 ====================


class PeerMatch(Base):
    """对等体匹配配置

    用于匹配特定的用户、群组或频道。

    对应 OpenClaw: bindings[].match.peer
    """

    kind: PeerKind  # direct | group | channel
    id: str  # 对等体 ID

    def to_openclaw(self) -> dict:
        return {
            "kind": self.kind,
            "id": self.id,
        }


class BindingMatch(Base):
    """绑定匹配规则

    对应 OpenClaw: bindings[].match

    匹配优先级（从高到低）：
    1. peer
    2. guildId
    3. teamId
    4. accountId (精确，无 peer/guild/team)
    5. accountId: "*" (渠道范围)
    6. 默认
    """

    channel: str  # 渠道名: telegram, whatsapp, discord, etc.
    account_id: Optional[str] = None  # 账号 ID，"*" 表示任意账号
    peer: Optional[PeerMatch] = None  # 对等体匹配
    guild_id: Optional[str] = None  # Discord 服务器 ID
    team_id: Optional[str] = None  # Slack/MSTeams 团队 ID

    def to_openclaw(self) -> dict:
        result: dict[str, Any] = {"channel": self.channel}
        if self.account_id is not None:
            result["accountId"] = self.account_id
        if self.peer:
            result["peer"] = self.peer.to_openclaw()
        if self.guild_id:
            result["guildId"] = self.guild_id
        if self.team_id:
            result["teamId"] = self.team_id
        return result


# ==================== ACP 配置 ====================


class AcpConfig(Base):
    """ACP 绑定配置

    对应 OpenClaw: bindings[].acp (仅 type="acp" 时使用)
    """

    mode: AcpMode = "persistent"  # persistent | ephemeral
    label: Optional[str] = None  # 会话标签
    cwd: Optional[str] = None  # 工作目录
    backend: AcpBackend = "acpx"  # 后端类型

    def to_openclaw(self) -> dict:
        result: dict[str, Any] = {
            "mode": self.mode,
            "backend": self.backend,
        }
        if self.label:
            result["label"] = self.label
        if self.cwd:
            result["cwd"] = self.cwd
        return result


# ==================== 绑定条目 ====================


class Binding(Base):
    """绑定条目

    对应 OpenClaw: bindings[]
    """

    id: Optional[str] = None
    type: BindingType = "route"  # route | acp
    agent_id: str
    match: BindingMatch
    acp: Optional[AcpConfig] = None  # ACP 配置（仅 type="acp" 时使用）

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_openclaw(self) -> dict:
        result: dict[str, Any] = {
            "type": self.type,
            "agentId": self.agent_id,
            "match": self.match.to_openclaw(),
        }
        if self.acp and self.type == "acp":
            result["acp"] = self.acp.to_openclaw()
        return result


# ==================== 主模型 ====================


class BindingsConfig(Base):
    """Bindings 配置模型

    对应 OpenClaw: bindings[]

    管理多 Agent 路由配置。

    匹配优先级（从高到低）：
    1. match.peer
    2. match.guildId
    3. match.teamId
    4. match.accountId (精确，无 peer/guild/team)
    5. match.accountId: "*" (渠道范围)
    6. 默认 Agent

    在每个层级内，第一个匹配的绑定获胜。
    """

    bindings: list[Binding] = Field(default_factory=list)

    # === 元数据 ===
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # ==================== 序列化方法 ====================

    def to_openclaw(self) -> list[dict]:
        """转换为 OpenClaw 配置格式"""
        return [b.to_openclaw() for b in self.bindings]

    @classmethod
    def from_openclaw(cls, data: list[dict]) -> "BindingsConfig":
        """从 OpenClaw 配置格式解析"""
        bindings = []
        for entry in data:
            # 解析 match
            match_data = entry.get("match", {})
            peer = None
            if "peer" in match_data:
                peer = PeerMatch(
                    kind=match_data["peer"]["kind"],
                    id=match_data["peer"]["id"],
                )
            match = BindingMatch(
                channel=match_data.get("channel", ""),
                account_id=match_data.get("accountId"),
                peer=peer,
                guild_id=match_data.get("guildId"),
                team_id=match_data.get("teamId"),
            )

            # 解析 acp
            acp = None
            if "acp" in entry:
                acp_data = entry["acp"]
                acp = AcpConfig(
                    mode=acp_data.get("mode", "persistent"),
                    label=acp_data.get("label"),
                    cwd=acp_data.get("cwd"),
                    backend=acp_data.get("backend", "acpx"),
                )

            bindings.append(Binding(
                id=entry.get("id"),
                type=entry.get("type", "route"),
                agent_id=entry.get("agentId", ""),
                match=match,
                acp=acp,
            ))

        return cls(bindings=bindings)
