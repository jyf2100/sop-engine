"""应用配置模块。

使用 pydantic-settings 从环境变量加载配置。
所有敏感信息必须通过环境变量设置，禁止硬编码。
"""
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # 数据库配置
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/sop_engine"

    # Redis 配置
    redis_url: str = "redis://localhost:6379/0"

    # OpenClaw 配置
    openclaw_url: str = "http://localhost:18789"
    openclaw_token: str = ""
    openclaw_timeout: int = 30
    openclaw_workspace_root: str = "~/.openclaw"

    # 凭证加密配置
    credential_encryption_key: str = ""

    # 应用配置
    environment: str = "development"
    log_level: str = "INFO"
    port: int = 8000

    @field_validator("openclaw_token", "credential_encryption_key")
    @classmethod
    def validate_production_secrets(cls, v: str, info) -> str:
        """生产环境必须设置敏感配置"""
        if info.data.get("environment") == "production":
            if not v:
                raise ValueError(f"{info.field_name} must be set in production")
        return v


@lru_cache
def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()


# 全局配置实例
settings = get_settings()
