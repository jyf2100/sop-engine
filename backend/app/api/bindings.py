"""Bindings API 端点。

REQ-0001-028: Bindings 配置支持

提供 Binding 的 REST API。
"""
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException

from app.models.binding import (
    AcpConfig,
    Binding,
    BindingMatch,
    PeerMatch,
)


@dataclass
class BindingService:
    """Binding 服务（简化版，直接在 API 中使用）"""
    _bindings: dict[str, Binding] = field(default_factory=dict)
    _openclaw_config_path: Path = field(
        default_factory=lambda: Path.home() / ".openclaw" / "openclaw.json",
        repr=False,
    )

    def _sync_to_openclaw(self) -> None:
        """同步绑定到 openclaw.json"""
        import json
        import shutil

        # 备份
        if self._openclaw_config_path.exists():
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_path = self._openclaw_config_path.with_suffix(
                f".json.backup.{timestamp}"
            )
            shutil.copy2(self._openclaw_config_path, backup_path)

        # 读取现有配置
        config = {}
        if self._openclaw_config_path.exists():
            try:
                config = json.loads(self._openclaw_config_path.read_text())
            except (json.JSONDecodeError, IOError):
                pass

        # 更新 bindings
        config["bindings"] = [
            b.to_openclaw() for b in self._bindings.values()
        ]

        # 写入
        self._openclaw_config_path.parent.mkdir(parents=True, exist_ok=True)
        self._openclaw_config_path.write_text(
            json.dumps(config, indent=2, ensure_ascii=False) + "\n"
        )


# 全局服务实例
_binding_service = BindingService()


# ==================== API 路由 ====================


router = APIRouter(prefix="/bindings", tags=["bindings"])


@router.get("/")
async def list_bindings() -> list[dict[str, Any]]:
    """列出所有绑定

    Returns:
        绑定列表
    """
    return [binding.model_dump() for binding in _binding_service._bindings.values()]


@router.get("/{binding_id}")
async def get_binding(binding_id: str) -> dict[str, Any]:
    """获取单个绑定

    Args:
        binding_id: 绑定 ID

    Returns:
        绑定详情

    Raises:
        404: 绑定不存在
    """
    if binding_id not in _binding_service._bindings:
        raise HTTPException(status_code=404, detail=f"Binding '{binding_id}' not found")

    return _binding_service._bindings[binding_id].model_dump()


@router.post("/")
async def create_binding(
    id: str,
    type: str = "route",
    agent_id: str = "",
    match: Optional[dict[str, Any]] = None,
    acp: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """创建绑定

    Args:
        id: 绑定 ID
        type: 绑定类型 (route | acp)
        agent_id: 目标 Agent ID
        match: 匹配规则
        acp: ACP 配置（仅 type="acp" 时使用）

    Returns:
        创建的绑定

    Raises:
        400: 绑定已存在
    """
    if id in _binding_service._bindings:
        raise HTTPException(status_code=400, detail=f"Binding '{id}' already exists")

    # 解析 match
    match_obj = None
    if match:
        peer_obj = None
        if "peer" in match:
            peer_obj = PeerMatch(
                kind=match["peer"]["kind"],
                id=match["peer"]["id"],
            )
        match_obj = BindingMatch(
            channel=match.get("channel", ""),
            account_id=match.get("accountId"),
            peer=peer_obj,
            guild_id=match.get("guildId"),
            team_id=match.get("teamId"),
        )
    else:
        match_obj = BindingMatch(channel="")

    # 解析 acp
    acp_obj = None
    if acp:
        acp_obj = AcpConfig(
            mode=acp.get("mode", "persistent"),
            label=acp.get("label"),
            cwd=acp.get("cwd"),
            backend=acp.get("backend", "acpx"),
        )

    binding = Binding(
        id=id,
        type=type,
        agent_id=agent_id,
        match=match_obj,
        acp=acp_obj,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    _binding_service._bindings[id] = binding
    _binding_service._sync_to_openclaw()

    return binding.model_dump()


@router.put("/{binding_id}")
async def update_binding(
    binding_id: str,
    type: Optional[str] = None,
    agent_id: Optional[str] = None,
    match: Optional[dict[str, Any]] = None,
    acp: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """更新绑定

    Args:
        binding_id: 绑定 ID
        type: 新的绑定类型
        agent_id: 新的目标 Agent ID
        match: 新的匹配规则
        acp: 新的 ACP 配置

    Returns:
        更新后的绑定

    Raises:
        404: 绑定不存在
    """
    if binding_id not in _binding_service._bindings:
        raise HTTPException(status_code=404, detail=f"Binding '{binding_id}' not found")

    existing = _binding_service._bindings[binding_id]

    # 解析 match
    match_obj = existing.match
    if match:
        peer_obj = None
        if "peer" in match:
            peer_obj = PeerMatch(
                kind=match["peer"]["kind"],
                id=match["peer"]["id"],
            )
        match_obj = BindingMatch(
            channel=match.get("channel", existing.match.channel),
            account_id=match.get("accountId", existing.match.account_id),
            peer=peer_obj,
            guild_id=match.get("guildId", existing.match.guild_id),
            team_id=match.get("teamId", existing.match.team_id),
        )

    # 解析 acp
    acp_obj = existing.acp
    if acp is not None:
        acp_obj = AcpConfig(
            mode=acp.get("mode", existing.acp.mode if existing.acp else "persistent"),
            label=acp.get("label", existing.acp.label if existing.acp else None),
            cwd=acp.get("cwd", existing.acp.cwd if existing.acp else None),
            backend=acp.get("backend", existing.acp.backend if existing.acp else "acpx"),
        )

    updated = Binding(
        id=binding_id,
        type=type if type is not None else existing.type,
        agent_id=agent_id if agent_id is not None else existing.agent_id,
        match=match_obj,
        acp=acp_obj,
        created_at=existing.created_at,
        updated_at=datetime.utcnow(),
    )

    _binding_service._bindings[binding_id] = updated
    _binding_service._sync_to_openclaw()

    return updated.model_dump()


@router.delete("/{binding_id}")
async def delete_binding(binding_id: str) -> dict[str, str]:
    """删除绑定

    Args:
        binding_id: 绑定 ID

    Returns:
        删除确认

    Raises:
        404: 绑定不存在
    """
    if binding_id not in _binding_service._bindings:
        raise HTTPException(status_code=404, detail=f"Binding '{binding_id}' not found")

    del _binding_service._bindings[binding_id]
    _binding_service._sync_to_openclaw()

    return {"status": "deleted", "id": binding_id}


@router.post("/match")
async def match_binding_endpoint(
    channel: str,
    peer: Optional[dict[str, Any]] = None,
    guild_id: Optional[str] = None,
    team_id: Optional[str] = None,
    account_id: Optional[str] = None,
) -> dict[str, Any]:
    """按优先级匹配绑定

    Args:
        channel: 渠道名称
        peer: 对等体信息
        guild_id: Discord 服务器 ID
        team_id: Slack/MSTeams 团队 ID
        account_id: 账号 ID

    Returns:
        匹配的绑定，无匹配时返回 null
    """
    from app.services.binding_service import match_binding

    result = match_binding(
        list(_binding_service._bindings.values()),
        channel,
        peer,
        guild_id,
        team_id,
        account_id,
    )

    if result:
        return result.model_dump()
    return {"matched": False, "binding": None}
