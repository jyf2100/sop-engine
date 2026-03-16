"""AgentService 单元测试。

REQ-0001-003: Agent 配置管理
"""
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestAgentServiceExists:
    """验证 AgentService 存在"""

    def test_agent_service_importable(self):
        """REQ-0001-003: AgentService 可导入"""
        from app.services.agent_service import AgentService

        assert AgentService is not None

    def test_openclaw_sync_importable(self):
        """REQ-0001-003: OpenClawSync 可导入"""
        from app.services.openclaw_sync import OpenClawSync

        assert OpenClawSync is not None


class TestAgentCreate:
    """测试 Agent 创建"""

    @pytest.fixture
    def temp_workspace(self):
        """临时工作目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def agent_service(self, temp_workspace):
        """创建 AgentService 实例"""
        from app.services.agent_service import AgentService

        return AgentService(workspace_root=temp_workspace)

    def test_create_agent_with_required_fields(self, agent_service):
        """REQ-0001-003: 创建 Agent 时必须有基本字段"""
        agent = agent_service.create_agent(
            agent_id="test-agent",
            name="Test Agent",
        )
        assert agent.id == "test-agent"
        assert agent.name == "Test Agent"

    def test_create_agent_generates_default_files(self, agent_service, temp_workspace):
        """REQ-0001-003: 创建 Agent 时生成默认配置文件"""
        agent = agent_service.create_agent(
            agent_id="test-agent",
            name="Test Agent",
        )

        # 验证配置文件已创建
        agent_dir = temp_workspace / "test-agent"
        assert (agent_dir / "AGENTS.md").exists()
        assert (agent_dir / "SOUL.md").exists()
        assert (agent_dir / "USER.md").exists()
        assert (agent_dir / "IDENTITY.md").exists()

    def test_create_agent_with_custom_config(self, agent_service):
        """REQ-0001-003: 创建 Agent 时支持自定义配置"""
        agent = agent_service.create_agent(
            agent_id="custom-agent",
            name="Custom Agent",
            llm_config={"primary": "claude-3-opus", "fallbacks": ["claude-3-sonnet"]},
            sandbox_config={"mode": "all"},
            tools_config={"allow": ["read", "write", "execute"]},
        )
        assert agent.llm_config["primary"] == "claude-3-opus"
        assert agent.sandbox_config["mode"] == "all"

    def test_create_agent_with_invalid_id_raises_error(self, agent_service):
        """REQ-0001-003: 创建重复 Agent 抛出异常"""
        agent_service.create_agent(agent_id="test-agent", name="First Agent")
        with pytest.raises(ValueError, match="already exists"):
            agent_service.create_agent(
                agent_id="test-agent",  # 重复 ID
                name="Second Agent",
            )


class TestAgentUpdate:
    """测试 Agent 更新"""

    @pytest.fixture
    def temp_workspace(self):
        """临时工作目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def agent_service(self, temp_workspace):
        """创建 AgentService 实例"""
        from app.services.agent_service import AgentService

        return AgentService(workspace_root=temp_workspace)

    def test_update_agent_name(self, agent_service):
        """REQ-0001-003: 更新 Agent 名称"""
        agent_service.create_agent(agent_id="test-agent", name="Original Name")
        agent = agent_service.update_agent(
            agent_id="test-agent",
            name="Updated Name",
        )
        assert agent.name == "Updated Name"

    def test_update_agent_config_file(self, agent_service, temp_workspace):
        """REQ-0001-003: 更新配置文件内容"""
        agent_service.create_agent(agent_id="test-agent", name="Test Agent")

        new_content = "# Updated AGENTS.md\nNew instructions here."
        agent_service.update_config_file(
            agent_id="test-agent",
            file_type="AGENTS.md",
            content=new_content,
        )

        # 验证文件已更新
        agent_dir = temp_workspace / "test-agent"
        content = (agent_dir / "AGENTS.md").read_text()
        assert "Updated AGENTS.md" in content

    def test_update_nonexistent_agent_raises_error(self, agent_service):
        """REQ-0001-003: 更新不存在的 Agent 抛出异常"""
        with pytest.raises(KeyError, match="not found"):
            agent_service.update_agent(agent_id="nonexistent", name="New Name")


class TestAgentDelete:
    """测试 Agent 删除"""

    @pytest.fixture
    def temp_workspace(self):
        """临时工作目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def agent_service(self, temp_workspace):
        """创建 AgentService 实例"""
        from app.services.agent_service import AgentService

        return AgentService(workspace_root=temp_workspace)

    def test_delete_agent_removes_workspace(self, agent_service, temp_workspace):
        """REQ-0001-003: 删除 Agent 时清理 workspace 目录"""
        agent_service.create_agent(agent_id="test-agent", name="Test Agent")

        # 确认目录存在
        agent_dir = temp_workspace / "test-agent"
        assert agent_dir.exists()

        # 删除
        agent_service.delete_agent("test-agent")

        # 验证目录已删除
        assert not agent_dir.exists()

    def test_delete_nonexistent_agent_raises_error(self, agent_service):
        """REQ-0001-003: 删除不存在的 Agent 抛出异常"""
        with pytest.raises(KeyError, match="not found"):
            agent_service.delete_agent("nonexistent")


class TestAgentList:
    """测试 Agent 列表"""

    @pytest.fixture
    def temp_workspace(self):
        """临时工作目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def agent_service(self, temp_workspace):
        """创建 AgentService 实例"""
        from app.services.agent_service import AgentService

        return AgentService(workspace_root=temp_workspace)

    def test_list_agents(self, agent_service):
        """REQ-0001-003: 列出所有 Agent"""
        agent_service.create_agent(agent_id="agent-1", name="Agent 1")
        agent_service.create_agent(agent_id="agent-2", name="Agent 2")

        agents = agent_service.list_agents()
        assert len(agents) == 2
        agent_ids = [a.id for a in agents]
        assert "agent-1" in agent_ids
        assert "agent-2" in agent_ids

    def test_get_agent_by_id(self, agent_service):
        """REQ-0001-003: 根据 ID 获取 Agent"""
        agent_service.create_agent(
            agent_id="test-agent",
            name="Test Agent",
        )

        agent = agent_service.get_agent("test-agent")
        assert agent.id == "test-agent"
        assert agent.name == "Test Agent"


class TestAgentConfigFiles:
    """测试配置文件管理"""

    @pytest.fixture
    def temp_workspace(self):
        """临时工作目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def agent_service(self, temp_workspace):
        """创建 AgentService 实例"""
        from app.services.agent_service import AgentService

        return AgentService(workspace_root=temp_workspace)

    def test_get_config_file_content(self, agent_service):
        """REQ-0001-003: 获取配置文件内容"""
        agent_service.create_agent(agent_id="test-agent", name="Test Agent")

        content = agent_service.get_config_file("test-agent", "AGENTS.md")
        assert "test-agent" in content  # 模板应包含 agent id

    def test_list_config_files(self, agent_service):
        """REQ-0001-003: 列出所有配置文件"""
        agent_service.create_agent(agent_id="test-agent", name="Test Agent")

        files = agent_service.list_config_files("test-agent")
        file_types = [f.file_type for f in files]
        assert "AGENTS.md" in file_types
        assert "SOUL.md" in file_types
        assert "USER.md" in file_types
        assert "IDENTITY.md" in file_types

    def test_add_custom_config_file(self, agent_service, temp_workspace):
        """REQ-0001-003: 添加自定义配置文件"""
        agent_service.create_agent(agent_id="test-agent", name="Test Agent")

        agent_service.update_config_file(
            agent_id="test-agent",
            file_type="TOOLS.md",
            content="# Tools\nCustom tools definition",
        )

        # 验证文件已创建
        agent_dir = temp_workspace / "test-agent"
        assert (agent_dir / "TOOLS.md").exists()
