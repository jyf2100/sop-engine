"""Agent 管理 REST API。

REQ-0001-015: REST API - Agent 管理
"""
from typing import Any

from fastapi import APIRouter, HTTPException, Request

from app.models import Agent
from app.services.agent_service import AgentService

router = APIRouter(prefix="/api/agents", tags=["agents"])


def get_service(request: Request) -> AgentService:
    """获取 AgentService 实例"""
    return request.app.state.agent_service


@router.get("")
async def list_agents(request: Request) -> list[dict[str, Any]]:
    """获取 Agent 列表"""
    service = get_service(request)
    agents = service.list_agents()
    return [_agent_to_dict(a) for a in agents]


@router.post("", status_code=201)
async def create_agent(request: Request, data: dict[str, Any]) -> dict[str, Any]:
    """创建 Agent"""
    service = get_service(request)

    agent_id = data.get("id")
    if not agent_id:
        raise HTTPException(status_code=422, detail="Missing required field: id")

    try:
        agent = service.create_agent(
            agent_id=agent_id,
            name=data.get("name", agent_id),
            llm_config=data.get("llm_config"),
            sandbox_config=data.get("sandbox_config"),
            tools_config=data.get("tools_config"),
            is_default=data.get("is_default", False),
        )
        return _agent_to_dict(agent)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{agent_id}")
async def get_agent(request: Request, agent_id: str) -> dict[str, Any]:
    """获取 Agent 详情"""
    service = get_service(request)
    try:
        agent = service.get_agent(agent_id)
        return _agent_to_dict(agent)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")


@router.patch("/{agent_id}")
async def update_agent(
    request: Request,
    agent_id: str,
    data: dict[str, Any],
) -> dict[str, Any]:
    """更新 Agent"""
    service = get_service(request)
    try:
        agent = service.update_agent(
            agent_id=agent_id,
            name=data.get("name"),
            llm_config=data.get("llm_config"),
            sandbox_config=data.get("sandbox_config"),
            tools_config=data.get("tools_config"),
            is_default=data.get("is_default"),
            is_active=data.get("is_active"),
        )
        return _agent_to_dict(agent)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(request: Request, agent_id: str) -> None:
    """删除 Agent"""
    service = get_service(request)
    try:
        service.delete_agent(agent_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")


@router.get("/{agent_id}/files")
async def list_config_files(request: Request, agent_id: str) -> list[dict[str, Any]]:
    """列出 Agent 配置文件"""
    service = get_service(request)
    try:
        files = service.list_config_files(agent_id)
        return [
            {
                "id": f.id,
                "agent_id": f.agent_id,
                "file_type": f.file_type,
                "created_at": f.created_at.isoformat() if f.created_at else None,
                "updated_at": f.updated_at.isoformat() if f.updated_at else None,
            }
            for f in files
        ]
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")


@router.get("/{agent_id}/files/{file_type}")
async def get_config_file(
    request: Request,
    agent_id: str,
    file_type: str,
) -> dict[str, Any]:
    """获取配置文件内容"""
    service = get_service(request)
    try:
        content = service.get_config_file(agent_id, file_type)
        return {
            "agent_id": agent_id,
            "file_type": file_type,
            "content": content,
        }
    except KeyError as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{agent_id}/files/{file_type}")
async def update_config_file(
    request: Request,
    agent_id: str,
    file_type: str,
    data: dict[str, Any],
) -> dict[str, Any]:
    """更新配置文件"""
    service = get_service(request)
    content = data.get("content", "")
    try:
        config_file = service.update_config_file(agent_id, file_type, content)
        return {
            "id": config_file.id,
            "agent_id": config_file.agent_id,
            "file_type": config_file.file_type,
            "content": config_file.content,
            "updated_at": config_file.updated_at.isoformat() if config_file.updated_at else None,
        }
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")


@router.post("/{agent_id}/sync")
async def sync_agent(request: Request, agent_id: str) -> dict[str, Any]:
    """手动同步 Agent 到 OpenClaw"""
    service = get_service(request)
    try:
        agent = service.get_agent(agent_id)
        # 同步逻辑已经在 update_config_file 中自动执行
        # 这里只是显式触发
        service._ensure_workspace(agent_id)
        return {"status": "synced", "agent_id": agent_id}
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")


def _agent_to_dict(agent: Agent) -> dict[str, Any]:
    """将 Agent 转换为字典"""
    return {
        "id": agent.id,
        "name": agent.name,
        "workspace_path": agent.workspace_path,
        "llm_config": agent.llm_config,
        "sandbox_config": agent.sandbox_config,
        "tools_config": agent.tools_config,
        "is_default": agent.is_default,
        "is_active": agent.is_active,
        "created_at": agent.created_at.isoformat() if agent.created_at else None,
        "updated_at": agent.updated_at.isoformat() if agent.updated_at else None,
    }
