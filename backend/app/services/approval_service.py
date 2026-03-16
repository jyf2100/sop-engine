"""审批服务。

REQ-0001-014: Human 审批节点执行器

管理审批流程的创建、查询和提交。
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Optional
from enum import Enum

from app.services.event_bus import EventBus, MemoryEventBus


class ApprovalStatus(str, Enum):
    """审批状态"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


@dataclass
class Approval:
    """审批实例"""

    id: str
    execution_id: str
    node_id: str
    message: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    timeout_seconds: int = 3600  # 1 hour default
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    decided_at: Optional[datetime] = None
    decided_by: Optional[str] = None
    comment: Optional[str] = None

    def __post_init__(self):
        if self.expires_at is None:
            self.expires_at = self.created_at + timedelta(seconds=self.timeout_seconds)


class ApprovalService:
    """审批服务

    管理审批流程的创建、查询和提交。
    """

    def __init__(self, event_bus: Optional[EventBus] = None):
        self.event_bus = event_bus or MemoryEventBus()
        self._approvals: dict[str, Approval] = {}

    def create_approval(
        self,
        execution_id: str,
        node_id: str,
        message: str,
        timeout_seconds: int = 3600,
    ) -> Approval:
        """创建审批

        Args:
            execution_id: 执行 ID
            node_id: 节点 ID
            message: 审批消息
            timeout_seconds: 超时秒数

        Returns:
            Approval: 审批实例
        """
        approval_id = f"approval-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow()

        approval = Approval(
            id=approval_id,
            execution_id=execution_id,
            node_id=node_id,
            message=message,
            timeout_seconds=timeout_seconds,
            created_at=now,
            expires_at=now + timedelta(seconds=timeout_seconds),
        )

        self._approvals[approval_id] = approval

        # 发布审批创建事件
        self.event_bus.publish({
            "type": "human.approval_required",
            "approval_id": approval_id,
            "execution_id": execution_id,
            "node_id": node_id,
            "message": message,
            "timeout_seconds": timeout_seconds,
            "timestamp": now.isoformat(),
        })

        return approval

    def get_approval(self, approval_id: str) -> Optional[Approval]:
        """获取审批详情

        Args:
            approval_id: 审批 ID

        Returns:
            Approval: 审批实例，不存在返回 None
        """
        return self._approvals.get(approval_id)

    def submit_approval(
        self,
        approval_id: str,
        approved: bool,
        comment: Optional[str] = None,
        decided_by: Optional[str] = None,
    ) -> Approval:
        """提交审批结果

        Args:
            approval_id: 审批 ID
            approved: 是否批准
            comment: 审批意见
            decided_by: 审批人

        Returns:
            Approval: 更新后的审批实例

        Raises:
            KeyError: 审批不存在
            ValueError: 审批已处理
        """
        approval = self._approvals.get(approval_id)
        if not approval:
            raise KeyError(f"Approval '{approval_id}' not found")

        if approval.status != ApprovalStatus.PENDING:
            raise ValueError(f"Approval already {approval.status.value}")

        # 更新状态
        now = datetime.utcnow()
        approval.status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
        approval.decided_at = now
        approval.decided_by = decided_by
        approval.comment = comment

        # 发布审批结果事件
        self.event_bus.publish({
            "type": "human.approval_decided",
            "approval_id": approval_id,
            "execution_id": approval.execution_id,
            "node_id": approval.node_id,
            "approved": approved,
            "comment": comment,
            "decided_by": decided_by,
            "timestamp": now.isoformat(),
        })

        return approval

    def list_pending(self) -> list[Approval]:
        """列出待审批

        Returns:
            待审批列表
        """
        return [
            a for a in self._approvals.values()
            if a.status == ApprovalStatus.PENDING
        ]

    def check_timeouts(self) -> list[Approval]:
        """检查超时审批

        Returns:
            超时的审批列表
        """
        now = datetime.utcnow()
        timed_out = []

        for approval in self._approvals.values():
            if approval.status == ApprovalStatus.PENDING:
                if approval.expires_at and now > approval.expires_at:
                    approval.status = ApprovalStatus.TIMEOUT
                    timed_out.append(approval)

                    # 发布超时事件
                    self.event_bus.publish({
                        "type": "human.approval_timeout",
                        "approval_id": approval.id,
                        "execution_id": approval.execution_id,
                        "node_id": approval.node_id,
                        "timestamp": now.isoformat(),
                    })

        return timed_out

    def get_by_execution(self, execution_id: str) -> list[Approval]:
        """获取执行的所有审批

        Args:
            execution_id: 执行 ID

        Returns:
            审批列表
        """
        return [
            a for a in self._approvals.values()
            if a.execution_id == execution_id
        ]
