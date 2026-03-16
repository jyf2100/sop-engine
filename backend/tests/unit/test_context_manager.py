"""ContextManager 测试。

REQ-0001-008: Context 上下文管理
"""
import pytest


class TestContextManager:
    """测试上下文管理器"""

    @pytest.fixture
    def context_manager(self):
        """创建 ContextManager 实例"""
        from app.services.context_manager import ContextManager

        return ContextManager()

    def test_context_manager_importable(self):
        """REQ-0001-008: ContextManager 可导入"""
        from app.services.context_manager import ContextManager

        assert ContextManager is not None

    def test_get_set(self, context_manager):
        """REQ-0001-008: set 后 get 可读取"""
        execution_id = "exec-001"

        # 设置变量
        context_manager.set(execution_id, "user_name", "Alice")
        context_manager.set(execution_id, "count", 42)

        # 读取变量
        assert context_manager.get(execution_id, "user_name") == "Alice"
        assert context_manager.get(execution_id, "count") == 42

    def test_get_nonexistent_variable(self, context_manager):
        """REQ-0001-008: 变量不存在时抛出异常"""
        from app.services.context_manager import ContextVariableError

        with pytest.raises(ContextVariableError, match="not found"):
            context_manager.get("exec-002", "nonexistent")

    def test_resolve_variables(self, context_manager):
        """REQ-0001-008: resolve_variables 正确替换 {var_name}"""
        execution_id = "exec-003"

        context_manager.set(execution_id, "name", "World")
        context_manager.set(execution_id, "count", 5)

        # 解析模板变量
        template = "Hello, {name}! Count: {count}"
        result = context_manager.resolve_variables(execution_id, template)

        assert result == "Hello, World! Count: 5"

    def test_resolve_variables_missing(self, context_manager):
        """REQ-0001-008: 变量不存在时抛出 ContextVariableError"""
        from app.services.context_manager import ContextVariableError

        execution_id = "exec-004"
        context_manager.set(execution_id, "name", "Test")

        # 模板引用不存在的变量
        template = "Hello, {name}! Missing: {nonexistent}"

        with pytest.raises(ContextVariableError, match="nonexistent"):
            context_manager.resolve_variables(execution_id, template)

    def test_get_all(self, context_manager):
        """REQ-0001-008: 获取完整上下文"""
        execution_id = "exec-005"

        context_manager.set(execution_id, "a", 1)
        context_manager.set(execution_id, "b", 2)
        context_manager.set(execution_id, "c", 3)

        ctx = context_manager.get_all(execution_id)
        assert ctx == {"a": 1, "b": 2, "c": 3}

    def test_delete(self, context_manager):
        """REQ-0001-008: 删除变量"""
        execution_id = "exec-006"

        context_manager.set(execution_id, "temp", "value")
        assert context_manager.get(execution_id, "temp") == "value"

        context_manager.delete(execution_id, "temp")

        from app.services.context_manager import ContextVariableError

        with pytest.raises(ContextVariableError):
            context_manager.get(execution_id, "temp")

    def test_clear_execution(self, context_manager):
        """REQ-0001-008: 清空执行上下文"""
        execution_id = "exec-007"

        context_manager.set(execution_id, "a", 1)
        context_manager.set(execution_id, "b", 2)

        context_manager.clear(execution_id)

        from app.services.context_manager import ContextVariableError

        with pytest.raises(ContextVariableError):
            context_manager.get(execution_id, "a")

    def test_resolve_nested_variables(self, context_manager):
        """REQ-0001-008: 解析嵌套的模板变量"""
        execution_id = "exec-008"

        context_manager.set(execution_id, "first", "John")
        context_manager.set(execution_id, "last", "Doe")

        template = "Full name: {first} {last}"
        result = context_manager.resolve_variables(execution_id, template)

        assert result == "Full name: John Doe"

    def test_resolve_json_template(self, context_manager):
        """REQ-0001-008: 解析 JSON 模板中的变量"""
        import json

        execution_id = "exec-009"

        context_manager.set(execution_id, "agent_id", "agent-001")
        context_manager.set(execution_id, "message", "Hello")

        template = json.dumps({
            "agent": "{agent_id}",
            "prompt": "{message}",
        })

        result = context_manager.resolve_variables(execution_id, template)
        parsed = json.loads(result)

        assert parsed["agent"] == "agent-001"
        assert parsed["prompt"] == "Hello"

    def test_isolation_between_executions(self, context_manager):
        """REQ-0001-008: 不同执行的上下文隔离"""
        exec1 = "exec-isolation-1"
        exec2 = "exec-isolation-2"

        context_manager.set(exec1, "shared", "value1")
        context_manager.set(exec2, "shared", "value2")

        assert context_manager.get(exec1, "shared") == "value1"
        assert context_manager.get(exec2, "shared") == "value2"

    def test_set_default(self, context_manager):
        """REQ-0001-008: 设置默认值"""
        execution_id = "exec-010"

        # 设置默认值（变量不存在时）
        context_manager.set_default(execution_id, "timeout", 30)

        assert context_manager.get(execution_id, "timeout") == 30

        # 再次设置默认值（变量已存在，不覆盖）
        context_manager.set_default(execution_id, "timeout", 60)

        assert context_manager.get(execution_id, "timeout") == 30
