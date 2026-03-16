"""Template 管理 REST API。

REQ-0001-016: REST API - 模板管理
"""
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from app.services.template_service import TemplateService

router = APIRouter(prefix="/api/templates", tags=["templates"])


def get_service(request: Request) -> TemplateService:
    """获取 TemplateService 实例"""
    if not hasattr(request.app.state, "template_service"):
        request.app.state.template_service = TemplateService()
    return request.app.state.template_service


class TemplateCreate(BaseModel):
    """创建模板请求"""
    name: str
    version: str = "1.0"
    yaml_content: str
    description: Optional[str] = None


class TemplateResponse(BaseModel):
    """模板响应"""
    id: str
    name: str
    version: str
    yaml_content: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class TemplateListResponse(BaseModel):
    """模板列表响应"""
    items: list[TemplateResponse]
    total: int
    skip: int
    limit: int


@router.get("", response_model=TemplateListResponse)
async def list_templates(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> dict[str, Any]:
    """获取模板列表"""
    service = get_service(request)
    templates, total = service.list_templates(skip=skip, limit=limit)

    return {
        "items": [_template_to_dict(t) for t in templates],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("", response_model=TemplateResponse, status_code=201)
async def create_template(
    request: Request,
    data: TemplateCreate,
) -> dict[str, Any]:
    """创建模板"""
    service = get_service(request)
    try:
        template = service.create_template(
            name=data.name,
            yaml_content=data.yaml_content,
            version=data.version,
            description=data.description,
        )
        return _template_to_dict(template)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    request: Request,
    template_id: str,
) -> dict[str, Any]:
    """获取模板详情"""
    service = get_service(request)
    try:
        template = service.get_template(template_id)
        return _template_to_dict(template)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")


@router.delete("/{template_id}", status_code=204)
async def delete_template(
    request: Request,
    template_id: str,
) -> None:
    """删除模板"""
    service = get_service(request)
    try:
        service.delete_template(template_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")


@router.post("/upload", response_model=TemplateResponse, status_code=201)
async def upload_yaml(
    request: Request,
) -> dict[str, Any]:
    """上传 YAML 模板"""
    service = get_service(request)

    # 读取原始 body
    content = await request.body()
    yaml_content = content.decode("utf-8")

    try:
        template = service.upload_yaml(yaml_content)
        return _template_to_dict(template)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def _template_to_dict(template) -> dict[str, Any]:
    """将模板转换为字典"""
    return {
        "id": template.id,
        "name": template.name,
        "version": template.version,
        "yaml_content": template.yaml_content,
        "created_at": template.created_at.isoformat() if template.created_at else None,
        "updated_at": template.updated_at.isoformat() if template.updated_at else None,
    }
