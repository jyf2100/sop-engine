"""执行实例模型。

REQ-0001-002: 数据库模型定义
"""
from datetime import datetime
from enum import Enum
from typing import Any

from .base import Base


class ExecutionStatus(str, Enum):
    """执行状态"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Execution(Base):
    """执行实例模型

    记录流程执行的完整生命周期。
    """

    id: str
    template_id: str
    status: str = "pending"  # pending, running, paused, completed, failed, cancelled
    params: dict[str, Any]
    context: dict[str, Any] | None = None
    current_node: str | None = None
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
