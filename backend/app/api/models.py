"""模型配置管理 REST API。

REQ-0001-XXX: 模型配置管理
"""
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from app.models import ModelConfig
from app.services.model_service import ModelService

router = APIRouter(prefix="/api/models", tags=["models"])


def get_service(request: Request) -> ModelService:
    """获取 ModelService 实例"""
    return request.app.state.model_service


def _model_to_dict(model: ModelConfig) -> dict[str, Any]:
    """将 ModelConfig 转换为字典（隐藏 API Key）"""
    return {
        "id": model.id,
        "name": model.name,
        "type": model.type,
        "provider": model.provider,
        "model_id": model.model_id,
        "base_url": model.base_url,
        "api_key": "***" if model.api_key else "",  # 隐藏 API Key
        "default_params": model.default_params,
        "dimensions": model.dimensions,
        "default_size": model.default_size,
        "is_default": model.is_default,
        "created_at": model.created_at.isoformat() if model.created_at else None,
        "updated_at": model.updated_at.isoformat() if model.updated_at else None,
    }


@router.get("")
async def list_models(
    request: Request,
    type: str | None = None,
) -> list[dict[str, Any]]:
    """获取模型配置列表

    Args:
        type: 可选的模型类型过滤 (llm | embedding | image)
    """
    service = get_service(request)
    models = service.list_models(type)
    return [_model_to_dict(m) for m in models]


@router.post("", status_code=201)
async def create_model(request: Request, data: dict[str, Any]) -> dict[str, Any]:
    """创建模型配置"""
    service = get_service(request)

    model_id = data.get("id")
    if not model_id:
        raise HTTPException(status_code=422, detail="Missing required field: id")

    try:
        model = service.create_model(
            model_id=model_id,
            name=data.get("name", model_id),
            model_type=data.get("type", "llm"),
            provider=data.get("provider", "custom"),
            model_id_str=data.get("model_id", model_id),
            base_url=data.get("base_url", ""),
            api_key=data.get("api_key", ""),
            default_params=data.get("default_params"),
            dimensions=data.get("dimensions"),
            default_size=data.get("default_size"),
            is_default=data.get("is_default", False),
        )
        return _model_to_dict(model)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{model_id}")
async def get_model(request: Request, model_id: str) -> dict[str, Any]:
    """获取模型配置详情"""
    service = get_service(request)
    try:
        model = service.get_model(model_id)
        return _model_to_dict(model)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")


@router.patch("/{model_id}")
async def update_model(
    request: Request,
    model_id: str,
    data: dict[str, Any],
) -> dict[str, Any]:
    """更新模型配置"""
    service = get_service(request)
    try:
        model = service.update_model(
            model_id=model_id,
            name=data.get("name"),
            provider=data.get("provider"),
            model_id_str=data.get("model_id"),
            base_url=data.get("base_url"),
            api_key=data.get("api_key"),
            default_params=data.get("default_params"),
            dimensions=data.get("dimensions"),
            default_size=data.get("default_size"),
            is_default=data.get("is_default"),
        )
        return _model_to_dict(model)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")


@router.delete("/{model_id}", status_code=204)
async def delete_model(request: Request, model_id: str) -> None:
    """删除模型配置"""
    service = get_service(request)
    try:
        service.delete_model(model_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")


@router.get("/default/{model_type}")
async def get_default_model(
    request: Request,
    model_type: str,
) -> dict[str, Any]:
    """获取指定类型的默认模型"""
    service = get_service(request)
    model = service.get_default_model(model_type)
    if not model:
        raise HTTPException(
            status_code=404,
            detail=f"No default model found for type '{model_type}'",
        )
    return _model_to_dict(model)
