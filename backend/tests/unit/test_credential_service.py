"""凭证服务测试。

REQ-0001-005: OpenClaw 凭证管理
"""
import os
import tempfile
from pathlib import Path

import pytest

from app.utils.crypto import generate_key, key_to_base64


class TestCredentialService:
    """测试凭证服务"""

    @pytest.fixture
    def temp_storage(self):
        """临时存储目录"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def encryption_key(self):
        """生成加密密钥"""
        return generate_key()

    @pytest.fixture
    def credential_service(self, temp_storage, encryption_key):
        """创建 CredentialService 实例"""
        from app.services.credential_service import CredentialService

        return CredentialService(
            storage_path=temp_storage,
            encryption_key=encryption_key,
        )

    def test_service_importable(self):
        """REQ-0001-005: 服务可导入"""
        from app.services.credential_service import CredentialService

        assert CredentialService is not None

    def test_encrypt_credential(self, credential_service):
        """REQ-0001-005: 加密凭证"""
        credential = credential_service.create_credential(
            id="cred-001",
            name="OpenAI API Key",
            plaintext="sk-proj-1234567890abcdef",
        )

        assert credential.id == "cred-001"
        assert credential.name == "OpenAI API Key"
        assert credential.encrypted_value != "sk-proj-1234567890abcdef"
        assert credential.masked_value == "sk-proj-***"

    def test_decrypt_credential(self, credential_service):
        """REQ-0001-005: 解密凭证"""
        plaintext = "my-secret-api-key-12345"

        credential = credential_service.create_credential(
            id="cred-002",
            name="Test Key",
            plaintext=plaintext,
        )

        decrypted = credential_service.decrypt_credential(credential.id)
        assert decrypted == plaintext

    def test_get_credential_not_found(self, credential_service):
        """REQ-0001-005: 获取不存在的凭证"""
        from app.services.credential_service import CredentialNotFoundError

        with pytest.raises(CredentialNotFoundError):
            credential_service.get_credential("non-existent")

    def test_update_credential(self, credential_service):
        """REQ-0001-005: 更新凭证"""
        # 先创建
        credential_service.create_credential(
            id="cred-003",
            name="Original Name",
            plaintext="original-value",
        )

        # 更新
        updated = credential_service.update_credential(
            credential_id="cred-003",
            name="Updated Name",
            plaintext="updated-value",
        )

        assert updated.name == "Updated Name"
        assert credential_service.decrypt_credential("cred-003") == "updated-value"

    def test_delete_credential(self, credential_service):
        """REQ-0001-005: 删除凭证"""
        from app.services.credential_service import CredentialNotFoundError

        # 创建
        credential_service.create_credential(
            id="cred-004",
            name="To Delete",
            plaintext="delete-me",
        )

        # 删除
        credential_service.delete_credential("cred-004")

        # 验证已删除
        with pytest.raises(CredentialNotFoundError):
            credential_service.get_credential("cred-004")

    def test_list_credentials(self, credential_service):
        """REQ-0001-005: 列出凭证"""
        credential_service.create_credential(
            id="cred-005",
            name="Key 1",
            plaintext="value-1",
        )
        credential_service.create_credential(
            id="cred-006",
            name="Key 2",
            plaintext="value-2",
        )

        credentials = credential_service.list_credentials()
        assert len(credentials) == 2
        # 验证脱敏
        for cred in credentials:
            assert "***" in cred.masked_value

    def test_mask_credential_short(self, credential_service):
        """REQ-0001-005: 短凭证脱敏"""
        credential = credential_service.create_credential(
            id="cred-007",
            name="Short Key",
            plaintext="abc",
        )

        assert credential.masked_value == "***"

    def test_list_credentials_by_agent(self, credential_service):
        """REQ-0001-005: 按 Agent ID 筛选凭证"""
        credential_service.create_credential(
            id="cred-008",
            name="Agent 1 Key",
            plaintext="value-1",
            agent_id="agent-001",
        )
        credential_service.create_credential(
            id="cred-009",
            name="Agent 2 Key",
            plaintext="value-2",
            agent_id="agent-002",
        )

        credentials = credential_service.list_credentials(agent_id="agent-001")
        assert len(credentials) == 1
        assert credentials[0].agent_id == "agent-001"
