"""执行器注册表。

REQ-0001-010: BaseExecutor 抽象基类

按节点类型查找执行器。
"""
from typing import Optional

from app.executors.base import BaseExecutor


class ExecutorRegistry:
    """执行器注册表

    管理节点类型到执行器的映射。
    """

    def __init__(self):
        self._executors: dict[str, BaseExecutor] = {}

    def register(self, node_type: str, executor: BaseExecutor) -> None:
        """注册执行器

        Args:
            node_type: 节点类型
            executor: 执行器实例
        """
        self._executors[node_type] = executor

    def unregister(self, node_type: str) -> None:
        """注销执行器

        Args:
            node_type: 节点类型
        """
        if node_type in self._executors:
            del self._executors[node_type]

    def get(self, node_type: str) -> Optional[BaseExecutor]:
        """获取执行器

        Args:
            node_type: 节点类型

        Returns:
            执行器实例，不存在返回 None
        """
        return self._executors.get(node_type)

    def list(self) -> list[str]:
        """列出已注册的执行器类型

        Returns:
            节点类型列表
        """
        return list(self._executors.keys())

    def clear(self) -> None:
        """清空注册表"""
        self._executors.clear()


# 全局注册表实例
_global_registry: Optional[ExecutorRegistry] = None


def get_registry() -> ExecutorRegistry:
    """获取全局注册表实例

    Returns:
        全局注册表实例
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ExecutorRegistry()
    return _global_registry
