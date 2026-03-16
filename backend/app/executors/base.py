"""BaseExecutor 抽象基类。

REQ-0001-010: BaseExecutor 抽象基类

定义节点执行器的统一接口。
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class NodeStatus(str, Enum):
    """节点执行状态"""

    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class NodeResult:
    """节点执行结果

    不可变数据类，记录节点执行的状态、输出和错误信息。
    """

    status: NodeStatus
    output: Optional[dict[str, Any]] = None
    error: Optional[str] = None


class BaseExecutor(ABC):
    """节点执行器抽象基类

    所有具体的节点执行器都必须继承此类并实现 execute 方法。
    """

    @abstractmethod
    def execute(
        self,
        node: dict[str, Any],
        context: dict[str, Any],
    ) -> NodeResult:
        """执行节点

        Args:
            node: 节点配置（来自 FlowTemplate）
            context: 执行上下文（包含变量和状态）

        Returns:
            NodeResult: 节点执行结果
        """
        pass

    def validate_node(self, node: dict[str, Any]) -> bool:
        """验证节点配置

        Args:
            node: 节点配置

        Returns:
            配置是否有效

        Raises:
            ValueError: 配置无效
        """
        if not node.get("id"):
            raise ValueError("Node must have an 'id' field")
        if not node.get("type"):
            raise ValueError("Node must have a 'type' field")
        return True
