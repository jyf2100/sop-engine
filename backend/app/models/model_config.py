"""模型配置模型。

REQ-0001-XXX: 模型配置管理

支持 LLM、Embedding、Image 三种模型类型的配置。
"""
from datetime import datetime
from typing import Any, Literal

from .base import Base

ModelType = Literal["llm", "embedding", "image"]
ModelProvider = Literal["anthropic", "openai", "google", "cohere", "stability", "custom"]


class ModelConfig(Base):
    """模型配置模型

    存储各类 AI 模型的配置信息，支持 OpenAI 兼容格式。
    """

    id: str
    name: str  # 显示名称
    type: ModelType  # llm | embedding | image
    provider: ModelProvider  # anthropic | openai | google | custom 等

    # 模型标识
    model_id: str  # claude-3-5-sonnet, gpt-4o 等

    # API 配置
    base_url: str
    api_key: str  # 实际使用时加密存储

    # 默认参数
    default_params: dict[str, Any]  # temperature, max_tokens, top_p 等

    # Embedding 专用
    dimensions: int | None = None  # 向量维度

    # Image 专用
    default_size: str | None = None  # 1024x1024 等

    # 元数据
    is_default: bool = False

    created_at: datetime | None = None
    updated_at: datetime | None = None


# 预设模型模板
PRESET_MODELS: list[dict[str, Any]] = [
    # LLM 模型
    {
        "id": "claude-3-5-sonnet",
        "name": "Claude 3.5 Sonnet",
        "type": "llm",
        "provider": "anthropic",
        "model_id": "claude-3-5-sonnet-20241022",
        "base_url": "https://api.anthropic.com",
        "default_params": {"temperature": 0.7, "max_tokens": 4096},
    },
    {
        "id": "claude-3-5-haiku",
        "name": "Claude 3.5 Haiku",
        "type": "llm",
        "provider": "anthropic",
        "model_id": "claude-3-5-haiku-20241022",
        "base_url": "https://api.anthropic.com",
        "default_params": {"temperature": 0.7, "max_tokens": 4096},
    },
    {
        "id": "gpt-4o",
        "name": "GPT-4o",
        "type": "llm",
        "provider": "openai",
        "model_id": "gpt-4o",
        "base_url": "https://api.openai.com/v1",
        "default_params": {"temperature": 0.7, "max_tokens": 4096, "top_p": 1.0},
    },
    {
        "id": "gpt-4o-mini",
        "name": "GPT-4o Mini",
        "type": "llm",
        "provider": "openai",
        "model_id": "gpt-4o-mini",
        "base_url": "https://api.openai.com/v1",
        "default_params": {"temperature": 0.7, "max_tokens": 4096},
    },
    {
        "id": "gemini-2-0-flash",
        "name": "Gemini 2.0 Flash",
        "type": "llm",
        "provider": "google",
        "model_id": "gemini-2.0-flash",
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "default_params": {"temperature": 0.7, "max_tokens": 8192},
    },
    # Embedding 模型
    {
        "id": "text-embedding-3-small",
        "name": "OpenAI text-embedding-3-small",
        "type": "embedding",
        "provider": "openai",
        "model_id": "text-embedding-3-small",
        "base_url": "https://api.openai.com/v1",
        "dimensions": 1536,
        "default_params": {},
    },
    {
        "id": "text-embedding-3-large",
        "name": "OpenAI text-embedding-3-large",
        "type": "embedding",
        "provider": "openai",
        "model_id": "text-embedding-3-large",
        "base_url": "https://api.openai.com/v1",
        "dimensions": 3072,
        "default_params": {},
    },
    # 图像模型
    {
        "id": "dall-e-3",
        "name": "DALL-E 3",
        "type": "image",
        "provider": "openai",
        "model_id": "dall-e-3",
        "base_url": "https://api.openai.com/v1",
        "default_size": "1024x1024",
        "default_params": {"quality": "standard"},
    },
    {
        "id": "stable-diffusion-xl",
        "name": "Stable Diffusion XL",
        "type": "image",
        "provider": "stability",
        "model_id": "stable-diffusion-xl-1024-v1-0",
        "base_url": "https://api.stability.ai",
        "default_size": "1024x1024",
        "default_params": {},
    },
]
