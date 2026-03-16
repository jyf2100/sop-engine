"""Agent 配置模型。

REQ-0001-002: 数据库模型定义
REQ-0001-003: Agent 配置管理

对应 OpenClaw agents.list[] 的完整配置。
SOP Engine 是 Agent 配置的唯一来源（Source of Truth）。
"""
from datetime import datetime
from typing import Any

from .base import Base


class Agent(Base):
    """Agent 配置模型

    存储 OpenClaw Agent 的元数据和配置。
    所有配置变更通过 SOP Engine 进行，OpenClaw 被动接收。
    """

    id: str
    name: str
    workspace_path: str

    # 模型配置 (对应 openclaw.json model.*)
    llm_config: dict[str, Any]  # primary, fallbacks

    # 沙箱配置 (对应 openclaw.json sandbox.*)
    sandbox_config: dict[str, Any]  # mode, workspaceAccess, scope, docker

    # 工具配置 (对应 openclaw.json tools.*)
    tools_config: dict[str, Any]  # profile, allow, deny, exec

    # 心跳配置 (对应 openclaw.json heartbeat.*)
    heartbeat_config: dict[str, Any] | None = None  # every, target

    # 记忆搜索配置 (对应 openclaw.json memorySearch.*)
    memory_search_config: dict[str, Any] | None = None  # enabled, provider, model

    # 群聊配置 (对应 openclaw.json groupChat.*)
    group_chat_config: dict[str, Any] | None = None  # mentionPatterns

    # 其他元数据
    is_default: bool = False
    is_active: bool = True

    created_at: datetime | None = None
    updated_at: datetime | None = None
