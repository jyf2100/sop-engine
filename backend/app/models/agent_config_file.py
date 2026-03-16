"""Agent 配置文件模型。

REQ-0001-002: 数据库模型定义
REQ-0001-003: Agent 配置管理

存储 Agent 的配置文件内容（AGENTS.md, SOUL.md, USER.md 等）。
这些文件会被同步到 OpenClaw workspace 目录。
"""
from datetime import datetime

from .base import Base

# 支持的配置文件类型
CONFIG_FILE_TYPES = frozenset([
    "AGENTS.md",      # 操作指令、行为规则（必需）
    "SOUL.md",        # 人设、语调、边界（必需）
    "USER.md",        # 用户信息、称呼方式（必需）
    "IDENTITY.md",    # Agent 名称、风格、emoji（必需）
    "TOOLS.md",       # 工具使用说明（可选）
    "HEARTBEAT.md",   # 心跳检查清单（可选）
    "BOOT.md",        # 启动清单（可选）
    "BOOTSTRAP.md",   # 首次运行引导（可选）
    "MEMORY.md",      # 长期记忆（可选）
])


class AgentConfigFile(Base):
    """Agent 配置文件模型

    存储 Agent workspace 中的配置文件内容。
    同步时会写入 {OPENCLAW_WORKSPACE_ROOT}/{agent_id}/{file_type}
    """

    id: str
    agent_id: str
    file_type: str  # CONFIG_FILE_TYPES 中的值
    content: str

    created_at: datetime | None = None
    updated_at: datetime | None = None

    def is_required(self) -> bool:
        """检查是否为必需配置文件"""
        return self.file_type in {"AGENTS.md", "SOUL.md", "USER.md", "IDENTITY.md"}
