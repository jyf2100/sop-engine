"""OpenClaw 配置管理测试。

REQ-0001-004: OpenClaw 主配置管理
"""
import json
import tempfile
from pathlib import Path

import pytest


class TestOpenClawConfigService:
    """测试 OpenClaw 配置服务"""

    @pytest.fixture
    def temp_openclaw_root(self):
        """临时 OpenClaw 根目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # 创建初始 openclaw.json
            openclaw_json = root / "openclaw.json"
            openclaw_json.write_text(json.dumps({
                "agents": {"list": [], "defaults": {}},
                "bindings": []
            }))
            yield root

    @pytest.fixture
    def config_service(self, temp_openclaw_root):
        """创建 OpenClawConfigService 实例"""
        from app.services.openclaw_config_service import OpenClawConfigService

        return OpenClawConfigService(config_path=temp_openclaw_root / "openclaw.json")

    def test_service_importable(self):
        """REQ-0001-004: 服务可导入"""
        from app.services.openclaw_config_service import OpenClawConfigService

        assert OpenClawConfigService is not None

    def test_load_config(self, config_service):
        """REQ-0001-004: 加载 openclaw.json"""
        config = config_service.load_config()
        assert "agents" in config
        assert "bindings" in config

    def test_update_config(self, config_service, temp_openclaw_root):
        """REQ-0001-004: 更新并保存配置"""
        config_service.update_config({
            "agents": {
                "list": [{"id": "test-agent"}],
                "defaults": {}
            },
            "bindings": []
        })

        # 验证文件已更新
        openclaw_json = temp_openclaw_root / "openclaw.json"
        config = json.loads(openclaw_json.read_text())
        assert len(config["agents"]["list"]) == 1

    def test_validate_valid_config(self, config_service):
        """REQ-0001-004: 验证有效配置"""
        valid_config = {
            "agents": {"list": [], "defaults": {}},
            "bindings": []
        }
        assert config_service.validate_config(valid_config) is True

    def test_validate_config_fails_on_missing_agents(self, config_service):
        """REQ-0001-004: 缺少 agents 字段验证失败"""
        invalid_config = {"bindings": []}
        with pytest.raises(ValueError, match="agents"):
            config_service.validate_config(invalid_config)

    def test_validate_config_fails_on_invalid_agent_id(self, config_service):
        """REQ-0001-004: 无效 agent ID 验证失败"""
        invalid_config = {
            "agents": {
                "list": [{"id": ""}],  # 空 ID
                "defaults": {}
            },
            "bindings": []
        }
        with pytest.raises(ValueError, match="id"):
            config_service.validate_config(invalid_config)

    def test_get_agent_list(self, config_service):
        """REQ-0001-004: 获取 agent 列表"""
        config_service.update_config({
            "agents": {
                "list": [
                    {"id": "agent-1", "name": "Agent 1"},
                    {"id": "agent-2", "name": "Agent 2"}
                ],
                "defaults": {}
            },
            "bindings": []
        })

        agents = config_service.get_agent_list()
        assert len(agents) == 2
        assert agents[0]["id"] == "agent-1"

    def test_add_agent_to_list(self, config_service):
        """REQ-0001-004: 添加 agent 到列表"""
        config_service.add_agent({"id": "new-agent", "name": "New Agent"})

        agents = config_service.get_agent_list()
        assert len(agents) == 1
        assert agents[0]["id"] == "new-agent"

    def test_remove_agent_from_list(self, config_service):
        """REQ-0001-004: 从列表移除 agent"""
        config_service.add_agent({"id": "agent-1", "name": "Agent 1"})
        config_service.remove_agent("agent-1")

        agents = config_service.get_agent_list()
        assert len(agents) == 0

    def test_get_bindings(self, config_service):
        """REQ-0001-004: 获取绑定列表"""
        config_service.update_config({
            "agents": {"list": [], "defaults": {}},
            "bindings": [
                {"agentId": "agent-1", "type": "default"}
            ]
        })

        bindings = config_service.get_bindings()
        assert len(bindings) == 1

    def test_add_binding(self, config_service):
        """REQ-0001-004: 添加绑定"""
        config_service.add_binding({"agentId": "agent-1", "type": "default"})

        bindings = config_service.get_bindings()
        assert len(bindings) == 1

    def test_update_global_settings(self, config_service):
        """REQ-0001-004: 更新全局设置"""
        config_service.update_global_settings({
            "logging": {"level": "DEBUG"},
            "env": {"vars": {"API_KEY": "test"}}
        })

        config = config_service.load_config()
        assert config["logging"]["level"] == "DEBUG"


class TestOpenClawConfigWithHooks:
    """测试配置变更通知"""

    @pytest.fixture
    def temp_openclaw_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            openclaw_json = root / "openclaw.json"
            openclaw_json.write_text(json.dumps({
                "agents": {"list": [], "defaults": {}},
                "bindings": []
            }))
            yield root

    @pytest.fixture
    def config_service(self, temp_openclaw_root):
        from app.services.openclaw_config_service import OpenClawConfigService

        return OpenClawConfigService(
            config_path=temp_openclaw_root / "openclaw.json",
            reload_webhook_url="http://localhost:18789/reload"
        )

    def test_reload_notification_disabled(self, temp_openclaw_root):
        """REQ-0001-004: 未配置 webhook 时不发送通知"""
        from app.services.openclaw_config_service import OpenClawConfigService

        service = OpenClawConfigService(
            config_path=temp_openclaw_root / "openclaw.json",
            reload_webhook_url=None
        )
        service.update_config({
            "agents": {"list": [], "defaults": {}},
            "bindings": []
        })
        # 应该不抛出异常
