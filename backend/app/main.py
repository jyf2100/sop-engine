"""FastAPI 应用主入口。

REQ-0001-001: 项目骨架搭建
"""
from contextlib import asynccontextmanager
from typing import Any
from pathlib import Path

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .api.agents import router as agents_router
from .api.channels import router as channels_router
from .api.models import router as models_router
from .api.templates import router as templates_router
from .api.executions import router as executions_router
from .api.approvals import router as approvals_router, websocket_endpoint


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化服务
    from .services.agent_service import AgentService
    from .services.channel_service import ChannelService
    from .services.model_service import ModelService

    workspace_root = Path(settings.openclaw_workspace_root).expanduser()
    app.state.agent_service = AgentService(workspace_root=workspace_root)
    app.state.model_service = ModelService()
    app.state.channel_service = ChannelService()
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

# 配置 CORS - 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(agents_router)
app.include_router(channels_router)
app.include_router(models_router)
app.include_router(templates_router)
app.include_router(executions_router)
app.include_router(approvals_router)


# WebSocket 端点
@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    """WebSocket 实时推送端点"""
    await websocket_endpoint(websocket)


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
