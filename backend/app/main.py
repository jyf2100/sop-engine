"""FastAPI 应用主入口。

REQ-0001-001: 项目骨架搭建
"""
from contextlib import asynccontextmanager
from typing import Any
from pathlib import Path

from fastapi import FastAPI

from .config import settings
from .api.agents import router as agents_router
from .api.templates import router as templates_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化 AgentService
    from .services.agent_service import AgentService
    workspace_root = Path(settings.openclaw_workspace_root).expanduser()
    app.state.agent_service = AgentService(workspace_root=workspace_root)
    yield
    # 关闭时清理


app = FastAPI(
    title="SOP Engine",
    description="SOP 编排引擎 API - 基于 OpenClaw 的工作流自动化平台",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# 注册路由
app.include_router(agents_router)
app.include_router(templates_router)


@app.get("/", response_model=dict[str, Any])
async def root() -> dict[str, Any]:
    """根路径 - 返回 API 信息"""
    return {
        "name": "SOP Engine",
        "version": "0.1.0",
        "description": "SOP 编排引擎 API",
        "environment": settings.environment,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """健康检查端点"""
    return {"status": "ok"}
