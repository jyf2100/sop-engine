"""Execution API 测试。

REQ-0001-017: REST API - 执行管理
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
def template_yaml():
    """示例模板 YAML"""
    return """
name: test-flow
version: "1.0"
params:
  - name: user
    type: string
    default: World
nodes:
  start:
    type: start
    next: echo
  echo:
    type: script
    command: echo "Hello {user}"
    next: end
  end:
    type: end
"""


@pytest.fixture
def template_id(client, template_yaml):
    """创建模板并返回 ID"""
    response = client.post(
        "/api/templates/upload",
        content=template_yaml,
        headers={"Content-Type": "text/yaml"},
    )
    return response.json()["id"]


class TestExecutionStart:
    """测试执行启动 API"""

    def test_start_execution(self, client, template_id):
        """REQ-0001-017: 启动执行成功"""
        response = client.post("/api/executions", json={
            "template_id": template_id,
            "params": {"user": "TestUser"},
        })
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["status"] in ("pending", "running")

    def test_start_execution_missing_template(self, client):
        """REQ-0001-017: 模板不存在"""
        response = client.post("/api/executions", json={
            "template_id": "nonexistent-template",
            "params": {},
        })
        assert response.status_code == 404

    def test_start_execution_invalid_params(self, client, template_id):
        """REQ-0001-017: 参数验证失败"""
        response = client.post("/api/executions", json={
            "template_id": template_id,
            # 缺少 params 字段
        })
        assert response.status_code == 422


class TestExecutionList:
    """测试执行列表 API"""

    def test_list_executions_empty(self, client):
        """REQ-0001-017: 空列表"""
        response = client.get("/api/executions")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_list_executions_with_data(self, client, template_id):
        """REQ-0001-017: 有数据"""
        # 先创建一个执行
        client.post("/api/executions", json={
            "template_id": template_id,
            "params": {},
        })

        response = client.get("/api/executions")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    def test_list_executions_filter_by_status(self, client, template_id):
        """REQ-0001-017: 按状态过滤"""
        response = client.get("/api/executions?status=running")
        assert response.status_code == 200
        data = response.json()
        # 验证所有返回的执行都是 running 状态
        for item in data["items"]:
            assert item["status"] == "running"

    def test_list_executions_pagination(self, client, template_id):
        """REQ-0001-017: 分页"""
        # 创建多个执行
        for i in range(5):
            client.post("/api/executions", json={
                "template_id": template_id,
                "params": {"user": f"user-{i}"},
            })

        response = client.get("/api/executions?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 2


class TestExecutionGet:
    """测试执行详情 API"""

    def test_get_execution(self, client, template_id):
        """REQ-0001-017: 获取详情"""
        # 先创建
        create_response = client.post("/api/executions", json={
            "template_id": template_id,
            "params": {},
        })
        execution_id = create_response.json()["id"]

        response = client.get(f"/api/executions/{execution_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == execution_id
        assert "status" in data

    def test_get_execution_not_found(self, client):
        """REQ-0001-017: 不存在"""
        response = client.get("/api/executions/nonexistent-id")
        assert response.status_code == 404


class TestExecutionCancel:
    """测试执行取消 API"""

    def test_cancel_execution(self, client, template_id):
        """REQ-0001-017: 取消执行"""
        # 先创建
        create_response = client.post("/api/executions", json={
            "template_id": template_id,
            "params": {},
        })
        execution_id = create_response.json()["id"]

        response = client.post(f"/api/executions/{execution_id}/cancel")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"

    def test_cancel_execution_not_found(self, client):
        """REQ-0001-017: 取消不存在的执行"""
        response = client.post("/api/executions/nonexistent-id/cancel")
        assert response.status_code == 404

    def test_cancel_completed_execution(self, client, template_id):
        """REQ-0001-017: 取消已完成的执行"""
        # 先创建
        create_response = client.post("/api/executions", json={
            "template_id": template_id,
            "params": {},
        })
        execution_id = create_response.json()["id"]

        # 第一次取消成功
        response = client.post(f"/api/executions/{execution_id}/cancel")
        assert response.status_code == 200

        # 第二次取消（已经是 cancelled 状态）应该失败
        response = client.post(f"/api/executions/{execution_id}/cancel")
        assert response.status_code == 400


class TestExecutionNodes:
    """测试节点执行列表 API"""

    def test_list_execution_nodes(self, client, template_id):
        """REQ-0001-017: 获取节点执行列表"""
        # 先创建执行
        create_response = client.post("/api/executions", json={
            "template_id": template_id,
            "params": {},
        })
        execution_id = create_response.json()["id"]

        response = client.get(f"/api/executions/{execution_id}/nodes")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_list_execution_nodes_not_found(self, client):
        """REQ-0001-017: 执行不存在"""
        response = client.get("/api/executions/nonexistent-id/nodes")
        assert response.status_code == 404
