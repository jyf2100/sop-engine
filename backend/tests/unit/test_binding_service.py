"""Binding 配置服务测试。

测试 Bindings 配置与 OpenClaw 的完整对齐。
对应 REQ-0001-028: Bindings 配置支持
"""
import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest


# ==================== Fixtures ====================


@pytest.fixture
def temp_config_path(tmp_path: Path) -> Path:
    """创建临时配置文件路径"""
    config_path = tmp_path / ".openclaw" / "openclaw.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text("{}")
    return config_path


# ==================== Binding 模型测试 ====================


class TestBindingMatchModel:
    """测试 BindingMatch 模型"""

    def test_binding_match_model_exists(self):
        """BindingMatch 模型应存在"""
        from app.models.binding import BindingMatch

        assert BindingMatch is not None

    def test_binding_match_channel_field(self):
        """BindingMatch channel 字段应正确设置"""
        from app.models.binding import BindingMatch

        match = BindingMatch(channel="telegram")
        assert match.channel == "telegram"

    def test_binding_match_all_fields(self):
        """BindingMatch 所有字段应正确设置"""
        from app.models.binding import BindingMatch, PeerMatch

        match = BindingMatch(
            channel="telegram",
            account_id="default",
            peer=PeerMatch(kind="direct", id="12345"),
            guild_id="guild-1",
            team_id="team-1",
        )

        assert match.channel == "telegram"
        assert match.account_id == "default"
        assert match.peer.kind == "direct"
        assert match.peer.id == "12345"
        assert match.guild_id == "guild-1"
        assert match.team_id == "team-1"


class TestBindingMatchToOpenClaw:
    """测试 BindingMatch 转换为 OpenClaw 格式"""

    def test_channel_only_to_openclaw(self):
        """仅 channel 应正确转换"""
        from app.models.binding import BindingMatch

        match = BindingMatch(channel="telegram")
        result = match.to_openclaw()

        assert result["channel"] == "telegram"
        assert "accountId" not in result

    def test_full_match_to_openclaw(self):
        """完整匹配规则应正确转换"""
        from app.models.binding import BindingMatch, PeerMatch

        match = BindingMatch(
            channel="telegram",
            account_id="default",
            peer=PeerMatch(kind="direct", id="12345"),
            guild_id="guild-1",
            team_id="team-1",
        )
        result = match.to_openclaw()

        assert result["channel"] == "telegram"
        assert result["accountId"] == "default"
        assert result["peer"]["kind"] == "direct"
        assert result["peer"]["id"] == "12345"
        assert result["guildId"] == "guild-1"
        assert result["teamId"] == "team-1"


class TestAcpConfigModel:
    """测试 AcpConfig 模型"""

    def test_acp_config_model_exists(self):
        """AcpConfig 模型应存在"""
        from app.models.binding import AcpConfig

        assert AcpConfig is not None

    def test_acp_config_default_values(self):
        """AcpConfig 默认值应正确"""
        from app.models.binding import AcpConfig

        acp = AcpConfig()

        assert acp.mode == "persistent"
        assert acp.backend == "acpx"
        assert acp.label is None
        assert acp.cwd is None

    def test_acp_config_custom_values(self):
        """AcpConfig 自定义值应正确"""
        from app.models.binding import AcpConfig

        acp = AcpConfig(
            mode="ephemeral",
            label="my-session",
            cwd="/workspace",
            backend="acpx",
        )

        assert acp.mode == "ephemeral"
        assert acp.label == "my-session"
        assert acp.cwd == "/workspace"
        assert acp.backend == "acpx"

    def test_acp_config_to_openclaw(self):
        """AcpConfig 应正确转换为 OpenClaw 格式"""
        from app.models.binding import AcpConfig

        acp = AcpConfig(
            mode="persistent",
            label="dev-session",
            cwd="/home/user/dev",
        )
        result = acp.to_openclaw()

        assert result["mode"] == "persistent"
        assert result["label"] == "dev-session"
        assert result["cwd"] == "/home/user/dev"
        assert result["backend"] == "acpx"


class TestBindingModel:
    """测试 Binding 模型"""

    def test_binding_model_exists(self):
        """Binding 模型应存在"""
        from app.models.binding import Binding

        assert Binding is not None

    def test_route_binding(self):
        """Route 类型绑定应正确创建"""
        from app.models.binding import Binding, BindingMatch

        binding = Binding(
            type="route",
            agent_id="agent-1",
            match=BindingMatch(channel="telegram"),
        )

        assert binding.type == "route"
        assert binding.agent_id == "agent-1"
        assert binding.match.channel == "telegram"
        assert binding.acp is None

    def test_acp_binding(self):
        """ACP 类型绑定应正确创建"""
        from app.models.binding import AcpConfig, Binding, BindingMatch

        binding = Binding(
            type="acp",
            agent_id="agent-2",
            match=BindingMatch(channel="discord"),
            acp=AcpConfig(mode="persistent", label="dev"),
        )

        assert binding.type == "acp"
        assert binding.agent_id == "agent-2"
        assert binding.acp is not None
        assert binding.acp.mode == "persistent"


class TestBindingToOpenClaw:
    """测试 Binding 转换为 OpenClaw 格式"""

    def test_route_binding_to_openclaw(self):
        """Route 绑定应正确转换"""
        from app.models.binding import Binding, BindingMatch

        binding = Binding(
            type="route",
            agent_id="agent-1",
            match=BindingMatch(channel="telegram", account_id="default"),
        )
        result = binding.to_openclaw()

        assert result["type"] == "route"
        assert result["agentId"] == "agent-1"
        assert result["match"]["channel"] == "telegram"
        assert result["match"]["accountId"] == "default"
        assert "acp" not in result

    def test_acp_binding_to_openclaw(self):
        """ACP 绑定应正确转换"""
        from app.models.binding import AcpConfig, Binding, BindingMatch

        binding = Binding(
            type="acp",
            agent_id="agent-2",
            match=BindingMatch(channel="discord"),
            acp=AcpConfig(mode="persistent", cwd="/workspace"),
        )
        result = binding.to_openclaw()

        assert result["type"] == "acp"
        assert result["agentId"] == "agent-2"
        assert result["acp"]["mode"] == "persistent"
        assert result["acp"]["cwd"] == "/workspace"


class TestBindingsConfig:
    """测试 BindingsConfig 模型"""

    def test_bindings_config_model_exists(self):
        """BindingsConfig 模型应存在"""
        from app.models.binding import BindingsConfig

        assert BindingsConfig is not None

    def test_empty_bindings_config(self):
        """空 BindingsConfig 应正确创建"""
        from app.models.binding import BindingsConfig

        config = BindingsConfig()

        assert config.bindings == []

    def test_bindings_config_with_bindings(self):
        """包含绑定的 BindingsConfig 应正确创建"""
        from app.models.binding import Binding, BindingsConfig, BindingMatch

        config = BindingsConfig(
            bindings=[
                Binding(
                    type="route",
                    agent_id="agent-1",
                    match=BindingMatch(channel="telegram"),
                ),
                Binding(
                    type="route",
                    agent_id="agent-2",
                    match=BindingMatch(channel="discord"),
                ),
            ]
        )

        assert len(config.bindings) == 2
        assert config.bindings[0].agent_id == "agent-1"
        assert config.bindings[1].agent_id == "agent-2"

    def test_bindings_config_to_openclaw(self):
        """BindingsConfig 应正确转换为 OpenClaw 格式"""
        from app.models.binding import Binding, BindingsConfig, BindingMatch

        config = BindingsConfig(
            bindings=[
                Binding(
                    type="route",
                    agent_id="agent-1",
                    match=BindingMatch(channel="telegram"),
                ),
            ]
        )
        result = config.to_openclaw()

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["agentId"] == "agent-1"


class TestBindingsConfigFromOpenClaw:
    """测试从 OpenClaw 格式解析 BindingsConfig"""

    def test_parse_empty_bindings(self):
        """空绑定列表应正确解析"""
        from app.models.binding import BindingsConfig

        config = BindingsConfig.from_openclaw([])

        assert config.bindings == []

    def test_parse_route_binding(self):
        """Route 绑定应正确解析"""
        from app.models.binding import BindingsConfig

        data = [
            {
                "type": "route",
                "agentId": "agent-1",
                "match": {
                    "channel": "telegram",
                    "accountId": "default",
                },
            }
        ]

        config = BindingsConfig.from_openclaw(data)

        assert len(config.bindings) == 1
        assert config.bindings[0].type == "route"
        assert config.bindings[0].agent_id == "agent-1"
        assert config.bindings[0].match.channel == "telegram"

    def test_parse_acp_binding(self):
        """ACP 绑定应正确解析"""
        from app.models.binding import BindingsConfig

        data = [
            {
                "type": "acp",
                "agentId": "agent-2",
                "match": {
                    "channel": "discord",
                    "peer": {"kind": "direct", "id": "12345"},
                },
                "acp": {
                    "mode": "persistent",
                    "label": "dev-session",
                },
            }
        ]

        config = BindingsConfig.from_openclaw(data)

        assert len(config.bindings) == 1
        assert config.bindings[0].type == "acp"
        assert config.bindings[0].acp is not None
        assert config.bindings[0].acp.label == "dev-session"
        assert config.bindings[0].match.peer.kind == "direct"


# ==================== 优先级匹配测试 ====================


class TestBindingPriority:
    """测试绑定优先级匹配"""

    def test_match_binding_function_exists(self):
        """match_binding 函数应存在"""
        from app.services.binding_service import match_binding

        assert match_binding is not None

    def test_peer_priority_highest(self):
        """Peer 级别优先级最高"""
        from app.models.binding import Binding, BindingMatch, PeerMatch
        from app.services.binding_service import match_binding

        bindings = [
            Binding(
                type="route",
                agent_id="agent-default",
                match=BindingMatch(channel="telegram"),
            ),
            Binding(
                type="route",
                agent_id="agent-peer",
                match=BindingMatch(
                    channel="telegram",
                    peer=PeerMatch(kind="direct", id="12345"),
                ),
            ),
        ]

        result = match_binding(
            bindings,
            channel="telegram",
            peer={"kind": "direct", "id": "12345"},
        )

        assert result is not None
        assert result.agent_id == "agent-peer"

    def test_guild_priority_over_default(self):
        """Guild 级别优先级高于 Default"""
        from app.models.binding import Binding, BindingMatch
        from app.services.binding_service import match_binding

        bindings = [
            Binding(
                type="route",
                agent_id="agent-default",
                match=BindingMatch(channel="discord"),
            ),
            Binding(
                type="route",
                agent_id="agent-guild",
                match=BindingMatch(channel="discord", guild_id="guild-1"),
            ),
        ]

        result = match_binding(
            bindings,
            channel="discord",
            guild_id="guild-1",
        )

        assert result is not None
        assert result.agent_id == "agent-guild"

    def test_team_priority_over_default(self):
        """Team 级别优先级高于 Default"""
        from app.models.binding import Binding, BindingMatch
        from app.services.binding_service import match_binding

        bindings = [
            Binding(
                type="route",
                agent_id="agent-default",
                match=BindingMatch(channel="slack"),
            ),
            Binding(
                type="route",
                agent_id="agent-team",
                match=BindingMatch(channel="slack", team_id="team-1"),
            ),
        ]

        result = match_binding(
            bindings,
            channel="slack",
            team_id="team-1",
        )

        assert result is not None
        assert result.agent_id == "agent-team"

    def test_account_priority_over_default(self):
        """Account 级别优先级高于 Default"""
        from app.models.binding import Binding, BindingMatch
        from app.services.binding_service import match_binding

        bindings = [
            Binding(
                type="route",
                agent_id="agent-default",
                match=BindingMatch(channel="telegram"),
            ),
            Binding(
                type="route",
                agent_id="agent-account",
                match=BindingMatch(channel="telegram", account_id="account-1"),
            ),
        ]

        result = match_binding(
            bindings,
            channel="telegram",
            account_id="account-1",
        )

        assert result is not None
        assert result.agent_id == "agent-account"

    def test_default_fallback(self):
        """Default 级别作为兜底"""
        from app.models.binding import Binding, BindingMatch
        from app.services.binding_service import match_binding

        bindings = [
            Binding(
                type="route",
                agent_id="agent-default",
                match=BindingMatch(channel="telegram"),
            ),
        ]

        result = match_binding(
            bindings,
            channel="telegram",
            peer={"kind": "direct", "id": "99999"},
        )

        assert result is not None
        assert result.agent_id == "agent-default"

    def test_no_match_returns_none(self):
        """无匹配时返回 None"""
        from app.models.binding import Binding, BindingMatch
        from app.services.binding_service import match_binding

        bindings = [
            Binding(
                type="route",
                agent_id="agent-1",
                match=BindingMatch(channel="telegram"),
            ),
        ]

        result = match_binding(
            bindings,
            channel="discord",  # 不匹配的 channel
        )

        assert result is None

    def test_priority_order_peer_guild_team_account(self):
        """完整优先级顺序测试：peer > guild > team > account > default"""
        from app.models.binding import Binding, BindingMatch, PeerMatch
        from app.services.binding_service import match_binding

        bindings = [
            # Default
            Binding(
                type="route",
                agent_id="agent-default",
                match=BindingMatch(channel="discord"),
            ),
            # Account
            Binding(
                type="route",
                agent_id="agent-account",
                match=BindingMatch(channel="discord", account_id="acc-1"),
            ),
            # Team
            Binding(
                type="route",
                agent_id="agent-team",
                match=BindingMatch(channel="discord", team_id="team-1"),
            ),
            # Guild
            Binding(
                type="route",
                agent_id="agent-guild",
                match=BindingMatch(channel="discord", guild_id="guild-1"),
            ),
            # Peer
            Binding(
                type="route",
                agent_id="agent-peer",
                match=BindingMatch(
                    channel="discord",
                    peer=PeerMatch(kind="direct", id="user-1"),
                ),
            ),
        ]

        # Peer 匹配
        result = match_binding(
            bindings,
            channel="discord",
            peer={"kind": "direct", "id": "user-1"},
            guild_id="guild-1",
            team_id="team-1",
            account_id="acc-1",
        )
        assert result.agent_id == "agent-peer"

        # Guild 匹配（无 peer）
        result = match_binding(
            bindings,
            channel="discord",
            guild_id="guild-1",
            team_id="team-1",
            account_id="acc-1",
        )
        assert result.agent_id == "agent-guild"

        # Team 匹配（无 peer/guild）
        result = match_binding(
            bindings,
            channel="discord",
            team_id="team-1",
            account_id="acc-1",
        )
        assert result.agent_id == "agent-team"

        # Account 匹配（无 peer/guild/team）
        result = match_binding(
            bindings,
            channel="discord",
            account_id="acc-1",
        )
        assert result.agent_id == "agent-account"

        # Default 匹配
        result = match_binding(bindings, channel="discord")
        assert result.agent_id == "agent-default"


# ==================== BindingService 测试 ====================


class TestBindingService:
    """测试 BindingService"""

    @pytest.fixture
    def binding_service(self, temp_config_path):
        """创建 BindingService 实例"""
        from app.services.binding_service import BindingService

        service = BindingService()
        service._openclaw_config_path = temp_config_path
        return service

    def test_binding_service_exists(self, binding_service):
        """BindingService 应正确创建"""
        assert binding_service is not None

    def test_create_binding(self, binding_service):
        """应正确创建绑定"""
        from app.models.binding import Binding, BindingMatch

        binding = binding_service.create_binding(
            binding_id="bind-1",
            type="route",
            agent_id="agent-1",
            match=BindingMatch(channel="telegram"),
        )

        assert binding is not None
        assert binding.agent_id == "agent-1"

    def test_get_binding(self, binding_service):
        """应正确获取绑定"""
        from app.models.binding import BindingMatch

        binding_service.create_binding(
            binding_id="bind-1",
            type="route",
            agent_id="agent-1",
            match=BindingMatch(channel="telegram"),
        )

        binding = binding_service.get_binding("bind-1")

        assert binding is not None
        assert binding.agent_id == "agent-1"

    def test_list_bindings(self, binding_service):
        """应正确列出所有绑定"""
        from app.models.binding import BindingMatch

        binding_service.create_binding(
            binding_id="bind-1",
            type="route",
            agent_id="agent-1",
            match=BindingMatch(channel="telegram"),
        )
        binding_service.create_binding(
            binding_id="bind-2",
            type="route",
            agent_id="agent-2",
            match=BindingMatch(channel="discord"),
        )

        bindings = binding_service.list_bindings()

        assert len(bindings) == 2

    def test_update_binding(self, binding_service):
        """应正确更新绑定"""
        from app.models.binding import Binding, BindingMatch

        binding_service.create_binding(
            binding_id="bind-1",
            type="route",
            agent_id="agent-1",
            match=BindingMatch(channel="telegram"),
        )

        updated = binding_service.update_binding(
            binding_id="bind-1",
            agent_id="agent-updated",
        )

        assert updated.agent_id == "agent-updated"

    def test_delete_binding(self, binding_service):
        """应正确删除绑定"""
        from app.models.binding import BindingMatch

        binding_service.create_binding(
            binding_id="bind-1",
            type="route",
            agent_id="agent-1",
            match=BindingMatch(channel="telegram"),
        )

        binding_service.delete_binding("bind-1")

        with pytest.raises(KeyError):
            binding_service.get_binding("bind-1")


class TestBindingServiceSync:
    """测试 BindingService 同步到 openclaw.json"""

    @pytest.fixture
    def binding_service(self, temp_config_path):
        """创建 BindingService 实例"""
        from app.services.binding_service import BindingService

        service = BindingService()
        service._openclaw_config_path = temp_config_path
        return service

    def test_bindings_sync_to_openclaw(self, binding_service, temp_config_path):
        """绑定应同步到 openclaw.json"""
        from app.models.binding import BindingMatch

        binding_service.create_binding(
            binding_id="bind-1",
            type="route",
            agent_id="agent-1",
            match=BindingMatch(channel="telegram"),
        )

        # 读取配置
        result = json.loads(temp_config_path.read_text())

        assert "bindings" in result
        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["agentId"] == "agent-1"

    def test_multiple_bindings_sync(self, binding_service, temp_config_path):
        """多个绑定应正确同步"""
        from app.models.binding import BindingMatch

        binding_service.create_binding(
            binding_id="bind-1",
            type="route",
            agent_id="agent-1",
            match=BindingMatch(channel="telegram"),
        )
        binding_service.create_binding(
            binding_id="bind-2",
            type="route",
            agent_id="agent-2",
            match=BindingMatch(channel="discord"),
        )

        result = json.loads(temp_config_path.read_text())

        assert len(result["bindings"]) == 2

    def test_delete_binding_sync(self, binding_service, temp_config_path):
        """删除绑定应同步到 openclaw.json"""
        from app.models.binding import BindingMatch

        binding_service.create_binding(
            binding_id="bind-1",
            type="route",
            agent_id="agent-1",
            match=BindingMatch(channel="telegram"),
        )
        binding_service.create_binding(
            binding_id="bind-2",
            type="route",
            agent_id="agent-2",
            match=BindingMatch(channel="discord"),
        )

        binding_service.delete_binding("bind-1")

        result = json.loads(temp_config_path.read_text())

        assert len(result["bindings"]) == 1
        assert result["bindings"][0]["agentId"] == "agent-2"
