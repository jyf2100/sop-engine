"""Approval 管理 REST API。

REQ-0001-018: REST API - 审批管理
"""
from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query, Request, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from app.services.approval_service import ApprovalService, ApprovalStatus

router = APIRouter(prefix="/api/approvals", tags=["approvals"])


def get_service(request: Request) -> ApprovalService:
    """获取 ApprovalService 实例"""
    if not hasattr(request.app.state, "approval_service"):
        request.app.state.approval_service = ApprovalService()
    return request.app.state.approval_service


class ApprovalSubmit(BaseModel):
    """提交审批请求"""
    approved: bool
    comment: Optional[str] = None
    decided_by: Optional[str] = None


class ApprovalResponse(BaseModel):
    """审批响应"""
    id: str
    execution_id: str
    node_id: str
    message: str
    status: str
    timeout_seconds: int
    comment: Optional[str] = None
    decided_by: Optional[str] = None
    created_at: Optional[str] = None
    expires_at: Optional[str] = None
    decided_at: Optional[str] = None


class ApprovalListResponse(BaseModel):
    """审批列表响应"""
    items: list[ApprovalResponse]
    total: int


class PendingApprovalResponse(BaseModel):
    """待审批响应"""
    execution_id: str
    node_id: str
    message: str
    status: str
    created_at: Optional[str] = None
    expires_at: Optional[str] = None


class PendingApprovalListResponse(BaseModel):
    """待审批列表响应"""
    items: list[PendingApprovalResponse]
    total: int


@router.get("/pending", response_model=PendingApprovalListResponse)
async def list_pending_approvals(
    request: Request,
) -> dict[str, Any]:
    """获取待审批列表"""
    service = get_service(request)
    pending = service.list_pending()

    return {
        "items": [
            {
                "execution_id": a.execution_id,
                "node_id": a.node_id,
                "message": a.message,
                "status": a.status.value,
                "created_at": a.created_at.isoformat() if a.created_at else None,
                "expires_at": a.expires_at.isoformat() if a.expires_at else None,
            }
            for a in pending
        ],
        "total": len(pending),
    }


@router.post("/{execution_id}/{node_id}", response_model=ApprovalResponse)
async def submit_approval(
    request: Request,
    execution_id: str,
    node_id: str,
    data: ApprovalSubmit,
) -> dict[str, Any]:
    """提交审批"""
    service = get_service(request)

    # 查找对应的审批
    approval = None
    for a in service.list_pending():
        if a.execution_id == execution_id and a.node_id == node_id:
            approval = a
            break

    if not approval:
        raise HTTPException(
            status_code=404,
            detail=f"Approval for execution '{execution_id}' node '{node_id}' not found"
        )

    try:
        updated = service.submit_approval(
            approval_id=approval.id,
            approved=data.approved,
            comment=data.comment,
            decided_by=data.decided_by,
        )
        return _approval_to_dict(updated)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def _approval_to_dict(approval) -> dict[str, Any]:
    """将审批转换为字典"""
    return {
        "id": approval.id,
        "execution_id": approval.execution_id,
        "node_id": approval.node_id,
        "message": approval.message,
        "status": approval.status.value,
        "timeout_seconds": approval.timeout_seconds,
        "comment": approval.comment,
        "decided_by": approval.decided_by,
        "created_at": approval.created_at.isoformat() if approval.created_at else None,
        "expires_at": approval.expires_at.isoformat() if approval.expires_at else None,
        "decided_at": approval.decided_at.isoformat() if approval.decided_at else None,
    }


# WebSocket 连接管理
class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.subscriptions: dict[WebSocket, set[str]] = {}

    async def connect(self, websocket: WebSocket):
        """接受连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.subscriptions[websocket] = set()

    def disconnect(self, websocket: WebSocket):
        """断开连接"""
        self.active_connections.remove(websocket)
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]

    async def send_json(self, websocket: WebSocket, data: dict):
        """发送 JSON 消息"""
        await websocket.send_json(data)

    async def subscribe(self, websocket: WebSocket, execution_id: str):
        """订阅执行"""
        self.subscriptions[websocket].add(execution_id)

    async def broadcast_to_subscribers(self, execution_id: str, message: dict):
        """广播给订阅者"""
        for websocket, subs in self.subscriptions.items():
            if execution_id in subs:
                try:
                    await websocket.send_json(message)
                except Exception:
                    pass


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 端点"""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()

            if data.get("type") == "subscribe":
                execution_id = data.get("execution_id")
                if execution_id:
                    await manager.subscribe(websocket, execution_id)
                    await manager.send_json(websocket, {
                        "type": "subscribed",
                        "execution_id": execution_id,
                    })

            elif data.get("type") == "ping":
                await manager.send_json(websocket, {"type": "pong"})

            else:
                # 忽略未知消息或返回错误
                await manager.send_json(websocket, {
                    "type": "error",
                    "message": "Unknown message type",
                })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
