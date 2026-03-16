"""Human 审批节点执行器。

REQ-0001-014: Human 审批节点执行器

暂停流程等待人工审批。
"""
import re
from typing import Any, Optional

from app.executors.base import BaseExecutor, NodeResult, NodeStatus
from app.services.approval_service import ApprovalService, ApprovalStatus
from app.services.event_bus import EventBus, MemoryEventBus


class HumanExecutor(BaseExecutor):
    """Human 审批节点执行器

    暂停流程等待人工审批。
    """

    DEFAULT_TIMEOUT = 3600  # 1 hour

    def __init__(
        self,
        approval_service: Optional[ApprovalService] = None,
        event_bus: Optional[EventBus] = None,
    ):
        self.event_bus = event_bus or MemoryEventBus()
        self.approval_service = approval_service or ApprovalService(event_bus=self.event_bus)

    def execute(
        self,
        node: dict[str, Any],
        context: dict[str, Any],
    ) -> NodeResult:
        """执行审批节点

        Args:
            node: 节点配置
            context: 执行上下文

        Returns:
            NodeResult: 执行结果（状态为 paused）
        """
        # 获取审批消息
        message = node.get("approval_message", "Please approve")
        timeout_seconds = node.get("timeout_seconds", self.DEFAULT_TIMEOUT)

        # 变量替换
        try:
            message = self._substitute_variables(message, context)
        except Exception:
            pass  # 保持原消息

        # 获取执行 ID
        execution_id = context.get("execution_id", "unknown")
        node_id = node.get("id", "unknown")

        # 创建审批
        approval = self.approval_service.create_approval(
            execution_id=execution_id,
            node_id=node_id,
            message=message,
            timeout_seconds=timeout_seconds,
        )

        # 返回 paused 状态
        return NodeResult(
            status=NodeStatus.SUCCESS,
            output={
                "status": "paused",
                "approval_id": approval.id,
                "message": message,
                "timeout_seconds": timeout_seconds,
                "expires_at": approval.expires_at.isoformat() if approval.expires_at else None,
            },
        )

    def check_approval(self, approval_id: str) -> NodeResult:
        """检查审批状态

        Args:
            approval_id: 审批 ID

        Returns:
            NodeResult: 审批结果
        """
        approval = self.approval_service.get_approval(approval_id)

        if not approval:
            return NodeResult(
                status=NodeStatus.FAILED,
                error=f"Approval '{approval_id}' not found",
            )

        if approval.status == ApprovalStatus.PENDING:
            # 仍然等待中
            return NodeResult(
                status=NodeStatus.SUCCESS,
                output={
                    "status": "pending",
                    "approval_id": approval_id,
                },
            )

        elif approval.status == ApprovalStatus.APPROVED:
            # 审批通过
            return NodeResult(
                status=NodeStatus.SUCCESS,
                output={
                    "status": "approved",
                    "approval_id": approval_id,
                    "branch": "approved",
                    "comment": getattr(approval, "comment", None),
                    "decided_by": getattr(approval, "decided_by", None),
                },
            )

        elif approval.status == ApprovalStatus.REJECTED:
            # 审批拒绝
            return NodeResult(
                status=NodeStatus.SUCCESS,
                output={
                    "status": "rejected",
                    "approval_id": approval_id,
                    "branch": "rejected",
                    "comment": getattr(approval, "comment", None),
                    "decided_by": getattr(approval, "decided_by", None),
                },
            )

        elif approval.status == ApprovalStatus.TIMEOUT:
            # 审批超时
            return NodeResult(
                status=NodeStatus.SUCCESS,
                output={
                    "status": "timeout",
                    "approval_id": approval_id,
                    "branch": "timeout",
                },
            )

        return NodeResult(
            status=NodeStatus.FAILED,
            error=f"Unknown approval status: {approval.status}",
        )

    def _substitute_variables(
        self,
        text: str,
        context: dict[str, Any],
    ) -> str:
        """替换文本中的变量"""
        pattern = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")

        def replace(match: re.Match) -> str:
            var_name = match.group(1)
            if var_name not in context:
                return match.group(0)
            value = context[var_name]
            return str(value)

        return pattern.sub(replace, text)
