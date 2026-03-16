"""执行器模块。

REQ-0001-010: BaseExecutor 抽象基类
"""
from .base import BaseExecutor, NodeResult, NodeStatus
from .registry import ExecutorRegistry

__all__ = [
    "BaseExecutor",
    "NodeResult",
    "NodeStatus",
    "ExecutorRegistry",
]
