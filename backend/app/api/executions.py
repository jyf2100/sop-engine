"""Execution 管理 REST API。

REQ-0001-017: REST API - 执行管理
"""
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from app.services.execution_service import ExecutionService
from app.models.execution import ExecutionStatus

router = APIRouter(prefix="/api/executions", tags=["executions"])


def get_service(request: Request) -> ExecutionService:
    """获取 ExecutionService 实例"""
    if not hasattr(request.app.state, "execution_service"):
        request.app.state.execution_service = ExecutionService()
    return request.app.state.execution_service


def get_template_service(request: Request):
    """获取 TemplateService 实例"""
    if not hasattr(request.app.state, "template_service"):
        from app.services.template_service import TemplateService
        request.app.state.template_service = TemplateService()
    return request.app.state.template_service


class ExecutionStart(BaseModel):
    """启动执行请求"""
    template_id: str
    params: dict[str, Any]


class ExecutionResponse(BaseModel):
    """执行响应"""
    id: str
    template_id: str
    status: str
    params: dict[str, Any]
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ExecutionListResponse(BaseModel):
    """执行列表响应"""
    items: list[ExecutionResponse]
    total: int
    skip: int
    limit: int


class NodeExecutionResponse(BaseModel):
    """节点执行响应"""
    id: str
    execution_id: str
    node_id: str
    status: str
    input: Optional[dict[str, Any]] = None
    output: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class NodeExecutionListResponse(BaseModel):
    """节点执行列表响应"""
    items: list[NodeExecutionResponse]
    total: int


@router.get("", response_model=ExecutionListResponse)
async def list_executions(
    request: Request,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    template_id: Optional[str] = Query(None),
) -> dict[str, Any]:
    """获取执行列表"""
    service = get_service(request)

    # 转换状态
    status_enum = None
    if status:
        try:
            status_enum = ExecutionStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

    executions, total = service.list_executions(
        skip=skip,
        limit=limit,
        status=status_enum,
        template_id=template_id,
    )

    return {
        "items": [_execution_to_dict(e) for e in executions],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("", response_model=ExecutionResponse, status_code=201)
async def start_execution(
    request: Request,
    data: ExecutionStart,
) -> dict[str, Any]:
    """启动执行"""
    service = get_service(request)
    template_service = get_template_service(request)

    try:
        execution = service.start_execution(
            template_id=data.template_id,
            params=data.params,
            template_service=template_service,
        )
        return _execution_to_dict(execution)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    request: Request,
    execution_id: str,
) -> dict[str, Any]:
    """获取执行详情"""
    service = get_service(request)
    try:
        execution = service.get_execution(execution_id)
        return _execution_to_dict(execution)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Execution '{execution_id}' not found")


@router.post("/{execution_id}/cancel", response_model=ExecutionResponse)
async def cancel_execution(
    request: Request,
    execution_id: str,
) -> dict[str, Any]:
    """取消执行"""
    service = get_service(request)
    try:
        execution = service.cancel_execution(execution_id)
        return _execution_to_dict(execution)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Execution '{execution_id}' not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{execution_id}/nodes", response_model=NodeExecutionListResponse)
async def list_execution_nodes(
    request: Request,
    execution_id: str,
) -> dict[str, Any]:
    """获取节点执行列表"""
    service = get_service(request)
    try:
        nodes = service.list_node_executions(execution_id)
        return {
            "items": [_node_execution_to_dict(n) for n in nodes],
            "total": len(nodes),
        }
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Execution '{execution_id}' not found")


def _execution_to_dict(execution) -> dict[str, Any]:
    """将执行转换为字典"""
    return {
        "id": execution.id,
        "template_id": execution.template_id,
        "status": execution.status.value if hasattr(execution.status, "value") else execution.status,
        "params": execution.params or {},
        "started_at": execution.started_at.isoformat() if execution.started_at else None,
        "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
        "created_at": execution.created_at.isoformat() if execution.created_at else None,
        "updated_at": execution.updated_at.isoformat() if execution.updated_at else None,
    }


def _node_execution_to_dict(node_exec) -> dict[str, Any]:
    """将节点执行转换为字典"""
    return {
        "id": node_exec.id,
        "execution_id": node_exec.execution_id,
        "node_id": node_exec.node_id,
        "status": node_exec.status.value if hasattr(node_exec.status, "value") else node_exec.status,
        "input": node_exec.input,
        "output": node_exec.output,
        "error": node_exec.error,
        "started_at": node_exec.started_at.isoformat() if node_exec.started_at else None,
        "completed_at": node_exec.completed_at.isoformat() if node_exec.completed_at else None,
    }
