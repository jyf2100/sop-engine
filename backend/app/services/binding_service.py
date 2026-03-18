"""Binding 配置管理服务。

REQ-0001-028: Bindings 配置支持

提供 Binding 的 CRUD 操作和优先级匹配功能。
"""
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from app.models.binding import (
    AcpConfig,
    Binding,
    BindingMatch,
    BindingsConfig,
    PeerMatch,
)


def match_binding(
    bindings: list[Binding],
    channel: str,
    peer: Optional[dict] = None,
    guild_id: Optional[str] = None,
    team_id: Optional[str] = None,
    account_id: Optional[str] = None,
) -> Optional[Binding]:
    """按优先级匹配绑定

    优先级：peer > guildId > teamId > accountId > default

    Args:
        bindings: 绑定列表
        channel: 渠道名称
        peer: 对等体信息 {"kind": "direct|group|channel", "id": "..."}
        guild_id: Discord 服务器 ID
        team_id: Slack/MSTeams 团队 ID
        account_id: 账号 ID

    Returns:
        匹配的绑定，无匹配时返回 None
    """

    def priority(binding: Binding) -> int:
        """计算绑定优先级"""
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

    def matches(binding: Binding) -> bool:
        """检查绑定是否匹配给定条件"""
        m = binding.match

        # 渠道必须匹配
        if m.channel != channel:
            return False

        # 检查各种匹配条件
        if m.peer:
            if not peer:
                return False
            if m.peer.kind != peer.get("kind"):
                return False
            if m.peer.id != peer.get("id"):
                return False
            return True

        if m.guild_id:
            if guild_id and m.guild_id == guild_id:
                return True
            return False

        if m.team_id:
            if team_id and m.team_id == team_id:
                return True
            return False

        if m.account_id:
            if account_id and m.account_id == account_id:
                return True
            # "*" 表示匹配任意账号
            if m.account_id == "*":
                return True
            return False

        # Default 绑定：只匹配 channel
        return True

    # 过滤匹配 channel 的绑定
    candidates = [b for b in bindings if b.match.channel == channel]

    # 按优先级排序
    candidates.sort(key=priority, reverse=True)

    # 返回最高优先级的匹配绑定
    for binding in candidates:
        if matches(binding):
            return binding

    return None


@dataclass
class BindingService:
    """Binding 配置管理服务

    负责 Binding 的创建、更新、删除和同步到 OpenClaw。
    """

    _bindings: dict[str, Binding] = field(default_factory=dict)
    _openclaw_config_path: Path = field(
        default_factory=lambda: Path.home() / ".openclaw" / "openclaw.json",
        repr=False,
    )

    def create_binding(
        self,
        binding_id: str,
        type: str,
        agent_id: str,
        match: BindingMatch,
        acp: Optional[AcpConfig] = None,
    ) -> Binding:
        """创建绑定

        Args:
            binding_id: 绑定唯一标识
            type: 绑定类型 (route | acp)
            agent_id: 目标 Agent ID
            match: 匹配规则
            acp: ACP 配置（仅 type="acp" 时使用）

        Returns:
            创建的 Binding 实例
        """
        if binding_id in self._bindings:
            raise ValueError(f"Binding '{binding_id}' already exists")

        binding = Binding(
            id=binding_id,
            type=type,
            agent_id=agent_id,
            match=match,
            acp=acp,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self._bindings[binding_id] = binding
        self._sync_to_openclaw()

        return binding

    def get_binding(self, binding_id: str) -> Binding:
        """获取绑定

        Args:
            binding_id: 绑定唯一标识

        Returns:
            Binding 实例

        Raises:
            KeyError: 绑定不存在
        """
        if binding_id not in self._bindings:
            raise KeyError(f"Binding '{binding_id}' not found")
        return self._bindings[binding_id]

    def list_bindings(self) -> list[Binding]:
        """列出所有绑定

        Returns:
            绑定列表
        """
        return list(self._bindings.values())

    def update_binding(
        self,
        binding_id: str,
        type: Optional[str] = None,
        agent_id: Optional[str] = None,
        match: Optional[BindingMatch] = None,
        acp: Optional[AcpConfig] = None,
    ) -> Binding:
        """更新绑定

        Args:
            binding_id: 绑定唯一标识
            type: 新的绑定类型
            agent_id: 新的目标 Agent ID
            match: 新的匹配规则
            acp: 新的 ACP 配置

        Returns:
            更新后的 Binding 实例
        """
        existing = self.get_binding(binding_id)

        updated = Binding(
            id=binding_id,
            type=type if type is not None else existing.type,
            agent_id=agent_id if agent_id is not None else existing.agent_id,
            match=match if match is not None else existing.match,
            acp=acp if acp is not None else existing.acp,
            created_at=existing.created_at,
            updated_at=datetime.utcnow(),
        )

        self._bindings[binding_id] = updated
        self._sync_to_openclaw()

        return updated

    def delete_binding(self, binding_id: str) -> None:
        """删除绑定

        Args:
            binding_id: 绑定唯一标识

        Raises:
            KeyError: 绑定不存在
        """
        if binding_id not in self._bindings:
            raise KeyError(f"Binding '{binding_id}' not found")

        del self._bindings[binding_id]
        self._sync_to_openclaw()

    def match(
        self,
        channel: str,
        peer: Optional[dict] = None,
        guild_id: Optional[str] = None,
        team_id: Optional[str] = None,
        account_id: Optional[str] = None,
    ) -> Optional[Binding]:
        """按优先级匹配绑定

        Args:
            channel: 渠道名称
            peer: 对等体信息
            guild_id: Discord 服务器 ID
            team_id: Slack/MSTeams 团队 ID
            account_id: 账号 ID

        Returns:
            匹配的绑定，无匹配时返回 None
        """
        return match_binding(
            list(self._bindings.values()),
            channel,
            peer,
            guild_id,
            team_id,
            account_id,
        )

    # ==================== OpenClaw 同步方法 ====================

    def _sync_to_openclaw(self) -> None:
        """同步绑定到 openclaw.json"""
        self._backup_openclaw_config()

        config = self._read_openclaw_config()

        # 更新 bindings
        config["bindings"] = [
            b.to_openclaw() for b in self._bindings.values()
        ]

        self._write_openclaw_config(config)

    def _backup_openclaw_config(self) -> None:
        """备份 openclaw.json"""
        if self._openclaw_config_path.exists():
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_path = self._openclaw_config_path.with_suffix(
                f".json.backup.{timestamp}"
            )
            import shutil
            shutil.copy2(self._openclaw_config_path, backup_path)

    def _read_openclaw_config(self) -> dict[str, Any]:
        """读取 OpenClaw 配置文件"""
        if self._openclaw_config_path.exists():
            try:
                content = self._openclaw_config_path.read_text()
                return json.loads(content)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _write_openclaw_config(self, config: dict[str, Any]) -> None:
        """写入 OpenClaw 配置文件"""
        self._openclaw_config_path.parent.mkdir(parents=True, exist_ok=True)
        self._openclaw_config_path.write_text(
            json.dumps(config, indent=2, ensure_ascii=False) + "\n"
        )
