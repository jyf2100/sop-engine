"""FlowEngine 测试。

REQ-0001-009: FlowEngine 核心
"""
import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

from app.executors.base import NodeResult, NodeStatus


class TestFlowEngine:
    """测试流程引擎"""

    @pytest.fixture
    def flow_engine(self):
        """创建 FlowEngine 实例"""
        from app.services.flow_engine import FlowEngine

        return FlowEngine()

    @pytest.fixture
    def event_bus(self, flow_engine):
        """获取事件总线"""
        return flow_engine.event_bus

    @pytest.fixture
    def context_manager(self, flow_engine):
        """获取上下文管理器"""
        return flow_engine.context_manager

    @pytest.fixture
    def sample_template(self):
        """示例模板"""
        from app.models.flow_template import FlowTemplate, FlowNode, NodeType

        return FlowTemplate(
            id="test-flow",
            name="Test Flow",
            nodes={
                "start": FlowNode(id="start", type=NodeType.START, next="step1"),
                "step1": FlowNode(
                    id="step1",
                    type=NodeType.SCRIPT,
                    command="echo hello",
                    output_var="result",
                    next="end",
                ),
                "end": FlowNode(id="end", type=NodeType.END),
            },
        )

    def test_flow_engine_importable(self):
        """REQ-0001-009: FlowEngine 可导入"""
        from app.services.flow_engine import FlowEngine

        assert FlowEngine is not None

    def test_start_execution(self, flow_engine, sample_template, event_bus):
        """REQ-0001-009: start_execution 创建 Execution 并发布事件"""
        # Mock 执行器
        from app.executors.base import BaseExecutor

        class DummyExecutor(BaseExecutor):
            def execute(self, node, context):
                return NodeResult(status=NodeStatus.SUCCESS, output={"stdout": "hello"})

        flow_engine.executor_registry.register("script", DummyExecutor())

        # 启动执行
        execution = flow_engine.start_execution(sample_template, {"name": "test"})

        assert execution is not None
        assert execution.status == "running"
        assert execution.current_node == "start"

        # 消费事件验证
        events = event_bus.consume(count=1, block_ms=100)
        assert len(events) >= 1
        assert events[0]["type"] == "execution.started"

    def test_execute_node(self, flow_engine, sample_template, event_bus, context_manager):
        """REQ-0001-009: execute_node 发布 node.started/completed 事件"""
        from app.executors.base import BaseExecutor
        from app.models.flow_template import NodeType

        class DummyExecutor(BaseExecutor):
            def execute(self, node, context):
                return NodeResult(status=NodeStatus.SUCCESS, output={"stdout": "hello"})

        flow_engine.executor_registry.register("script", DummyExecutor())

        execution = flow_engine.start_execution(sample_template, {})

        # 执行节点
        node = sample_template.nodes["step1"]
        result = flow_engine.execute_node(execution, node)

        assert result.status == NodeStatus.SUCCESS

        # 验证事件
        events = event_bus.consume(count=10, block_ms=500)
        event_types = [e["type"] for e in events]
        assert "node.started" in event_types
        assert "node.completed" in event_types

    def test_transition(self, flow_engine, sample_template):
        """REQ-0001-009: transition 正确计算下一节点"""
        from app.executors.base import BaseExecutor

        class DummyExecutor(BaseExecutor):
            def execute(self, node, context):
                return NodeResult(status=NodeStatus.SUCCESS, output={"stdout": "hello"})

        flow_engine.executor_registry.register("script", DummyExecutor())

        execution = flow_engine.start_execution(sample_template, {})
        flow_engine._set_current_node(execution, "start")

        # 从 start 节点转换
        result = NodeResult(status=NodeStatus.SUCCESS)
        next_node_id = flow_engine.transition(execution, result)

        assert next_node_id == "step1"

    def test_handle_failure(self, flow_engine, sample_template, event_bus):
        """REQ-0001-009: handle_failure 正确处理异常"""
        from app.executors.base import BaseExecutor

        class FailingExecutor(BaseExecutor):
            def execute(self, node, context):
                return NodeResult(status=NodeStatus.FAILED, error="Something went wrong")

        flow_engine.executor_registry.register("script", FailingExecutor())

        execution = flow_engine.start_execution(sample_template, {})

        # 执行失败的节点
        node = sample_template.nodes["step1"]
        result = flow_engine.execute_node(execution, node)

        assert result.status == NodeStatus.FAILED

        # 处理失败
        flow_engine.handle_failure(execution, "Test error")

        assert execution.status == "failed"

    def test_run_to_completion(self, flow_engine, sample_template):
        """REQ-0001-009: 运行流程直到完成"""
        from app.executors.base import BaseExecutor

        class FastExecutor(BaseExecutor):
            def execute(self, node, context):
                return NodeResult(status=NodeStatus.SUCCESS, output={"stdout": "ok"})

        flow_engine.executor_registry.register("script", FastExecutor())
        flow_engine.executor_registry.register("start", FastExecutor())
        flow_engine.executor_registry.register("end", FastExecutor())

        execution = flow_engine.start_execution(sample_template, {})

        # 运行直到完成
        final_execution = flow_engine.run(execution)

        assert final_execution.status == "completed"

    def test_context_propagation(self, flow_engine, sample_template, context_manager):
        """REQ-0001-009: 上下文在节点间正确传递"""
        from app.executors.base import BaseExecutor

        class ContextExecutor(BaseExecutor):
            def execute(self, node, context):
                # 将输出保存到上下文
                output_var = node.get("output_var")
                if output_var:
                    return NodeResult(
                        status=NodeStatus.SUCCESS,
                        output={"value": "test-output"},
                    )
                return NodeResult(status=NodeStatus.SUCCESS)

        flow_engine.executor_registry.register("script", ContextExecutor())
        flow_engine.executor_registry.register("start", ContextExecutor())
        flow_engine.executor_registry.register("end", ContextExecutor())

        execution = flow_engine.start_execution(sample_template, {"name": "initial"})

        # 运行流程
        flow_engine.run(execution)

        # 验证上下文
        assert context_manager.has(execution.id, "result")


class TestFlowEngineCondition:
    """测试条件节点处理"""

    @pytest.fixture
    def flow_engine(self):
        from app.services.flow_engine import FlowEngine

        return FlowEngine()

    @pytest.fixture
    def condition_template(self):
        """带条件分支的模板"""
        from app.models.flow_template import FlowTemplate, FlowNode, NodeType

        return FlowTemplate(
            id="condition-flow",
            name="Condition Flow",
            nodes={
                "start": FlowNode(id="start", type=NodeType.START, next="check"),
                "check": FlowNode(
                    id="check",
                    type=NodeType.CONDITION,
                    branches={"success": "end", "failure": "retry"},
                ),
                "retry": FlowNode(
                    id="retry",
                    type=NodeType.SCRIPT,
                    command="echo retry",
                    next="end",
                ),
                "end": FlowNode(id="end", type=NodeType.END),
            },
        )

    def test_transition_condition_success(self, flow_engine, condition_template):
        """REQ-0001-009: 条件节点转换到 success 分支"""
        from app.executors.base import BaseExecutor

        class ConditionExecutor(BaseExecutor):
            def execute(self, node, context):
                return NodeResult(
                    status=NodeStatus.SUCCESS,
                    output={"branch": "success"},
                )

        flow_engine.executor_registry.register("condition", ConditionExecutor())

        execution = flow_engine._create_execution(condition_template, {})
        flow_engine._set_current_node(execution, "check")

        result = NodeResult(status=NodeStatus.SUCCESS, output={"branch": "success"})
        next_node = flow_engine.transition(execution, result)

        assert next_node == "end"

    def test_transition_condition_failure(self, flow_engine, condition_template):
        """REQ-0001-009: 条件节点转换到 failure 分支"""
        from app.executors.base import BaseExecutor

        execution = flow_engine._create_execution(condition_template, {})
        flow_engine._set_current_node(execution, "check")

        result = NodeResult(status=NodeStatus.SUCCESS, output={"branch": "failure"})
        next_node = flow_engine.transition(execution, result)

        assert next_node == "retry"
