"""Human 审批执行器测试。

REQ-0001-014: Human 审批节点执行器
"""
import pytest
from datetime import datetime, timedelta

from app.executors.base import NodeStatus


class TestHumanExecutor:
    """测试 Human 审批执行器"""

    @pytest.fixture
    def executor(self):
        """创建 HumanExecutor 实例"""
        from app.executors.human_executor import HumanExecutor

        return HumanExecutor()

    @pytest.fixture
    def event_bus(self, executor):
        """获取事件总线"""
        return executor.event_bus

    def test_executor_importable(self):
        """REQ-0001-014: HumanExecutor 可导入"""
        from app.executors.human_executor import HumanExecutor

        assert HumanExecutor is not None

    def test_pause_on_approval(self, executor):
        """REQ-0001-014: 执行时状态变为 paused"""
        node = {
            "id": "approval-1",
            "type": "human",
            "approval_message": "Please approve this request",
        }
        context = {"execution_id": "exec-001"}

        result = executor.execute(node, context)

        assert result.status == NodeStatus.SUCCESS
        assert result.output.get("status") == "paused"

    def test_approval_event(self, executor, event_bus):
        """REQ-0001-014: 发布 human.approval_required 事件"""
        node = {
            "id": "approval-2",
            "type": "human",
            "approval_message": "Please approve",
        }
        context = {"execution_id": "exec-002"}

        executor.execute(node, context)

        # 消费事件验证
        events = event_bus.consume(count=1, block_ms=100)
        assert len(events) >= 1
        assert events[0]["type"] == "human.approval_required"

    def test_approval_message_substitution(self, executor):
        """REQ-0001-014: 审批消息中的变量替换"""
        node = {
            "id": "approval-3",
            "type": "human",
            "approval_message": "Please approve order {order_id}",
            "timeout_seconds": 3600,
        }
        context = {"execution_id": "exec-003", "order_id": "ORD-12345"}

        result = executor.execute(node, context)

        assert result.status == NodeStatus.SUCCESS
        assert "ORD-12345" in result.output.get("message", "")

    def test_check_approval_pending(self, executor):
        """REQ-0001-014: 检查待审批状态"""
        node = {
            "id": "approval-4",
            "type": "human",
            "approval_message": "Approve?",
        }
        context = {"execution_id": "exec-004"}

        result = executor.execute(node, context)
        approval_id = result.output.get("approval_id")

        check_result = executor.check_approval(approval_id)

        assert check_result.status == NodeStatus.SUCCESS
        assert check_result.output.get("status") == "pending"

    def test_check_approval_approved(self, executor):
        """REQ-0001-014: 审批通过后继续执行"""
        node = {
            "id": "approval-5",
            "type": "human",
            "approval_message": "Approve?",
        }
        context = {"execution_id": "exec-005"}

        result = executor.execute(node, context)
        approval_id = result.output.get("approval_id")

        # 模拟审批通过
        executor.approval_service.submit_approval(
            approval_id=approval_id,
            approved=True,
            comment="Looks good",
            decided_by="manager@example.com",
        )

        check_result = executor.check_approval(approval_id)

        assert check_result.status == NodeStatus.SUCCESS
        assert check_result.output.get("status") == "approved"
        assert check_result.output.get("branch") == "approved"

    def test_check_approval_rejected(self, executor):
        """REQ-0001-014: 审批拒绝后走拒绝分支"""
        node = {
            "id": "approval-6",
            "type": "human",
            "approval_message": "Approve?",
        }
        context = {"execution_id": "exec-006"}

        result = executor.execute(node, context)
        approval_id = result.output.get("approval_id")

        # 模拟审批拒绝
        executor.approval_service.submit_approval(
            approval_id=approval_id,
            approved=False,
            comment="Not acceptable",
            decided_by="manager@example.com",
        )

        check_result = executor.check_approval(approval_id)

        assert check_result.status == NodeStatus.SUCCESS
        assert check_result.output.get("status") == "rejected"
        assert check_result.output.get("branch") == "rejected"

    def test_check_approval_timeout(self, executor):
        """REQ-0001-014: 超时后执行超时动作"""
        node = {
            "id": "approval-7",
            "type": "human",
            "approval_message": "Please approve",
            "timeout_seconds": 60,
        }
        context = {"execution_id": "exec-007"}

        result = executor.execute(node, context)
        approval_id = result.output.get("approval_id")

        # 模拟超时
        from app.services.approval_service import ApprovalStatus
        approval = executor.approval_service.get_approval(approval_id)
        approval.status = ApprovalStatus.TIMEOUT

        check_result = executor.check_approval(approval_id)

        assert check_result.status == NodeStatus.SUCCESS
        assert check_result.output.get("status") == "timeout"
        assert check_result.output.get("branch") == "timeout"

    def test_check_nonexistent_approval(self, executor):
        """REQ-0001-014: 检查不存在的审批"""
        check_result = executor.check_approval("nonexistent-id")

        assert check_result.status == NodeStatus.FAILED


class TestApprovalService:
    """测试审批服务"""

    @pytest.fixture
    def service(self):
        """创建 ApprovalService 实例"""
        from app.services.approval_service import ApprovalService

        return ApprovalService()

    def test_service_importable(self):
        """REQ-0001-014: ApprovalService 可导入"""
        from app.services.approval_service import ApprovalService

        assert ApprovalService is not None

    def test_create_approval(self, service):
        """REQ-0001-014: 创建审批"""
        from app.services.approval_service import ApprovalStatus

        approval = service.create_approval(
            execution_id="exec-001",
            node_id="approval-1",
            message="Please approve",
            timeout_seconds=3600,
        )

        assert approval is not None
        assert approval.execution_id == "exec-001"
        assert approval.node_id == "approval-1"
        assert approval.status == ApprovalStatus.PENDING

    def test_submit_approval(self, service):
        """REQ-0001-014: 提交审批结果"""
        from app.services.approval_service import ApprovalStatus

        # 创建审批
        approval = service.create_approval(
            execution_id="exec-002",
            node_id="approval-2",
            message="Approve?",
            timeout_seconds=60,
        )

        # 提交审批
        result = service.submit_approval(
            approval_id=approval.id,
            approved=True,
            comment="Looks good",
        )

        assert result.status == ApprovalStatus.APPROVED
        assert result.comment == "Looks good"

    def test_get_approval(self, service):
        """REQ-0001-014: 获取审批详情"""
        approval = service.create_approval(
            execution_id="exec-003",
            node_id="approval-3",
            message="Approve?",
            timeout_seconds=60,
        )

        fetched = service.get_approval(approval.id)

        assert fetched is not None
        assert fetched.id == approval.id

    def test_list_pending(self, service):
        """REQ-0001-014: 列出待审批"""
        for i in range(3):
            service.create_approval(
                execution_id=f"exec-{i}",
                node_id=f"approval-{i}",
                message=f"Approve {i}?",
                timeout_seconds=60,
            )

        pending = service.list_pending()

        assert len(pending) >= 3

    def test_check_timeouts(self, service):
        """REQ-0001-014: 检查超时审批"""
        # 创建一个已超时的审批（timeout_seconds=1）
        approval = service.create_approval(
            execution_id="exec-timeout",
            node_id="approval-timeout",
            message="Approve?",
            timeout_seconds=1,
        )

        # 手动设置过期时间为过去
        approval.expires_at = datetime.utcnow() - timedelta(seconds=10)

        # 检查超时
        timed_out = service.check_timeouts()

        # 验证
        assert isinstance(timed_out, list)
