"""测试配置模块。

REQ-0001-001: 项目骨架搭建
"""


def test_config_has_database_url():
    """REQ-0001-001: 验证配置包含 DATABASE_URL"""
    from app.config import settings

    assert hasattr(settings, "database_url")
    assert settings.database_url is not None


def test_config_has_redis_url():
    """REQ-0001-001: 验证配置包含 REDIS_URL"""
    from app.config import settings

    assert hasattr(settings, "redis_url")
    assert settings.redis_url is not None


def test_config_has_openclaw_settings():
    """REQ-0001-001: 验证配置包含 OpenClaw 设置"""
    from app.config import settings

    assert hasattr(settings, "openclaw_url")
    assert hasattr(settings, "openclaw_token")
    assert hasattr(settings, "openclaw_timeout")
    assert hasattr(settings, "openclaw_workspace_root")


def test_config_has_credential_encryption_key():
    """REQ-0001-005: 验证配置包含凭证加密密钥"""
    from app.config import settings

    assert hasattr(settings, "credential_encryption_key")


def test_config_has_environment():
    """REQ-0001-001: 验证配置包含运行环境"""
    from app.config import settings

    assert hasattr(settings, "environment")


def test_config_has_log_level():
    """REQ-0001-001: 验证配置包含日志级别"""
    from app.config import settings

    assert hasattr(settings, "log_level")
