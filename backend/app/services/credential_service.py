"""凭证管理服务。

REQ-0001-005: OpenClaw 凭证管理

提供凭证的加密存储、解密、脱敏等功能。
"""
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from app.models.credential import Credential
from app.utils.crypto import decrypt, encrypt, mask_credential


class CredentialNotFoundError(Exception):
    """凭证不存在异常"""

    pass


class CredentialService:
    """凭证管理服务

    负责凭证的 CRUD 操作和加密/解密处理。
    """

    def __init__(
        self,
        storage_path: Path | str,
        encryption_key: bytes,
    ):
        if isinstance(storage_path, str):
            storage_path = Path(storage_path)

        self.storage_path = storage_path
        self.storage_file = storage_path / "credentials.json"
        self.encryption_key = encryption_key
        self._credentials: dict[str, Credential] | None = None

    def _load_credentials(self) -> dict[str, Credential]:
        """加载凭证存储"""
        if self._credentials is not None:
            return self._credentials

        if not self.storage_file.exists():
            self._credentials = {}
            return self._credentials

        content = self.storage_file.read_text()
        data = json.loads(content)
        self._credentials = {
            cred_id: Credential(**cred_data)
            for cred_id, cred_data in data.items()
        }
        return self._credentials

    def _save_credentials(self) -> None:
        """保存凭证存储"""
        if self._credentials is None:
            return

        # 确保目录存在
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # 原子写入
        temp_path = self.storage_file.with_suffix(".tmp")
        try:
            data = {
                cred_id: cred.model_dump(mode="json")
                for cred_id, cred in self._credentials.items()
            }
            temp_path.write_text(json.dumps(data, indent=2, default=str))
            shutil.move(str(temp_path), str(self.storage_file))
        except Exception:
            if temp_path.exists():
                temp_path.unlink()
            raise

    def create_credential(
        self,
        id: str,
        name: str,
        plaintext: str,
        type: str = "api_key",
        agent_id: Optional[str] = None,
    ) -> Credential:
        """创建凭证

        Args:
            id: 凭证唯一标识
            name: 凭证名称
            plaintext: 明文凭证值
            type: 凭证类型
            agent_id: 关联的 Agent ID

        Returns:
            创建的凭证对象（加密后）

        Raises:
            ValueError: ID 已存在
        """
        credentials = self._load_credentials()

        if id in credentials:
            raise ValueError(f"Credential '{id}' already exists")

        # 加密
        encrypted_value = encrypt(plaintext, self.encryption_key)
        masked_value = mask_credential(plaintext)

        now = datetime.utcnow()
        credential = Credential(
            id=id,
            name=name,
            type=type,
            encrypted_value=encrypted_value,
            masked_value=masked_value,
            agent_id=agent_id,
            created_at=now,
            updated_at=now,
        )

        credentials[id] = credential
        self._save_credentials()

        return credential

    def get_credential(self, credential_id: str) -> Credential:
        """获取凭证（脱敏）

        Args:
            credential_id: 凭证 ID

        Returns:
            凭证对象（不包含明文）

        Raises:
            CredentialNotFoundError: 凭证不存在
        """
        credentials = self._load_credentials()

        if credential_id not in credentials:
            raise CredentialNotFoundError(f"Credential '{credential_id}' not found")

        return credentials[credential_id]

    def decrypt_credential(self, credential_id: str) -> str:
        """解密凭证

        Args:
            credential_id: 凭证 ID

        Returns:
            明文凭证值

        Raises:
            CredentialNotFoundError: 凭证不存在
        """
        credential = self.get_credential(credential_id)
        return decrypt(credential.encrypted_value, self.encryption_key)

    def update_credential(
        self,
        credential_id: str,
        name: Optional[str] = None,
        plaintext: Optional[str] = None,
        type: Optional[str] = None,
        agent_id: Optional[str] = None,
    ) -> Credential:
        """更新凭证

        Args:
            credential_id: 凭证 ID
            name: 新名称（可选）
            plaintext: 新明文值（可选）
            type: 新类型（可选）
            agent_id: 新 Agent ID（可选）

        Returns:
            更新后的凭证对象

        Raises:
            CredentialNotFoundError: 凭证不存在
        """
        credentials = self._load_credentials()

        if credential_id not in credentials:
            raise CredentialNotFoundError(f"Credential '{credential_id}' not found")

        old_credential = credentials[credential_id]

        # 更新字段
        new_name = name if name is not None else old_credential.name
        new_type = type if type is not None else old_credential.type
        new_agent_id = agent_id if agent_id is not None else old_credential.agent_id

        # 处理加密值
        if plaintext is not None:
            encrypted_value = encrypt(plaintext, self.encryption_key)
            masked_value = mask_credential(plaintext)
        else:
            encrypted_value = old_credential.encrypted_value
            masked_value = old_credential.masked_value

        updated_credential = Credential(
            id=credential_id,
            name=new_name,
            type=new_type,
            encrypted_value=encrypted_value,
            masked_value=masked_value,
            agent_id=new_agent_id,
            created_at=old_credential.created_at,
            updated_at=datetime.utcnow(),
        )

        credentials[credential_id] = updated_credential
        self._save_credentials()

        return updated_credential

    def delete_credential(self, credential_id: str) -> None:
        """删除凭证

        Args:
            credential_id: 凭证 ID

        Raises:
            CredentialNotFoundError: 凭证不存在
        """
        credentials = self._load_credentials()

        if credential_id not in credentials:
            raise CredentialNotFoundError(f"Credential '{credential_id}' not found")

        del credentials[credential_id]
        self._save_credentials()

    def list_credentials(
        self,
        agent_id: Optional[str] = None,
    ) -> list[Credential]:
        """列出凭证

        Args:
            agent_id: 筛选指定 Agent 的凭证（可选）

        Returns:
            凭证列表（脱敏）
        """
        credentials = self._load_credentials()

        result = list(credentials.values())

        if agent_id is not None:
            result = [c for c in result if c.agent_id == agent_id]

        return result
