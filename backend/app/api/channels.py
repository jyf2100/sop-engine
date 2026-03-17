"""Channel 管理 REST API。

提供 Channel 的 CRUD 操作。
"""
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from app.models import ChannelConfig
from app.services.channel_service import ChannelService

router = APIRouter(prefix="/api/channels", tags=["channels"])


def get_service(request: Request) -> ChannelService:
    """获取 ChannelService 实例"""
    return request.app.state.channel_service


@router.get("")
async def list_channels(request: Request) -> list[dict[str, Any]]:
    """获取 Channel 列表"""
    service = get_service(request)
    channels = service.list_channels()
    return [_channel_to_dict(c) for c in channels]


@router.post("", status_code=201)
async def create_channel(request: Request, data: dict[str, Any]) -> dict[str, Any]:
    """创建 Channel"""
    service = get_service(request)

    channel_id = data.get("id")
    if not channel_id:
        raise HTTPException(status_code=422, detail="Missing required field: id")

    name = data.get("name")
    if not name:
        raise HTTPException(status_code=422, detail="Missing required field: name")

    channel_type = data.get("type")
    if not channel_type:
        raise HTTPException(status_code=422, detail="Missing required field: type")

    try:
        channel = service.create_channel(
            channel_id=channel_id,
            name=name,
            type=channel_type,
            enabled=data.get("enabled", True),
            bot_token=data.get("bot_token"),
            dm_policy=data.get("dm_policy", "pairing"),
            allow_from=data.get("allow_from"),
            group_policy=data.get("group_policy", "allowlist"),
            group_allow_from=data.get("group_allow_from"),
            groups=data.get("groups"),
            streaming=data.get("streaming", "partial"),
            media_max_mb=data.get("media_max_mb", 100),
            phone_id=data.get("phone_id"),
            # 飞书配置
            app_id=data.get("app_id"),
            app_secret=data.get("app_secret"),
            encrypt_key=data.get("encrypt_key"),
            verification_token=data.get("verification_token"),
        )
        return _channel_to_dict(channel)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{channel_id}")
async def get_channel(request: Request, channel_id: str) -> dict[str, Any]:
    """获取 Channel 详情"""
    service = get_service(request)
    try:
        channel = service.get_channel(channel_id)
        return _channel_to_dict(channel)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Channel '{channel_id}' not found")


@router.patch("/{channel_id}")
async def update_channel(
    request: Request,
    channel_id: str,
    data: dict[str, Any],
) -> dict[str, Any]:
    """更新 Channel"""
    service = get_service(request)
    try:
        channel = service.update_channel(
            channel_id=channel_id,
            name=data.get("name"),
            enabled=data.get("enabled"),
            bot_token=data.get("bot_token"),
            dm_policy=data.get("dm_policy"),
            allow_from=data.get("allow_from"),
            group_policy=data.get("group_policy"),
            group_allow_from=data.get("group_allow_from"),
            groups=data.get("groups"),
            streaming=data.get("streaming"),
            media_max_mb=data.get("media_max_mb"),
            phone_id=data.get("phone_id"),
            # 飞书配置
            app_id=data.get("app_id"),
            app_secret=data.get("app_secret"),
            encrypt_key=data.get("encrypt_key"),
            verification_token=data.get("verification_token"),
        )
        return _channel_to_dict(channel)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Channel '{channel_id}' not found")


@router.delete("/{channel_id}", status_code=204)
async def delete_channel(request: Request, channel_id: str) -> None:
    """删除 Channel"""
    service = get_service(request)
    try:
        service.delete_channel(channel_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Channel '{channel_id}' not found")


def _channel_to_dict(channel: ChannelConfig) -> dict[str, Any]:
    """将 Channel 转换为字典（隐藏敏感字段）"""
    return {
        "id": channel.id,
        "name": channel.name,
        "type": channel.type,
        "enabled": channel.enabled,
        # Telegram 配置
        "bot_token": "***" if channel.bot_token else None,
        "has_bot_token": bool(channel.bot_token),
        "dm_policy": channel.dm_policy,
        "allow_from": channel.allow_from,
        "group_policy": channel.group_policy,
        "group_allow_from": channel.group_allow_from,
        "groups": channel.groups,
        "streaming": channel.streaming,
        "media_max_mb": channel.media_max_mb,
        # WhatsApp 配置
        "phone_id": "***" if channel.phone_id else None,
        "has_phone_id": bool(channel.phone_id),
        # 飞书配置
        "app_id": "***" if channel.app_id else None,
        "has_app_id": bool(channel.app_id),
        "app_secret": "***" if channel.app_secret else None,
        "has_app_secret": bool(channel.app_secret),
        "encrypt_key": "***" if channel.encrypt_key else None,
        "has_encrypt_key": bool(channel.encrypt_key),
        "verification_token": "***" if channel.verification_token else None,
        "has_verification_token": bool(channel.verification_token),
        # 元数据
        "created_at": channel.created_at.isoformat() if channel.created_at else None,
        "updated_at": channel.updated_at.isoformat() if channel.updated_at else None,
    }
