"""节点执行记录模型。

REQ-0001-002: 数据库模型定义
"""
from datetime import datetime
from typing import Any

from .base import Base


class NodeExecution(Base):
    """节点执行记录模型

    记录每个节点的执行状态和结果。
    """

    id: str
    execution_id: str
    node_id: str
    status: str = "pending"  # pending, running, completed, failed, skipped
    input: dict[str, Any] | None = None
    output: dict[str, Any] | None = None
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
