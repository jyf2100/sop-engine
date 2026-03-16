"""Template API 测试。

REQ-0001-016: REST API - 模板管理
"""
import pytest

from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """创建测试客户端"""
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_yaml():
    """示例 YAML 模板"""
    return """
name: test-flow
version: "1.0"
nodes:
  start:
    type: start
    next: echo
  echo:
    type: script
    command: echo "Hello"
    next: end
  end:
    type: end
"""


class TestTemplateList:
    """测试模板列表 API"""

    def test_list_templates_empty(self, client):
        """REQ-0001-016: 空列表"""
        response = client.get("/api/templates")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] == 0

    def test_list_templates_with_data(self, client):
        """REQ-0001-016: 有数据"""
        # 先创建一个模板
        client.post("/api/templates", json={
            "name": "test-template",
            "version": "1.0",
            "yaml_content": "name: test\nversion: '1.0'\nnodes: {}\n",
        })

        response = client.get("/api/templates")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
        assert len(data["items"]) >= 1

    def test_list_templates_pagination(self, client):
        """REQ-0001-016: 分页"""
        # 创建多个模板
        for i in range(5):
            client.post("/api/templates", json={
                "name": f"template-{i}",
                "version": "1.0",
                "yaml_content": f"name: template-{i}\nversion: '1.0'\nnodes: {{}}\n",
            })

        # 第一页
        response = client.get("/api/templates?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2

        # 第二页
        response = client.get("/api/templates?skip=2&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 2


class TestTemplateCreate:
    """测试模板创建 API"""

    def test_create_template(self, client):
        """REQ-0001-016: 创建成功"""
        response = client.post("/api/templates", json={
            "name": "new-template",
            "version": "1.0",
            "yaml_content": "name: new-template\nversion: '1.0'\nnodes: {}\n",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "new-template"
        assert "id" in data

    def test_create_template_missing_name(self, client):
        """REQ-0001-016: 缺少名称"""
        response = client.post("/api/templates", json={
            "version": "1.0",
            "yaml_content": "name: test\n",
        })
        assert response.status_code == 422


class TestTemplateGet:
    """测试模板详情 API"""

    def test_get_template(self, client):
        """REQ-0001-016: 获取详情"""
        # 先创建
        create_response = client.post("/api/templates", json={
            "name": "get-template",
            "version": "1.0",
            "yaml_content": "name: get-template\nversion: '1.0'\nnodes: {}\n",
        })
        template_id = create_response.json()["id"]

        response = client.get(f"/api/templates/{template_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "get-template"

    def test_get_template_not_found(self, client):
        """REQ-0001-016: 不存在"""
        response = client.get("/api/templates/nonexistent-id")
        assert response.status_code == 404


class TestTemplateDelete:
    """测试模板删除 API"""

    def test_delete_template(self, client):
        """REQ-0001-016: 删除成功"""
        # 先创建
        create_response = client.post("/api/templates", json={
            "name": "delete-template",
            "version": "1.0",
            "yaml_content": "name: delete-template\nversion: '1.0'\nnodes: {}\n",
        })
        template_id = create_response.json()["id"]

        response = client.delete(f"/api/templates/{template_id}")
        assert response.status_code == 204

        # 验证已删除
        get_response = client.get(f"/api/templates/{template_id}")
        assert get_response.status_code == 404

    def test_delete_template_not_found(self, client):
        """REQ-0001-016: 删除不存在的模板"""
        response = client.delete("/api/templates/nonexistent-id")
        assert response.status_code == 404


class TestTemplateUpload:
    """测试 YAML 上传 API"""

    def test_upload_yaml(self, client, sample_yaml):
        """REQ-0001-016: 上传 YAML 成功"""
        response = client.post(
            "/api/templates/upload",
            content=sample_yaml,
            headers={"Content-Type": "text/yaml"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test-flow"
        assert "id" in data

    def test_upload_invalid_yaml(self, client):
        """REQ-0001-016: 无效 YAML"""
        response = client.post(
            "/api/templates/upload",
            content="invalid: yaml: content:",
            headers={"Content-Type": "text/yaml"},
        )
        assert response.status_code == 400

    def test_upload_missing_name(self, client):
        """REQ-0001-016: 缺少 name 字段"""
        yaml_content = """
version: "1.0"
nodes:
  end:
    type: end
"""
        response = client.post(
            "/api/templates/upload",
            content=yaml_content,
            headers={"Content-Type": "text/yaml"},
        )
        # 应该成功，因为 name 会默认为 "unnamed"
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "unnamed"
