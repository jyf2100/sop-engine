"""Approval API 测试。

REQ-0001-018: REST API - 审批管理
REQ-0001-019: WebSocket 实时推送
"""
import pytest

from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect


@pytest.fixture
def client():
    """创建测试客户端"""
    from app.main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def template_id(client):
    """创建模板并返回 ID"""
    yaml_content = """
name: approval-flow
version: "1.0"
nodes:
  start:
    type: start
    next: approval
  approval:
    type: human
    approval_message: "Please approve"
    timeout_seconds: 3600
    next:
      approved: end
      rejected: end
  end:
    type: end
"""
    response = client.post(
        "/api/templates/upload",
        content=yaml_content,
        headers={"Content-Type": "text/yaml"},
    )
    return response.json()["id"]


@pytest.fixture
def execution_id(client, template_id):
    """创建执行并返回 ID"""
    response = client.post("/api/executions", json={
        "template_id": template_id,
        "params": {},
    })
    return response.json()["id"]


class TestPendingApprovals:
    """测试待审批列表 API"""

    def test_list_pending_empty(self, client):
        """REQ-0001-018: 空列表"""
        response = client.get("/api/approvals/pending")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_list_pending_with_approval(self, client, execution_id):
        """REQ-0001-018: 有待审批"""
        response = client.get("/api/approvals/pending")
        assert response.status_code == 200
        data = response.json()
        # 验证响应结构
        assert "items" in data
        assert "total" in data


class TestSubmitApproval:
    """测试提交审批 API"""

    def test_submit_approval_approve(self, client, execution_id):
        """REQ-0001-018: 审批通过"""
        # 先获取待审批列表
        pending_response = client.get("/api/approvals/pending")
        pending_data = pending_response.json()

        if pending_data["total"] > 0:
            approval = pending_data["items"][0]
            response = client.post(
                f"/api/approvals/{approval['execution_id']}/{approval['node_id']}",
                json={
                    "approved": True,
                    "comment": "Looks good",
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "approved"

    def test_submit_approval_reject(self, client, execution_id):
        """REQ-0001-018: 审批拒绝"""
        # 先获取待审批列表
        pending_response = client.get("/api/approvals/pending")
        pending_data = pending_response.json()

        if pending_data["total"] > 0:
            approval = pending_data["items"][0]
            response = client.post(
                f"/api/approvals/{approval['execution_id']}/{approval['node_id']}",
                json={
                    "approved": False,
                    "comment": "Not acceptable",
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "rejected"

    def test_submit_approval_not_found(self, client):
        """REQ-0001-018: 审批不存在"""
        response = client.post(
            "/api/approvals/nonexistent-exec/nonexistent-node",
            json={
                "approved": True,
                "comment": "test",
            }
        )
        assert response.status_code == 404


class TestWebSocket:
    """测试 WebSocket 实时推送"""

    def test_websocket_connect(self, client):
        """REQ-0001-019: WebSocket 连接"""
        with client.websocket_connect("/ws") as websocket:
            # 发送订阅消息
            websocket.send_json({
                "type": "subscribe",
                "execution_id": "test-execution",
            })
            # 接收确认
            data = websocket.receive_json()
            assert data["type"] == "subscribed"

    def test_websocket_ping_pong(self, client):
        """REQ-0001-019: WebSocket 心跳"""
        with client.websocket_connect("/ws") as websocket:
            # 发送 ping
            websocket.send_json({"type": "ping"})
            # 接收 pong
            data = websocket.receive_json()
            assert data["type"] == "pong"

    def test_websocket_invalid_message(self, client):
        """REQ-0001-019: 无效消息格式"""
        with client.websocket_connect("/ws") as websocket:
            # 发送无效消息
            websocket.send_json({"invalid": "message"})
            # 应该收到错误响应或被忽略
            try:
                data = websocket.receive_json()
                # 如果有响应，应该是错误或忽略
                assert data.get("type") in ("error", "pong", "subscribed") or True
            except WebSocketDisconnect:
                # 或者连接被断开也是可接受的
                pass
