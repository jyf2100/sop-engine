"""凭证同步集成测试。

REQ-0001-005: OpenClaw 凭证管理

测试凭证同步到 OpenClaw workspace 的功能。
"""
import json
import tempfile
from pathlib import Path

import pytest

from app.services.credential_service import CredentialService
from app.services.openclaw_sync import OpenClawSyncService
from app.utils.crypto import generate_key


class TestCredentialSync:
    """测试凭证同步"""

    @pytest.fixture
    def temp_workspace(self):
        """临时 OpenClaw workspace"""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)

            # 创建初始 openclaw.json
            openclaw_json = workspace / "openclaw.json"
            openclaw_json.write_text(json.dumps({
                "agents": {"list": [], "defaults": {}},
                "bindings": []
            }))

            # 创建 agents 目录
            (workspace / "agents").mkdir()

            yield workspace

    @pytest.fixture
    def credential_storage(self):
        """临时凭证存储目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def encryption_key(self):
        """加密密钥"""
        return generate_key()

    @pytest.fixture
    def credential_service(self, credential_storage, encryption_key):
        """凭证服务"""
        return CredentialService(
            storage_path=credential_storage,
            encryption_key=encryption_key,
        )

    @pytest.fixture
    def openclaw_sync(self, temp_workspace):
        """OpenClaw 同步服务"""
        return OpenClawSyncService(workspace_root=temp_workspace)

    def test_sync_credentials(self, credential_service, openclaw_sync, temp_workspace):
        """REQ-0001-005: 凭证同步到 OpenClaw"""
        # 创建凭证
        credential_service.create_credential(
            id="cred-001",
            name="OpenAI API Key",
            plaintext="sk-proj-1234567890abcdef",
            agent_id="agent-001",
        )

        # 同步凭证到 OpenClaw
        credentials = credential_service.list_credentials()
        openclaw_sync.sync_credentials(credentials)

        # 验证凭证文件已创建
        cred_file = temp_workspace / ".credentials" / "cred-001.json"
        assert cred_file.exists()

        # 验证文件内容（应该是脱敏的）
        content = json.loads(cred_file.read_text())
        assert content["id"] == "cred-001"
        assert content["name"] == "OpenAI API Key"
        assert content["masked_value"] == "sk-proj-***"
        # 不应该包含明文
        assert "sk-proj-1234567890abcdef" not in json.dumps(content)

    def test_sync_credentials_creates_directory(
        self, credential_service, openclaw_sync, temp_workspace
    ):
        """REQ-0001-005: 自动创建凭证目录"""
        credential_service.create_credential(
            id="cred-002",
            name="Test Key",
            plaintext="test-value",
        )

        credentials = credential_service.list_credentials()
        openclaw_sync.sync_credentials(credentials)

        # 验证目录已创建
        cred_dir = temp_workspace / ".credentials"
        assert cred_dir.exists()
        assert cred_dir.is_dir()

    def test_sync_multiple_credentials(
        self, credential_service, openclaw_sync, temp_workspace
    ):
        """REQ-0001-005: 同步多个凭证"""
        credential_service.create_credential(
            id="cred-003",
            name="Key 1",
            plaintext="value-1",
        )
        credential_service.create_credential(
            id="cred-004",
            name="Key 2",
            plaintext="value-2",
        )

        credentials = credential_service.list_credentials()
        openclaw_sync.sync_credentials(credentials)

        # 验证两个凭证文件都已创建
        cred_dir = temp_workspace / ".credentials"
        assert len(list(cred_dir.glob("*.json"))) == 2

    def test_sync_removes_deleted_credentials(
        self, credential_service, openclaw_sync, temp_workspace
    ):
        """REQ-0001-005: 删除的凭证会被清理"""
        # 创建并同步
        credential_service.create_credential(
            id="cred-005",
            name="To Delete",
            plaintext="delete-me",
        )

        credentials = credential_service.list_credentials()
        openclaw_sync.sync_credentials(credentials)

        cred_file = temp_workspace / ".credentials" / "cred-005.json"
        assert cred_file.exists()

        # 删除凭证
        credential_service.delete_credential("cred-005")

        # 再次同步
        credentials = credential_service.list_credentials()
        openclaw_sync.sync_credentials(credentials)

        # 验证文件已删除
        assert not cred_file.exists()
