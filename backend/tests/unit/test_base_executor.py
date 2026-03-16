"""BaseExecutor 测试。

REQ-0001-010: BaseExecutor 抽象基类
"""
import pytest
from abc import ABC
from dataclasses import FrozenInstanceError

from app.executors.base import BaseExecutor, NodeResult, NodeStatus


class TestNodeResult:
    """测试 NodeResult 数据类"""

    def test_node_result_importable(self):
        """REQ-0001-010: NodeResult 可导入"""
        from app.executors.base import NodeResult

        assert NodeResult is not None

    def test_node_result_success(self):
        """REQ-0001-010: 成功结果"""
        result = NodeResult(
            status=NodeStatus.SUCCESS,
            output={"message": "hello"},
        )

        assert result.status == NodeStatus.SUCCESS
        assert result.output == {"message": "hello"}
        assert result.error is None

    def test_node_result_failure(self):
        """REQ-0001-010: 失败结果"""
        result = NodeResult(
            status=NodeStatus.FAILED,
            error="Command failed with exit code 1",
        )

        assert result.status == NodeStatus.FAILED
        assert result.error == "Command failed with exit code 1"
        assert result.output is None

    def test_node_result_skipped(self):
        """REQ-0001-010: 跳过结果"""
        result = NodeResult(
            status=NodeStatus.SKIPPED,
            output={"reason": "condition not met"},
        )

        assert result.status == NodeStatus.SKIPPED

    def test_node_result_frozen(self):
        """REQ-0001-010: NodeResult 是不可变的"""
        result = NodeResult(status=NodeStatus.SUCCESS)

        with pytest.raises(FrozenInstanceError):
            result.status = NodeStatus.FAILED


class TestBaseExecutor:
    """测试 BaseExecutor 抽象类"""

    def test_base_executor_importable(self):
        """REQ-0001-010: BaseExecutor 可导入"""
        from app.executors.base import BaseExecutor

        assert BaseExecutor is not None

    def test_cannot_instantiate(self):
        """REQ-0001-010: BaseExecutor 无法直接实例化"""
        from app.executors.base import BaseExecutor

        with pytest.raises(TypeError):
            BaseExecutor()

    def test_subclass_must_implement_execute(self):
        """REQ-0001-010: 子类必须实现 execute 方法"""
        from app.executors.base import BaseExecutor

        class IncompleteExecutor(BaseExecutor):
            pass

        with pytest.raises(TypeError):
            IncompleteExecutor()

    def test_concrete_executor(self):
        """REQ-0001-010: 完整的执行器可以实例化"""
        from app.executors.base import BaseExecutor, NodeResult, NodeStatus

        class DummyExecutor(BaseExecutor):
            def execute(self, node: dict, context: dict) -> NodeResult:
                return NodeResult(status=NodeStatus.SUCCESS, output={"result": "ok"})

        executor = DummyExecutor()
        result = executor.execute({}, {})

        assert result.status == NodeStatus.SUCCESS
        assert result.output == {"result": "ok"}


class TestExecutorRegistry:
    """测试执行器注册表"""

    @pytest.fixture
    def registry(self):
        """创建注册表实例"""
        from app.executors.registry import ExecutorRegistry

        return ExecutorRegistry()

    @pytest.fixture
    def dummy_executor(self):
        """创建测试执行器"""
        from app.executors.base import BaseExecutor, NodeResult, NodeStatus

        class DummyExecutor(BaseExecutor):
            def execute(self, node: dict, context: dict) -> NodeResult:
                return NodeResult(status=NodeStatus.SUCCESS)

        return DummyExecutor()

    def test_registry_importable(self):
        """REQ-0001-010: 注册表可导入"""
        from app.executors.registry import ExecutorRegistry

        assert ExecutorRegistry is not None

    def test_register(self, registry, dummy_executor):
        """REQ-0001-010: 注册执行器"""
        registry.register("dummy", dummy_executor)

        assert registry.get("dummy") == dummy_executor

    def test_get_nonexistent(self, registry):
        """REQ-0001-010: 获取不存在的执行器返回 None"""
        result = registry.get("nonexistent")
        assert result is None

    def test_get_by_node_type(self, registry, dummy_executor):
        """REQ-0001-010: 按节点类型获取执行器"""
        from app.executors.base import BaseExecutor, NodeResult, NodeStatus

        class ScriptExecutor(BaseExecutor):
            def execute(self, node: dict, context: dict) -> NodeResult:
                return NodeResult(status=NodeStatus.SUCCESS)

        script_executor = ScriptExecutor()
        registry.register("script", script_executor)

        result = registry.get("script")
        assert result == script_executor

    def test_list_executors(self, registry, dummy_executor):
        """REQ-0001-010: 列出已注册执行器"""
        registry.register("dummy", dummy_executor)

        executors = registry.list()
        assert "dummy" in executors

    def test_unregister(self, registry, dummy_executor):
        """REQ-0001-010: 注销执行器"""
        registry.register("dummy", dummy_executor)
        registry.unregister("dummy")

        assert registry.get("dummy") is None

    def test_clear(self, registry, dummy_executor):
        """REQ-0001-010: 清空注册表"""
        registry.register("dummy1", dummy_executor)
        registry.register("dummy2", dummy_executor)

        registry.clear()

        assert registry.get("dummy1") is None
        assert registry.get("dummy2") is None
