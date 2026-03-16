"""测试 FastAPI 主入口。

REQ-0001-001: 项目骨架搭建
"""
from fastapi.testclient import TestClient


def test_main_app_exists():
    """验证 FastAPI 应用存在"""
    from app.main import app

    assert app is not None
    assert app.title == "SOP Engine"


def test_health_check():
    """验证健康检查端点"""
    from app.main import app

    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_docs():
    """验证 OpenAPI 文档可访问"""
    from app.main import app

    client = TestClient(app)
    response = client.get("/docs")
    assert response.status_code == 200


def test_root_endpoint():
    """验证根路径返回 API 信息"""
    from app.main import app

    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
