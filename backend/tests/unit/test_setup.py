"""测试依赖安装和项目配置。

REQ-0001-001: 项目骨架搭建
"""
import importlib


def test_fastapi_installed():
    """验证 FastAPI 已安装"""
    fastapi = importlib.import_module("fastapi")
    assert fastapi is not None


def test_sqlalchemy_installed():
    """验证 SQLAlchemy 已安装"""
    sqlalchemy = importlib.import_module("sqlalchemy")
    assert sqlalchemy is not None


def test_pydantic_installed():
    """验证 Pydantic 已安装"""
    pydantic = importlib.import_module("pydantic")
    assert pydantic is not None


def test_asyncpg_installed():
    """验证 asyncpg 已安装"""
    asyncpg = importlib.import_module("asyncpg")
    assert asyncpg is not None


def test_redis_installed():
    """验证 redis 已安装"""
    redis = importlib.import_module("redis")
    assert redis is not None


def test_httpx_installed():
    """验证 httpx 已安装"""
    httpx = importlib.import_module("httpx")
    assert httpx is not None


def test_structlog_installed():
    """验证 structlog 已安装"""
    structlog = importlib.import_module("structlog")
    assert structlog is not None
