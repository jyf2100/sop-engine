"""Agent API 测试。

REQ-0001-015: REST API - Agent 管理
"""
import pytest
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """创建测试客户端"""
    from app.main import app
    from app.services.agent_service import AgentService

    with TemporaryDirectory() as tmpdir:
        # 创建 AgentService 并注入到 app state
        service = AgentService(workspace_root=Path(tmpdir))
        app.state.agent_service = service

        with TestClient(app) as test_client:
            yield test_client


class TestAgentList:
    """测试 Agent 列表 API"""

    def test_list_agents_empty(self, client):
        """REQ-0001-015: 空列表"""
        response = client.get("/api/agents")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_agents_with_data(self, client):
        """REQ-0001-015: 有数据"""
        # 先创建一个 Agent
        client.post("/api/agents", json={
            "id": "agent-1",
            "name": "Test Agent",
        })

        response = client.get("/api/agents")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == "agent-1"
        assert data[0]["name"] == "Test Agent"


class TestAgentCreate:
    """测试 Agent 创建 API"""

    def test_create_agent(self, client):
        """REQ-0001-015: 创建成功"""
        response = client.post("/api/agents", json={
            "id": "new-agent",
            "name": "New Agent",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "new-agent"
        assert data["name"] == "New Agent"
        assert "workspace_path" in data

    def test_create_agent_with_config(self, client):
        """REQ-0001-015: 创建时带配置"""
        response = client.post("/api/agents", json={
            "id": "configured-agent",
            "name": "Configured Agent",
            "llm_config": {"primary": "claude-3-opus"},
            "sandbox_config": {"mode": "all"},
            "tools_config": {"allow": ["bash"]},
        })
        assert response.status_code == 201
        data = response.json()
        assert data["llm_config"]["primary"] == "claude-3-opus"

    def test_create_duplicate_agent(self, client):
        """REQ-0001-015: 重复创建失败"""
        client.post("/api/agents", json={
            "id": "dup-agent",
            "name": "Dup Agent",
        })

        response = client.post("/api/agents", json={
            "id": "dup-agent",
            "name": "Dup Agent 2",
        })
        assert response.status_code == 400

    def test_create_agent_missing_id(self, client):
        """REQ-0001-015: 缺少 id"""
        response = client.post("/api/agents", json={
            "name": "No ID Agent",
        })
        assert response.status_code == 422


class TestAgentGet:
    """测试 Agent 详情 API"""

    def test_get_agent(self, client):
        """REQ-0001-015: 获取详情"""
        client.post("/api/agents", json={
            "id": "get-agent",
            "name": "Get Agent",
        })

        response = client.get("/api/agents/get-agent")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "get-agent"
        assert data["name"] == "Get Agent"

    def test_get_agent_not_found(self, client):
        """REQ-0001-015: 不存在"""
        response = client.get("/api/agents/nonexistent")
        assert response.status_code == 404


class TestAgentUpdate:
    """测试 Agent 更新 API"""

    def test_update_agent_name(self, client):
        """REQ-0001-015: 更新名称"""
        client.post("/api/agents", json={
            "id": "update-agent",
            "name": "Original Name",
        })

        response = client.patch("/api/agents/update-agent", json={
            "name": "Updated Name",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"

    def test_update_agent_config(self, client):
        """REQ-0001-015: 更新配置"""
        client.post("/api/agents", json={
            "id": "config-agent",
            "name": "Config Agent",
        })

        response = client.patch("/api/agents/config-agent", json={
            "llm_config": {"primary": "gpt-4"},
        })
        assert response.status_code == 200
        data = response.json()
        assert data["llm_config"]["primary"] == "gpt-4"

    def test_update_agent_not_found(self, client):
        """REQ-0001-015: 更新不存在的 Agent"""
        response = client.patch("/api/agents/nonexistent", json={
            "name": "New Name",
        })
        assert response.status_code == 404


class TestAgentDelete:
    """测试 Agent 删除 API"""

    def test_delete_agent(self, client):
        """REQ-0001-015: 删除成功"""
        client.post("/api/agents", json={
            "id": "delete-agent",
            "name": "Delete Agent",
        })

        response = client.delete("/api/agents/delete-agent")
        assert response.status_code == 204

        # 验证已删除
        get_response = client.get("/api/agents/delete-agent")
        assert get_response.status_code == 404

    def test_delete_agent_not_found(self, client):
        """REQ-0001-015: 删除不存在的 Agent"""
        response = client.delete("/api/agents/nonexistent")
        assert response.status_code == 404


class TestAgentConfigFiles:
    """测试 Agent 配置文件 API"""

    def test_list_config_files(self, client):
        """REQ-0001-015: 列出配置文件"""
        client.post("/api/agents", json={
            "id": "files-agent",
            "name": "Files Agent",
        })

        response = client.get("/api/agents/files-agent/files")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 4  # AGENTS.md, SOUL.md, USER.md, IDENTITY.md

    def test_get_config_file(self, client):
        """REQ-0001-015: 获取配置文件内容"""
        client.post("/api/agents", json={
            "id": "file-agent",
            "name": "File Agent",
        })

        response = client.get("/api/agents/file-agent/files/AGENTS.md")
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "AGENTS" in data["content"] or "Agent" in data["content"]

    def test_get_config_file_not_found(self, client):
        """REQ-0001-015: 配置文件不存在"""
        client.post("/api/agents", json={
            "id": "nofile-agent",
            "name": "No File Agent",
        })

        response = client.get("/api/agents/nofile-agent/files/NOTEXIST.md")
        assert response.status_code == 404

    def test_update_config_file(self, client):
        """REQ-0001-015: 更新配置文件"""
        client.post("/api/agents", json={
            "id": "update-file-agent",
            "name": "Update File Agent",
        })

        response = client.put(
            "/api/agents/update-file-agent/files/AGENTS.md",
            json={"content": "# Updated AGENTS\n\nNew content here."}
        )
        assert response.status_code == 200
        data = response.json()
        assert "Updated AGENTS" in data["content"]

        # 验证更新成功
        get_response = client.get("/api/agents/update-file-agent/files/AGENTS.md")
        assert "Updated AGENTS" in get_response.json()["content"]

    def test_update_config_file_agent_not_found(self, client):
        """REQ-0001-015: Agent 不存在时更新配置文件"""
        response = client.put(
            "/api/agents/nonexistent/files/AGENTS.md",
            json={"content": "content"}
        )
        assert response.status_code == 404


class TestAgentSync:
    """测试 Agent 同步 API"""

    def test_sync_agent(self, client):
        """REQ-0001-015: 手动同步"""
        client.post("/api/agents", json={
            "id": "sync-agent",
            "name": "Sync Agent",
        })

        response = client.post("/api/agents/sync-agent/sync")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "synced"

    def test_sync_agent_not_found(self, client):
        """REQ-0001-015: 同步不存在的 Agent"""
        response = client.post("/api/agents/nonexistent/sync")
        assert response.status_code == 404
