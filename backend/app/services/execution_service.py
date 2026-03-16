"""执行管理服务。

REQ-0001-017: REST API - 执行管理
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from app.models.execution import Execution, ExecutionStatus
from app.models.node_execution import NodeExecution, NodeExecutionStatus


@dataclass
class ExecutionService:
    """执行管理服务

    提供执行的创建、查询、取消操作。
    """

    _executions: dict[str, Execution] = field(default_factory=dict)
    _node_executions: dict[str, list[NodeExecution]] = field(default_factory=dict)

    def start_execution(
        self,
        template_id: str,
        params: dict[str, Any],
        template_service: Any = None,
    ) -> Execution:
        """启动执行

        Args:
            template_id: 模板 ID
            params: 执行参数
            template_service: 模板服务（用于验证模板存在）

        Returns:
            创建的执行实例

        Raises:
            KeyError: 模板不存在
        """
        # 验证模板存在
        if template_service:
            try:
                template_service.get_template(template_id)
            except KeyError:
                raise KeyError(f"Template '{template_id}' not found")

        execution_id = f"exec-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow()

        execution = Execution(
            id=execution_id,
            template_id=template_id,
            status=ExecutionStatus.PENDING,
            params=params,
            started_at=now,
            created_at=now,
            updated_at=now,
        )

        self._executions[execution_id] = execution
        self._node_executions[execution_id] = []

        return execution

    def get_execution(self, execution_id: str) -> Execution:
        """获取执行详情

        Args:
            execution_id: 执行 ID

        Returns:
            执行实例

        Raises:
            KeyError: 执行不存在
        """
        if execution_id not in self._executions:
            raise KeyError(f"Execution '{execution_id}' not found")
        return self._executions[execution_id]

    def list_executions(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[ExecutionStatus] = None,
        template_id: Optional[str] = None,
    ) -> tuple[list[Execution], int]:
        """列出执行

        Args:
            skip: 跳过数量
            limit: 返回数量
            status: 状态过滤
            template_id: 模板 ID 过滤

        Returns:
            (执行列表, 总数)
        """
        all_executions = list(self._executions.values())

        # 过滤
        if status:
            all_executions = [e for e in all_executions if e.status == status]
        if template_id:
            all_executions = [e for e in all_executions if e.template_id == template_id]

        total = len(all_executions)
        return all_executions[skip:skip + limit], total

    def cancel_execution(self, execution_id: str) -> Execution:
        """取消执行

        Args:
            execution_id: 执行 ID

        Returns:
            更新后的执行实例

        Raises:
            KeyError: 执行不存在
            ValueError: 执行已完成，无法取消
        """
        execution = self.get_execution(execution_id)

        # 检查是否可取消
        status_value = execution.status.value if hasattr(execution.status, "value") else execution.status
        if status_value in ("completed", "failed", "cancelled"):
            raise ValueError(f"Cannot cancel execution with status '{status_value}'")

        # 更新状态
        now = datetime.utcnow()
        updated_execution = Execution(
            id=execution.id,
            template_id=execution.template_id,
            status=ExecutionStatus.CANCELLED,
            params=execution.params,
            started_at=execution.started_at,
            completed_at=now,
            created_at=execution.created_at,
            updated_at=now,
        )

        self._executions[execution_id] = updated_execution
        return updated_execution

    def list_node_executions(self, execution_id: str) -> list[NodeExecution]:
        """列出节点执行

        Args:
            execution_id: 执行 ID

        Returns:
            节点执行列表

        Raises:
            KeyError: 执行不存在
        """
        self.get_execution(execution_id)  # 验证存在
        return self._node_executions.get(execution_id, [])

    def add_node_execution(
        self,
        execution_id: str,
        node_id: str,
        status: NodeExecutionStatus = NodeExecutionStatus.PENDING,
        input_data: Optional[dict] = None,
        output_data: Optional[dict] = None,
        error: Optional[str] = None,
    ) -> NodeExecution:
        """添加节点执行记录

        Args:
            execution_id: 执行 ID
            node_id: 节点 ID
            status: 节点状态
            input_data: 输入数据
            output_data: 输出数据
            error: 错误信息

        Returns:
            创建的节点执行实例
        """
        self.get_execution(execution_id)  # 验证存在

        now = datetime.utcnow()
        node_exec = NodeExecution(
            id=f"node-exec-{uuid.uuid4().hex[:8]}",
            execution_id=execution_id,
            node_id=node_id,
            status=status,
            input=input_data,
            output=output_data,
            error=error,
            started_at=now,
            created_at=now,
            updated_at=now,
        )

        if execution_id not in self._node_executions:
            self._node_executions[execution_id] = []
        self._node_executions[execution_id].append(node_exec)

        return node_exec
