"""凭证模型。

REQ-0001-005: OpenClaw 凭证管理

存储 API 密钥等敏感凭证，支持加密存储和脱敏显示。
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class Credential(BaseModel):
    """凭证模型

    存储加密后的凭证信息。
    """

    id: str = Field(..., description="凭证唯一标识")
    name: str = Field(..., description="凭证名称")
    type: str = Field(default="api_key", description="凭证类型: api_key, password, token")
    encrypted_value: str = Field(..., description="加密后的凭证值")
    masked_value: str = Field(..., description="脱敏后的凭证值（用于显示）")
    agent_id: Optional[str] = Field(default=None, description="关联的 Agent ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "cred-001",
                    "name": "OpenAI API Key",
                    "type": "api_key",
                    "encrypted_value": "base64_encrypted_string...",
                    "masked_value": "sk-proj-***",
                    "agent_id": "agent-001",
                }
            ]
        }
    }
