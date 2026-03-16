"""测试数据模型。

REQ-0001-002: 数据库模型定义
"""
import uuid


class TestTemplateModel:
    """REQ-0001-002: Template 模型测试"""

    def test_template_model_exists(self):
        """验证 Template 模型存在"""
        from app.models import Template

        assert Template is not None

    def test_template_fields(self):
        """验证 Template 模型字段"""
        from app.models import Template

        template = Template(
            id="test-flow",
            name="Test Flow",
            version="1.0.0",
            yaml_content="nodes: {}",
        )
        assert template.id == "test-flow"
        assert template.name == "Test Flow"
        assert template.version == "1.0.0"
        assert template.yaml_content == "nodes: {}"


class TestExecutionModel:
    """REQ-0001-002: Execution 模型测试"""

    def test_execution_model_exists(self):
        """验证 Execution 模型存在"""
        from app.models import Execution

        assert Execution is not None

    def test_execution_fields(self):
        """验证 Execution 模型字段"""
        from app.models import Execution

        exec_id = str(uuid.uuid4())
        execution = Execution(
            id=exec_id,
            template_id="test-flow",
            status="pending",
            params={"key": "value"},
        )
        assert execution.id == exec_id
        assert execution.template_id == "test-flow"
        assert execution.status == "pending"
        assert execution.params == {"key": "value"}


class TestNodeExecutionModel:
    """REQ-0001-002: NodeExecution 模型测试"""

    def test_node_execution_model_exists(self):
        """验证 NodeExecution 模型存在"""
        from app.models import NodeExecution

        assert NodeExecution is not None

    def test_node_execution_fields(self):
        """验证 NodeExecution 模型字段"""
        from app.models import NodeExecution

        node_exec = NodeExecution(
            id="node-exec-1",
            execution_id="exec-1",
            node_id="start",
            status="pending",
        )
        assert node_exec.id == "node-exec-1"
        assert node_exec.execution_id == "exec-1"
        assert node_exec.node_id == "start"
        assert node_exec.status == "pending"


class TestAgentModel:
    """REQ-0001-002: Agent 模型测试"""

    def test_agent_model_exists(self):
        """验证 Agent 模型存在"""
        from app.models import Agent

        assert Agent is not None

    def test_agent_fields(self):
        """验证 Agent 模型字段"""
        from app.models import Agent

        agent = Agent(
            id="security-scanner",
            name="Security Scanner",
            workspace_path="/workspace/security-scanner",
            llm_config={"primary": "claude-3-5-sonnet"},
            sandbox_config={"mode": "non-main"},
            tools_config={"allow": ["read", "write"]},
        )
        assert agent.id == "security-scanner"
        assert agent.name == "Security Scanner"
        assert agent.workspace_path == "/workspace/security-scanner"
        assert agent.llm_config == {"primary": "claude-3-5-sonnet"}
        assert agent.sandbox_config == {"mode": "non-main"}
        assert agent.tools_config == {"allow": ["read", "write"]}


class TestAgentConfigFileModel:
    """REQ-0001-002: AgentConfigFile 模型测试"""

    def test_agent_config_file_model_exists(self):
        """验证 AgentConfigFile 模型存在"""
        from app.models import AgentConfigFile

        assert AgentConfigFile is not None

    def test_agent_config_file_fields(self):
        """验证 AgentConfigFile 模型字段"""
        from app.models import AgentConfigFile

        config_file = AgentConfigFile(
            id="cfg-001",
            agent_id="security-scanner",
            file_type="AGENTS.md",
            content="# Agent Instructions\n...",
        )
        assert config_file.id == "cfg-001"
        assert config_file.agent_id == "security-scanner"
        assert config_file.file_type == "AGENTS.md"
        assert config_file.content == "# Agent Instructions\n..."


class TestModelImports:
    """测试模型导入"""

    def test_all_models_importable(self):
        """验证所有模型可从 app.models 导入"""
        from app.models import (
            Agent,
            AgentConfigFile,
            Execution,
            NodeExecution,
            Template,
        )

        assert Template is not None
        assert Execution is not None
        assert NodeExecution is not None
        assert Agent is not None
        assert AgentConfigFile is not None
