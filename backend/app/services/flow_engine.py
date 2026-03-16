"""FlowEngine 流程引擎。

REQ-0001-009: FlowEngine 核心

流程编排的核心引擎，控制节点执行和状态转换。
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from app.executors.base import BaseExecutor, NodeResult, NodeStatus
from app.executors.registry import ExecutorRegistry, get_registry
from app.models.flow_template import FlowTemplate, NodeType
from app.services.context_manager import ContextManager
from app.services.event_bus import EventBus, MemoryEventBus


class ExecutionStatus(str, Enum):
    """执行状态"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Execution:
    """执行实例"""

    id: str
    template_id: str
    template: FlowTemplate
    status: ExecutionStatus = ExecutionStatus.PENDING
    current_node: Optional[str] = None
    params: dict[str, Any] = field(default_factory=dict)
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # 节点执行记录
    node_executions: dict[str, dict[str, Any]] = field(default_factory=dict)


class FlowEngine:
    """流程引擎

    负责流程的启动、节点执行、状态转换和错误处理。
    """

    def __init__(
        self,
        event_bus: Optional[EventBus] = None,
        context_manager: Optional[ContextManager] = None,
        executor_registry: Optional[ExecutorRegistry] = None,
    ):
        self.event_bus = event_bus or MemoryEventBus()
        self.context_manager = context_manager or ContextManager()
        self.executor_registry = executor_registry or get_registry()

        # 执行存储（生产环境应使用数据库）
        self._executions: dict[str, Execution] = {}

    def start_execution(
        self,
        template: FlowTemplate,
        params: dict[str, Any],
    ) -> Execution:
        """启动执行

        Args:
            template: 流程模板
            params: 执行参数

        Returns:
            Execution: 执行实例
        """
        # 创建执行实例
        execution = self._create_execution(template, params)

        # 设置初始参数到上下文
        for key, value in params.items():
            self.context_manager.set(execution.id, key, value)

        # 更新状态
        execution.status = ExecutionStatus.RUNNING
        execution.started_at = datetime.utcnow()

        # 查找 start 节点
        start_node = self._find_start_node(template)
        execution.current_node = start_node.id

        # 发布执行开始事件
        self.event_bus.publish({
            "type": "execution.started",
            "execution_id": execution.id,
            "template_id": template.id,
            "timestamp": datetime.utcnow().isoformat(),
        })

        # 存储执行
        self._executions[execution.id] = execution

        return execution

    def execute_node(
        self,
        execution: Execution,
        node: dict[str, Any],
    ) -> NodeResult:
        """执行单个节点

        Args:
            execution: 执行实例
            node: 节点配置（FlowNode 或 dict）

        Returns:
            NodeResult: 节点执行结果
        """
        # 支持 FlowNode Pydantic 模型和 dict
        if hasattr(node, "id"):
            node_id = node.id
            node_type = node.type.value if hasattr(node.type, "value") else node.type
            node_dict = node.model_dump() if hasattr(node, "model_dump") else dict(node)
        else:
            node_id = node.get("id", "unknown")
            node_type = node.get("type", "unknown")
            node_dict = node

        # 发布节点开始事件
        self.event_bus.publish({
            "type": "node.started",
            "execution_id": execution.id,
            "node_id": node_id,
            "node_type": node_type,
            "timestamp": datetime.utcnow().isoformat(),
        })

        # 获取执行器
        executor = self.executor_registry.get(node_type)

        if executor is None:
            # 没有注册执行器，返回成功（如 start/end 节点）
            result = NodeResult(status=NodeStatus.SUCCESS)
        else:
            # 获取上下文
            context = self.context_manager.get_all(execution.id)

            # 执行
            try:
                result = executor.execute(node_dict, context)
            except Exception as e:
                result = NodeResult(status=NodeStatus.FAILED, error=str(e))

        # 如果有输出变量，保存到上下文
        if result.status == NodeStatus.SUCCESS and result.output:
            output_var = node_dict.get("output_var")
            if output_var and output_var in result.output:
                self.context_manager.set(execution.id, output_var, result.output[output_var])
            elif output_var:
                self.context_manager.set(execution.id, output_var, result.output)

        # 记录节点执行
        execution.node_executions[node_id] = {
            "status": result.status.value,
            "output": result.output,
            "error": result.error,
            "completed_at": datetime.utcnow().isoformat(),
        }

        # 发布节点完成事件
        self.event_bus.publish({
            "type": "node.completed",
            "execution_id": execution.id,
            "node_id": node_id,
            "status": result.status.value,
            "timestamp": datetime.utcnow().isoformat(),
        })

        return result

    def transition(
        self,
        execution: Execution,
        result: NodeResult,
    ) -> Optional[str]:
        """计算下一节点

        Args:
            execution: 执行实例
            result: 当前节点执行结果

        Returns:
            下一节点 ID，如果没有则返回 None
        """
        current_node_id = execution.current_node
        if not current_node_id:
            return None

        current_node = execution.template.nodes.get(current_node_id)
        if not current_node:
            return None

        # 条件节点：根据结果选择分支
        if current_node.type == NodeType.CONDITION:
            branches = current_node.branches or {}
            branch = result.output.get("branch") if result.output else None
            if branch and branch in branches:
                return branches[branch]
            # 默认分支
            return branches.get("default")

        # 普通节点：使用 next 字段
        return current_node.next

    def handle_failure(
        self,
        execution: Execution,
        error: str,
    ) -> None:
        """处理执行失败

        Args:
            execution: 执行实例
            error: 错误信息
        """
        execution.status = ExecutionStatus.FAILED
        execution.error = error
        execution.completed_at = datetime.utcnow()

        # 发布执行失败事件
        self.event_bus.publish({
            "type": "execution.failed",
            "execution_id": execution.id,
            "error": error,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def run(self, execution: Execution) -> Execution:
        """运行执行直到完成

        Args:
            execution: 执行实例

        Returns:
            完成后的执行实例
        """
        while execution.status == ExecutionStatus.RUNNING:
            current_node_id = execution.current_node
            if not current_node_id:
                break

            current_node = execution.template.nodes.get(current_node_id)
            if not current_node:
                self.handle_failure(execution, f"Node '{current_node_id}' not found")
                break

            # 执行节点
            node_dict = current_node.model_dump()
            result = self.execute_node(execution, node_dict)

            # 处理失败
            if result.status == NodeStatus.FAILED:
                self.handle_failure(execution, result.error or "Node execution failed")
                break

            # 到达 end 节点
            if current_node.type == NodeType.END:
                execution.status = ExecutionStatus.COMPLETED
                execution.completed_at = datetime.utcnow()

                self.event_bus.publish({
                    "type": "execution.completed",
                    "execution_id": execution.id,
                    "timestamp": datetime.utcnow().isoformat(),
                })
                break

            # 转换到下一节点
            next_node_id = self.transition(execution, result)
            if not next_node_id:
                self.handle_failure(execution, "No next node and not at end")
                break

            execution.current_node = next_node_id

        return execution

    def get_execution(self, execution_id: str) -> Optional[Execution]:
        """获取执行实例

        Args:
            execution_id: 执行 ID

        Returns:
            执行实例，不存在则返回 None
        """
        return self._executions.get(execution_id)

    def cancel_execution(self, execution_id: str) -> bool:
        """取消执行

        Args:
            execution_id: 执行 ID

        Returns:
            是否取消成功
        """
        execution = self._executions.get(execution_id)
        if not execution:
            return False

        if execution.status not in (ExecutionStatus.PENDING, ExecutionStatus.RUNNING):
            return False

        execution.status = ExecutionStatus.CANCELLED
        execution.completed_at = datetime.utcnow()

        self.event_bus.publish({
            "type": "execution.cancelled",
            "execution_id": execution_id,
            "timestamp": datetime.utcnow().isoformat(),
        })

        return True

    # === 内部方法 ===

    def _create_execution(
        self,
        template: FlowTemplate,
        params: dict[str, Any],
    ) -> Execution:
        """创建执行实例"""
        execution_id = f"exec-{uuid.uuid4().hex[:12]}"
        return Execution(
            id=execution_id,
            template_id=template.id,
            template=template,
            params=params,
        )

    def _find_start_node(self, template: FlowTemplate) -> dict[str, Any]:
        """查找 start 节点"""
        for node_id, node in template.nodes.items():
            if node.type == NodeType.START:
                return node
        raise ValueError("Template must have a start node")

    def _set_current_node(self, execution: Execution, node_id: str) -> None:
        """设置当前节点"""
        execution.current_node = node_id
