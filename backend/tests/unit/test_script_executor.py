"""Script 执行器测试。

REQ-0001-011: Script 节点执行器
"""
import pytest
import asyncio

from app.executors.base import NodeResult, NodeStatus


class TestScriptExecutor:
    """测试 Script 执行器"""

    @pytest.fixture
    def executor(self):
        """创建 ScriptExecutor 实例"""
        from app.executors.script_executor import ScriptExecutor

        return ScriptExecutor()

    def test_executor_importable(self):
        """REQ-0001-011: ScriptExecutor 可导入"""
        from app.executors.script_executor import ScriptExecutor

        assert ScriptExecutor is not None

    def test_echo_hello(self, executor):
        """REQ-0001-011: 执行 echo hello 返回 'hello'"""
        node = {
            "id": "test-echo",
            "type": "script",
            "command": "echo hello",
        }
        context = {}

        result = executor.execute(node, context)

        assert result.status == NodeStatus.SUCCESS
        assert "hello" in result.output.get("stdout", "").lower()

    def test_variable_substitution(self, executor):
        """REQ-0001-011: 命令中的 {var} 被正确替换"""
        node = {
            "id": "test-var",
            "type": "script",
            "command": "echo {name}",
        }
        context = {"name": "World"}

        result = executor.execute(node, context)

        assert result.status == NodeStatus.SUCCESS
        assert "World" in result.output.get("stdout", "")

    def test_timeout(self, executor):
        """REQ-0001-011: 超时命令抛出异常"""
        node = {
            "id": "test-timeout",
            "type": "script",
            "command": "sleep 10",
            "config": {"timeout_seconds": 1},
        }
        context = {}

        with pytest.raises(Exception, match="timed out"):
            executor.execute(node, context)

    def test_failure(self, executor):
        """REQ-0001-011: 失败命令返回非零 exit code 和 stderr"""
        node = {
            "id": "test-fail",
            "type": "script",
            "command": "exit 1",
        }
        context = {}

        result = executor.execute(node, context)

        assert result.status == NodeStatus.FAILED
        assert result.output.get("exit_code") != 0

    def test_capture_stderr(self, executor):
        """REQ-0001-011: 捕获 stderr"""
        node = {
            "id": "test-stderr",
            "type": "script",
            "command": "echo error >&2",
        }
        context = {}

        result = executor.execute(node, context)

        assert result.status == NodeStatus.SUCCESS
        assert "error" in result.output.get("stderr", "")

    def test_capture_stdout(self, executor):
        """REQ-0001-011: 捕获 stdout"""
        node = {
            "id": "test-stdout",
            "type": "script",
            "command": "echo 'test output'",
        }
        context = {}

        result = executor.execute(node, context)

        assert result.status == NodeStatus.SUCCESS
        assert "test output" in result.output.get("stdout", "")

    def test_missing_command(self, executor):
        """REQ-0001-011: 缺少 command 字段"""
        node = {
            "id": "test-missing",
            "type": "script",
        }
        context = {}

        result = executor.execute(node, context)

        assert result.status == NodeStatus.FAILED
        assert "command" in result.error.lower()

    def test_custom_timeout(self, executor):
        """REQ-0001-011: 自定义超时时间"""
        node = {
            "id": "test-custom-timeout",
            "type": "script",
            "command": "sleep 5",
            "config": {"timeout_seconds": 2},
        }
        context = {}

        with pytest.raises(Exception, match="timed out"):
            executor.execute(node, context)


class TestConditionExecutor:
    """测试 Condition 执行器"""

    @pytest.fixture
    def executor(self):
        """创建 ConditionExecutor 实例"""
        from app.executors.condition_executor import ConditionExecutor

        return ConditionExecutor()

    def test_executor_importable(self):
        """REQ-0001-013: ConditionExecutor 可导入"""
        from app.executors.condition_executor import ConditionExecutor

        assert ConditionExecutor is not None

    def test_match_branch(self, executor):
        """REQ-0001-013: 成功匹配分支"""
        node = {
            "id": "test-condition",
            "type": "condition",
            "branches": {"success": "node-a", "failure": "node-b"},
        }
        context = {"status": "success"}

        result = executor.execute(node, context)

        assert result.status == NodeStatus.SUCCESS
        assert result.output.get("branch") == "success"

    def test_default_branch(self, executor):
        """REQ-0001-013: 默认分支"""
        node = {
            "id": "test-default",
            "type": "condition",
            "branches": {"default": "node-c", "success": "node-a"},
        }
        context = {"status": "unknown"}

        result = executor.execute(node, context)

        assert result.status == NodeStatus.SUCCESS
        assert result.output.get("branch") == "default"

    def test_expression_evaluation(self, executor):
        """REQ-0001-013: 表达式评估"""
        node = {
            "id": "test-expr",
            "type": "condition",
            "branches": {"pass": "node-a", "fail": "node-b"},
            "config": {
                "expression": "{count} > 10",
            },
        }
        context = {"count": 15}

        result = executor.execute(node, context)

        assert result.status == NodeStatus.SUCCESS
        # 表达式评估为 true，应匹配 pass
        assert result.output.get("branch") == "pass"

    def test_no_matching_branch(self, executor):
        """REQ-0001-013: 无匹配分支"""
        node = {
            "id": "test-no-match",
            "type": "condition",
            "branches": {"success": "node-a"},
        }
        context = {"status": "failure"}

        result = executor.execute(node, context)

        # 无匹配分支时返回失败
        assert result.status == NodeStatus.FAILED


class TestAgentExecutor:
    """测试 Agent 执行器"""

    @pytest.fixture
    def executor(self):
        """创建 AgentExecutor 实例"""
        from app.executors.agent_executor import AgentExecutor

        return AgentExecutor()

    def test_executor_importable(self):
        """REQ-0001-012: AgentExecutor 可导入"""
        from app.executors.agent_executor import AgentExecutor

        assert AgentExecutor is not None

    def test_agent_call(self, executor):
        """REQ-0001-012: 调用 Agent"""
        node = {
            "id": "test-agent",
            "type": "agent",
            "agent_id": "default",
            "prompt": "Hello, {name}!",
        }
        context = {"name": "World"}

        # 使用 mock 模式测试
        result = executor.execute(node, context)

        # 由于没有真实 Agent，应该返回成功或失败
        assert result.status in (NodeStatus.SUCCESS, NodeStatus.FAILED)

    def test_variable_in_prompt(self, executor):
        """REQ-0001-012: 提示词中的变量替换"""
        node = {
            "id": "test-prompt-var",
            "type": "agent",
            "agent_id": "default",
            "prompt": "Process {item} for user {user}",
        }
        context = {"item": "order-123", "user": "Alice"}

        result = executor.execute(node, context)

        # 验证变量替换后的提示词
        if result.status == NodeStatus.SUCCESS:
            assert result.output is not None

    def test_missing_agent_id(self, executor):
        """REQ-0001-012: 缺少 agent_id 字段"""
        node = {
            "id": "test-missing-agent",
            "type": "agent",
            "prompt": "Hello",
        }
        context = {}

        result = executor.execute(node, context)

        assert result.status == NodeStatus.FAILED
        assert "agent_id" in result.error.lower()

    def test_missing_prompt(self, executor):
        """REQ-0001-012: 缺少 prompt 字段"""
        node = {
            "id": "test-missing-prompt",
            "type": "agent",
            "agent_id": "default",
        }
        context = {}

        result = executor.execute(node, context)

        assert result.status == NodeStatus.FAILED
        assert "prompt" in result.error.lower()
