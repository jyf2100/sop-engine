"""Agent 配置对齐测试。

测试 Session、Messages、Commands 配置与 OpenClaw 的完整对齐。
对应 REQ-0001-027: Agent 配置完整对齐
"""
import json
import tempfile
from pathlib import Path

import pytest


# ==================== Fixtures ====================


@pytest.fixture
def temp_config_path(tmp_path: Path) -> Path:
    """创建临时配置文件路径"""
    config_path = tmp_path / ".openclaw" / "openclaw.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text("{}")
    return config_path


@pytest.fixture
def agent_service(temp_config_path: Path):
    """创建使用临时配置路径的 AgentService"""
    from app.services.agent_service import AgentService

    service = AgentService()
    service._openclaw_config_path = temp_config_path
    return service


# ==================== Session 配置测试 ====================


class TestSessionConfigModel:
    """测试 Session 配置模型"""

    def test_session_config_model_exists(self):
        """SessionConfig 模型应存在"""
        from app.models.session_config import SessionConfig

        assert SessionConfig is not None

    def test_dm_scope_field(self):
        """dm_scope 字段应支持所有值"""
        from app.models.session_config import SessionConfig

        # main
        config = SessionConfig(dm_scope="main")
        assert config.dm_scope == "main"

        # per-peer
        config = SessionConfig(dm_scope="per-peer")
        assert config.dm_scope == "per-peer"

        # per-channel-peer
        config = SessionConfig(dm_scope="per-channel-peer")
        assert config.dm_scope == "per-channel-peer"

        # per-account-channel-peer
        config = SessionConfig(dm_scope="per-account-channel-peer")
        assert config.dm_scope == "per-account-channel-peer"

    def test_reset_config(self):
        """重置配置应正确设置"""
        from app.models.session_config import SessionConfig, SessionResetConfig

        config = SessionConfig(
            reset=SessionResetConfig(
                mode="daily",
                at_hour=4,
            )
        )

        assert config.reset.mode == "daily"
        assert config.reset.at_hour == 4

    def test_reset_by_type_config(self):
        """按类型重置配置应正确设置"""
        from app.models.session_config import (
            SessionConfig,
            SessionResetByTypeConfig,
            SessionResetConfig,
        )

        config = SessionConfig(
            reset_by_type=SessionResetByTypeConfig(
                direct=SessionResetConfig(mode="idle", idle_minutes=120),
                group=SessionResetConfig(mode="daily", at_hour=2),
            )
        )

        assert config.reset_by_type.direct.mode == "idle"
        assert config.reset_by_type.direct.idle_minutes == 120
        assert config.reset_by_type.group.mode == "daily"
        assert config.reset_by_type.group.at_hour == 2

    def test_maintenance_config(self):
        """维护配置应正确设置"""
        from app.models.session_config import (
            SessionConfig,
            SessionMaintenanceConfig,
        )

        config = SessionConfig(
            maintenance=SessionMaintenanceConfig(
                mode="enforce",
                prune_after="30d",
                max_entries=500,
            )
        )

        assert config.maintenance.mode == "enforce"
        assert config.maintenance.prune_after == "30d"
        assert config.maintenance.max_entries == 500

    def test_thread_bindings_config(self):
        """线程绑定配置应正确设置"""
        from app.models.session_config import (
            SessionConfig,
            SessionThreadBindingsConfig,
        )

        config = SessionConfig(
            thread_bindings=SessionThreadBindingsConfig(
                enabled=True,
                idle_hours=24,
            )
        )

        assert config.thread_bindings.enabled == True
        assert config.thread_bindings.idle_hours == 24


class TestSessionConfigToOpenClaw:
    """测试 Session 配置转换为 OpenClaw 格式"""

    def test_dm_scope_camel_case(self):
        """dmScope 应转为 camelCase"""
        from app.models.session_config import SessionConfig

        config = SessionConfig(dm_scope="per-peer")
        result = config.to_openclaw()

        assert result["dmScope"] == "per-peer"

    def test_reset_to_openclaw(self):
        """reset 应正确转换"""
        from app.models.session_config import SessionConfig, SessionResetConfig

        config = SessionConfig(
            reset=SessionResetConfig(mode="daily", at_hour=4, idle_minutes=120)
        )
        result = config.to_openclaw()

        assert result["reset"]["mode"] == "daily"
        assert result["reset"]["atHour"] == 4
        assert result["reset"]["idleMinutes"] == 120

    def test_reset_by_type_to_openclaw(self):
        """resetByType 应正确转换"""
        from app.models.session_config import (
            SessionConfig,
            SessionResetByTypeConfig,
            SessionResetConfig,
        )

        config = SessionConfig(
            reset_by_type=SessionResetByTypeConfig(
                direct=SessionResetConfig(mode="idle", idle_minutes=60),
            )
        )
        result = config.to_openclaw()

        assert "resetByType" in result
        assert result["resetByType"]["direct"]["mode"] == "idle"
        assert result["resetByType"]["direct"]["idleMinutes"] == 60

    def test_maintenance_to_openclaw(self):
        """maintenance 应正确转换"""
        from app.models.session_config import (
            SessionConfig,
            SessionMaintenanceConfig,
        )

        config = SessionConfig(
            maintenance=SessionMaintenanceConfig(
                mode="enforce",
                prune_after="30d",
                max_disk_bytes="100mb",
            )
        )
        result = config.to_openclaw()

        assert result["maintenance"]["mode"] == "enforce"
        assert result["maintenance"]["pruneAfter"] == "30d"
        assert result["maintenance"]["maxDiskBytes"] == "100mb"

    def test_full_session_config_to_openclaw(self):
        """完整 Session 配置应正确转换"""
        from app.models.session_config import (
            SessionConfig,
            SessionMaintenanceConfig,
            SessionResetConfig,
        )

        config = SessionConfig(
            dm_scope="per-peer",
            reset=SessionResetConfig(mode="daily", at_hour=4),
            maintenance=SessionMaintenanceConfig(mode="warn"),
            reset_triggers=["/new", "/reset"],
        )
        result = config.to_openclaw()

        assert result["dmScope"] == "per-peer"
        assert result["reset"]["mode"] == "daily"
        assert result["maintenance"]["mode"] == "warn"
        assert result["resetTriggers"] == ["/new", "/reset"]


# ==================== Messages 配置测试 ====================


class TestMessagesConfigModel:
    """测试 Messages 配置模型"""

    def test_messages_config_model_exists(self):
        """MessagesConfig 模型应存在"""
        from app.models.messages_config import MessagesConfig

        assert MessagesConfig is not None

    def test_queue_config(self):
        """队列配置应正确设置"""
        from app.models.messages_config import MessagesConfig, MessageQueueConfig

        config = MessagesConfig(
            queue=MessageQueueConfig(mode="steer", debounce_ms=500)
        )

        assert config.queue.mode == "steer"
        assert config.queue.debounce_ms == 500

    def test_queue_modes(self):
        """队列模式应支持所有值"""
        from app.models.messages_config import MessageQueueConfig

        for mode in ["steer", "followup", "collect", "interrupt"]:
            config = MessageQueueConfig(mode=mode)
            assert config.mode == mode

    def test_inbound_config(self):
        """入站配置应正确设置"""
        from app.models.messages_config import InboundConfig, MessagesConfig

        config = MessagesConfig(
            inbound=InboundConfig(debounce_ms=1000)
        )

        assert config.inbound.debounce_ms == 1000


class TestMessagesConfigToOpenClaw:
    """测试 Messages 配置转换为 OpenClaw 格式"""

    def test_queue_to_openclaw(self):
        """queue 应正确转换"""
        from app.models.messages_config import MessageQueueConfig

        config = MessageQueueConfig(
            mode="steer",
            debounce_ms=500,
            cap=20,
        )
        result = config.to_openclaw()

        assert result["mode"] == "steer"
        assert result["debounceMs"] == 500
        assert result["cap"] == 20

    def test_inbound_to_openclaw(self):
        """inbound 应正确转换"""
        from app.models.messages_config import InboundConfig

        config = InboundConfig(debounce_ms=2000)
        result = config.to_openclaw()

        assert result["debounceMs"] == 2000


# ==================== Commands 配置测试 ====================


class TestCommandsConfigModel:
    """测试 Commands 配置模型"""

    def test_commands_config_model_exists(self):
        """CommandsConfig 模型应存在"""
        from app.models.commands_config import CommandsConfig

        assert CommandsConfig is not None

    def test_native_commands_config(self):
        """原生命令配置应正确设置"""
        from app.models.commands_config import CommandsConfig, NativeCommandsConfig

        config = CommandsConfig(
            native=NativeCommandsConfig(enabled=True)
        )

        assert config.native.enabled == True

    def test_text_commands_config(self):
        """文本命令配置应正确设置"""
        from app.models.commands_config import CommandsConfig, TextCommandsConfig

        config = CommandsConfig(
            text=TextCommandsConfig(prefix="!", enabled=True)
        )

        assert config.text.prefix == "!"
        assert config.text.enabled == True

    def test_bash_commands_config(self):
        """Bash 命令配置应正确设置"""
        from app.models.commands_config import BashCommandsConfig, CommandsConfig

        config = CommandsConfig(
            bash=BashCommandsConfig(
                enabled=True,
                timeout_seconds=60,
            )
        )

        assert config.bash.enabled == True
        assert config.bash.timeout_seconds == 60


class TestCommandsConfigToOpenClaw:
    """测试 Commands 配置转换为 OpenClaw 格式"""

    def test_native_to_openclaw(self):
        """native 应正确转换"""
        from app.models.commands_config import NativeCommandsConfig

        config = NativeCommandsConfig(enabled=True)
        result = config.to_openclaw()

        assert result["enabled"] == True

    def test_text_to_openclaw(self):
        """text 应正确转换"""
        from app.models.commands_config import TextCommandsConfig

        config = TextCommandsConfig(prefix="!", enabled=True)
        result = config.to_openclaw()

        assert result["prefix"] == "!"
        assert result["enabled"] == True

    def test_bash_to_openclaw(self):
        """bash 应正确转换"""
        from app.models.commands_config import BashCommandsConfig

        config = BashCommandsConfig(
            enabled=True,
            timeout_seconds=60,
            safe_bins=["ls", "cat"],
        )
        result = config.to_openclaw()

        assert result["enabled"] == True
        assert result["timeoutSeconds"] == 60
        assert result["safeBins"] == ["ls", "cat"]


# ==================== Agent 整合测试 ====================


class TestAgentWithSessionConfig:
    """测试 Agent 整合 Session 配置"""

    @pytest.fixture
    def temp_workspace(self):
        """临时工作目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def agent_service(self, temp_workspace, temp_config_path):
        """创建 AgentService 实例"""
        from app.services.agent_service import AgentService

        service = AgentService(workspace_root=temp_workspace)
        service._openclaw_config_path = temp_config_path
        return service

    def test_agent_with_session_config(
        self, agent_service, temp_workspace, temp_config_path
    ):
        """Agent 应支持 Session 配置"""
        from app.models.session_config import (
            SessionConfig,
            SessionResetConfig,
        )

        agent = agent_service.create_agent(
            agent_id="test-agent",
            name="Test Agent",
            session_config=SessionConfig(
                dm_scope="per-peer",
                reset=SessionResetConfig(mode="daily", at_hour=4),
            ),
        )

        assert agent.session_config is not None
        assert agent.session_config.dm_scope == "per-peer"

    def test_agent_session_config_sync_to_openclaw(
        self, agent_service, temp_workspace, temp_config_path
    ):
        """Agent Session 配置应同步到 openclaw.json"""
        from app.models.session_config import (
            SessionConfig,
            SessionResetConfig,
        )

        agent_service.create_agent(
            agent_id="test-agent",
            name="Test Agent",
            session_config=SessionConfig(
                dm_scope="per-peer",
                reset=SessionResetConfig(mode="daily", at_hour=4),
            ),
        )

        # 读取生成的配置
        result = json.loads(temp_config_path.read_text())

        # 验证 session 配置
        agent_config = result["agents"]["list"][0]
        assert agent_config["session"]["dmScope"] == "per-peer"
        assert agent_config["session"]["reset"]["mode"] == "daily"
        assert agent_config["session"]["reset"]["atHour"] == 4


class TestAgentWithMessagesConfig:
    """测试 Agent 整合 Messages 配置"""

    @pytest.fixture
    def temp_workspace(self):
        """临时工作目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def agent_service(self, temp_workspace, temp_config_path):
        """创建 AgentService 实例"""
        from app.services.agent_service import AgentService

        service = AgentService(workspace_root=temp_workspace)
        service._openclaw_config_path = temp_config_path
        return service

    def test_agent_with_messages_config(
        self, agent_service, temp_workspace, temp_config_path
    ):
        """Agent 应支持 Messages 配置"""
        from app.models.messages_config import (
            InboundConfig,
            MessageQueueConfig,
            MessagesConfig,
        )

        agent = agent_service.create_agent(
            agent_id="test-agent",
            name="Test Agent",
            messages_config=MessagesConfig(
                queue=MessageQueueConfig(mode="steer"),
                inbound=InboundConfig(debounce_ms=500),
            ),
        )

        assert agent.messages_config is not None
        assert agent.messages_config.queue.mode == "steer"

    def test_agent_messages_config_sync_to_openclaw(
        self, agent_service, temp_workspace, temp_config_path
    ):
        """Agent Messages 配置应同步到 openclaw.json"""
        from app.models.messages_config import (
            InboundConfig,
            MessageQueueConfig,
            MessagesConfig,
        )

        agent_service.create_agent(
            agent_id="test-agent",
            name="Test Agent",
            messages_config=MessagesConfig(
                queue=MessageQueueConfig(mode="steer"),
                inbound=InboundConfig(debounce_ms=500),
            ),
        )

        # 读取生成的配置
        result = json.loads(temp_config_path.read_text())

        # 验证 messages 配置（在 agents.list[] 中）
        agent_config = result["agents"]["list"][0]
        assert agent_config["messages"]["queue"]["mode"] == "steer"
        assert agent_config["messages"]["inbound"]["debounceMs"] == 500


class TestAgentWithCommandsConfig:
    """测试 Agent 整合 Commands 配置"""

    @pytest.fixture
    def temp_workspace(self):
        """临时工作目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def agent_service(self, temp_workspace, temp_config_path):
        """创建 AgentService 实例"""
        from app.services.agent_service import AgentService

        service = AgentService(workspace_root=temp_workspace)
        service._openclaw_config_path = temp_config_path
        return service

    def test_agent_with_commands_config(
        self, agent_service, temp_workspace, temp_config_path
    ):
        """Agent 应支持 Commands 配置"""
        from app.models.commands_config import (
            BashCommandsConfig,
            CommandsConfig,
            NativeCommandsConfig,
            TextCommandsConfig,
        )

        agent = agent_service.create_agent(
            agent_id="test-agent",
            name="Test Agent",
            commands_config=CommandsConfig(
                native=NativeCommandsConfig(enabled=True),
                text=TextCommandsConfig(prefix="!"),
                bash=BashCommandsConfig(enabled=True, timeout_seconds=60),
            ),
        )

        assert agent.commands_config is not None
        assert agent.commands_config.native.enabled == True
        assert agent.commands_config.text.prefix == "!"

    def test_agent_commands_config_sync_to_openclaw(
        self, agent_service, temp_workspace, temp_config_path
    ):
        """Agent Commands 配置应同步到 openclaw.json"""
        from app.models.commands_config import (
            BashCommandsConfig,
            CommandsConfig,
            NativeCommandsConfig,
            TextCommandsConfig,
        )

        agent_service.create_agent(
            agent_id="test-agent",
            name="Test Agent",
            commands_config=CommandsConfig(
                native=NativeCommandsConfig(enabled=True),
                text=TextCommandsConfig(prefix="!"),
                bash=BashCommandsConfig(enabled=True, timeout_seconds=60),
            ),
        )

        # 读取生成的配置
        result = json.loads(temp_config_path.read_text())

        # 验证 commands 配置（在 agents.list[] 中）
        agent_config = result["agents"]["list"][0]
        assert agent_config["commands"]["native"]["enabled"] == True
        assert agent_config["commands"]["text"]["prefix"] == "!"
        assert agent_config["commands"]["bash"]["timeoutSeconds"] == 60
