"""Agent 同步集成测试。

REQ-0001-003: Agent 配置管理
测试与 OpenClaw 的同步机制。
"""
import json
import tempfile
from pathlib import Path

import pytest


class TestOpenClawSync:
    """测试 OpenClaw 同步功能"""

    @pytest.fixture
    def temp_openclaw_root(self):
        """临时 OpenClaw 根目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # 创建初始 openclaw.json
            openclaw_json = root / "openclaw.json"
            openclaw_json.write_text(json.dumps({
                "agents": {
                    "list": [],
                    "defaults": {}
                },
                "bindings": []
            }))
            yield root

    @pytest.fixture
    def openclaw_sync(self, temp_openclaw_root):
        """创建 OpenClawSync 实例"""
        from app.services.openclaw_sync import OpenClawSync

        return OpenClawSync(workspace_root=temp_openclaw_root)

    def test_sync_agent_creates_workspace(self, openclaw_sync, temp_openclaw_root):
        """REQ-0001-003: 同步 Agent 时创建 workspace 目录"""
        from app.models import Agent

        agent = Agent(
            id="test-agent",
            name="Test Agent",
            workspace_path=str(temp_openclaw_root / "test-agent"),
            llm_config={"primary": "claude-3-5-sonnet"},
            sandbox_config={"mode": "non-main"},
            tools_config={"allow": []},
        )

        openclaw_sync.sync_agent(agent)

        # 验证目录已创建
        assert (temp_openclaw_root / "test-agent").exists()
        assert (temp_openclaw_root / "test-agent" / "AGENTS.md").exists()

    def test_sync_agent_updates_openclaw_json(self, openclaw_sync, temp_openclaw_root):
        """REQ-0001-003: 同步 Agent 时更新 openclaw.json"""
        from app.models import Agent

        agent = Agent(
            id="test-agent",
            name="Test Agent",
            workspace_path=str(temp_openclaw_root / "test-agent"),
            llm_config={"primary": "claude-3-5-sonnet"},
            sandbox_config={"mode": "non-main"},
            tools_config={"allow": []},
        )

        openclaw_sync.sync_agent(agent)

        # 验证 openclaw.json 已更新
        openclaw_json = temp_openclaw_root / "openclaw.json"
        config = json.loads(openclaw_json.read_text())

        agent_ids = [a["id"] for a in config["agents"]["list"]]
        assert "test-agent" in agent_ids

    def test_sync_config_files_to_workspace(self, openclaw_sync, temp_openclaw_root):
        """REQ-0001-003: 同步配置文件到 workspace"""
        from app.models import Agent, AgentConfigFile

        agent = Agent(
            id="test-agent",
            name="Test Agent",
            workspace_path=str(temp_openclaw_root / "test-agent"),
            llm_config={"primary": "claude-3-5-sonnet"},
            sandbox_config={"mode": "non-main"},
            tools_config={"allow": []},
        )

        config_files = [
            AgentConfigFile(
                id="cfg-1",
                agent_id="test-agent",
                file_type="AGENTS.md",
                content="# Custom Agents",
            ),
            AgentConfigFile(
                id="cfg-2",
                agent_id="test-agent",
                file_type="SOUL.md",
                content="# Custom Soul",
            ),
        ]

        openclaw_sync.sync_agent(agent, config_files)

        # 验证自定义内容已写入
        agents_content = (temp_openclaw_root / "test-agent" / "AGENTS.md").read_text()
        assert "Custom Agents" in agents_content

    def test_delete_agent_cleans_up(self, openclaw_sync, temp_openclaw_root):
        """REQ-0001-003: 删除 Agent 时清理 workspace 和 openclaw.json"""
        from app.models import Agent

        # 先创建
        agent = Agent(
            id="test-agent",
            name="Test Agent",
            workspace_path=str(temp_openclaw_root / "test-agent"),
            llm_config={"primary": "claude-3-5-sonnet"},
            sandbox_config={"mode": "non-main"},
            tools_config={"allow": []},
        )
        openclaw_sync.sync_agent(agent)

        # 再删除
        openclaw_sync.delete_agent("test-agent")

        # 验证目录已删除
        assert not (temp_openclaw_root / "test-agent").exists()

        # 验证 openclaw.json 已更新
        openclaw_json = temp_openclaw_root / "openclaw.json"
        config = json.loads(openclaw_json.read_text())
        agent_ids = [a["id"] for a in config["agents"]["list"]]
        assert "test-agent" not in agent_ids

    def test_sync_multiple_agents(self, openclaw_sync, temp_openclaw_root):
        """REQ-0001-003: 同步多个 Agent"""
        from app.models import Agent

        agents = [
            Agent(
                id=f"agent-{i}",
                name=f"Agent {i}",
                workspace_path=str(temp_openclaw_root / f"agent-{i}"),
                llm_config={"primary": "claude-3-5-sonnet"},
                sandbox_config={"mode": "non-main"},
                tools_config={"allow": []},
            )
            for i in range(3)
        ]

        for agent in agents:
            openclaw_sync.sync_agent(agent)

        # 验证所有 agent 都在 openclaw.json
        openclaw_json = temp_openclaw_root / "openclaw.json"
        config = json.loads(openclaw_json.read_text())
        assert len(config["agents"]["list"]) == 3

    def test_update_agent_metadata(self, openclaw_sync, temp_openclaw_root):
        """REQ-0001-003: 更新 Agent 元数据"""
        from app.models import Agent

        agent = Agent(
            id="test-agent",
            name="Test Agent",
            workspace_path=str(temp_openclaw_root / "test-agent"),
            llm_config={"primary": "claude-3-5-sonnet"},
            sandbox_config={"mode": "non-main"},
            tools_config={"allow": []},
        )
        openclaw_sync.sync_agent(agent)

        # 更新
        updated_agent = Agent(
            id="test-agent",
            name="Updated Agent",
            workspace_path=str(temp_openclaw_root / "test-agent"),
            llm_config={"primary": "claude-3-5-sonnet"},
            sandbox_config={"mode": "all"},  # 修改
            tools_config={"allow": ["read", "write"]},  # 修改
        )
        openclaw_sync.sync_agent(updated_agent)

        # 验证更新
        openclaw_json = temp_openclaw_root / "openclaw.json"
        config = json.loads(openclaw_json.read_text())
        agent_config = next(a for a in config["agents"]["list"] if a["id"] == "test-agent")
        assert agent_config["sandbox"]["mode"] == "all"


class TestOpenClawBindings:
    """测试 OpenClaw bindings 生成"""

    @pytest.fixture
    def temp_openclaw_root(self):
        """临时 OpenClaw 根目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            openclaw_json = root / "openclaw.json"
            openclaw_json.write_text(json.dumps({
                "agents": {"list": [], "defaults": {}},
                "bindings": []
            }))
            yield root

    @pytest.fixture
    def openclaw_sync(self, temp_openclaw_root):
        from app.services.openclaw_sync import OpenClawSync
        return OpenClawSync(workspace_root=temp_openclaw_root)

    def test_generate_default_binding(self, openclaw_sync, temp_openclaw_root):
        """REQ-0001-003: 为 default Agent 生成绑定"""
        from app.models import Agent

        agent = Agent(
            id="main",
            name="Main Agent",
            workspace_path=str(temp_openclaw_root / "main"),
            llm_config={"primary": "claude-3-5-sonnet"},
            sandbox_config={"mode": "non-main"},
            tools_config={"allow": []},
            is_default=True,
        )
        openclaw_sync.sync_agent(agent)

        openclaw_json = temp_openclaw_root / "openclaw.json"
        config = json.loads(openclaw_json.read_text())

        # 验证 default binding
        bindings = config.get("bindings", [])
        default_binding = next((b for b in bindings if b.get("agentId") == "main"), None)
        assert default_binding is not None
