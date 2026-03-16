"""EventBus 测试。

REQ-0001-007: EventBus 实现
"""
import json
import time
from datetime import datetime

import pytest


class TestEventBus:
    """测试 EventBus 抽象类"""

    def test_event_bus_importable(self):
        """REQ-0001-007: EventBus 可导入"""
        from app.services.event_bus import EventBus, MemoryEventBus

        assert EventBus is not None
        assert MemoryEventBus is not None

    def test_memory_event_bus_is_event_bus(self):
        """REQ-0001-007: MemoryEventBus 继承 EventBus"""
        from app.services.event_bus import EventBus, MemoryEventBus

        assert issubclass(MemoryEventBus, EventBus)


class TestMemoryEventBus:
    """测试内存事件总线"""

    @pytest.fixture
    def event_bus(self):
        """创建内存 EventBus 实例"""
        from app.services.event_bus import MemoryEventBus

        return MemoryEventBus(stream_name="test-events")

    def test_publish_consume(self, event_bus):
        """REQ-0001-007: publish 后可通过 consume 读取"""
        event = {
            "type": "node.started",
            "execution_id": "exec-001",
            "node_id": "node-001",
            "timestamp": datetime.utcnow().isoformat(),
        }

        # 发布事件
        event_id = event_bus.publish(event)
        assert event_id is not None

        # 消费事件
        events = event_bus.consume(count=1, block_ms=100)
        assert len(events) >= 1

        # 验证事件内容
        consumed = events[0]
        assert consumed["type"] == "node.started"
        assert consumed["execution_id"] == "exec-001"
        assert consumed["node_id"] == "node-001"

    def test_ack(self, event_bus):
        """REQ-0001-007: ack 后事件标记为已处理"""
        event = {
            "type": "node.completed",
            "execution_id": "exec-002",
            "node_id": "node-002",
            "timestamp": datetime.utcnow().isoformat(),
        }

        event_id = event_bus.publish(event)
        events = event_bus.consume(count=1, block_ms=100)
        assert len(events) >= 1

        # 确认事件
        result = event_bus.ack(events[0]["_id"])
        assert result is True

    def test_event_has_required_fields(self, event_bus):
        """REQ-0001-007: 事件包含 execution_id, node_id, type, timestamp"""
        event = {
            "type": "execution.started",
            "execution_id": "exec-003",
            "node_id": None,  # 执行级别事件没有 node_id
            "timestamp": datetime.utcnow().isoformat(),
        }

        event_bus.publish(event)
        events = event_bus.consume(count=1, block_ms=100)
        assert len(events) >= 1

        consumed = events[0]
        assert "type" in consumed
        assert "execution_id" in consumed
        assert "timestamp" in consumed

    def test_publish_multiple_events(self, event_bus):
        """REQ-0001-007: 发布多个事件"""
        for i in range(5):
            event = {
                "type": "node.started",
                "execution_id": f"exec-{i:03d}",
                "node_id": f"node-{i:03d}",
                "timestamp": datetime.utcnow().isoformat(),
            }
            event_bus.publish(event)

        events = event_bus.consume(count=5, block_ms=500)
        assert len(events) >= 5

    def test_event_types(self, event_bus):
        """REQ-0001-007: 支持各种事件类型"""
        event_types = {
            "node.started",
            "node.completed",
            "node.failed",
            "execution.started",
            "execution.completed",
        }

        for event_type in event_types:
            event = {
                "type": event_type,
                "execution_id": "exec-types",
                "node_id": "node-types",
                "timestamp": datetime.utcnow().isoformat(),
            }
            event_bus.publish(event)

        events = event_bus.consume(count=5, block_ms=500)
        consumed_types = {e["type"] for e in events}
        assert event_types.issubset(consumed_types)

    def test_fifo_order(self, event_bus):
        """REQ-0001-007: 保持 FIFO 顺序"""
        for i in range(5):
            event_bus.publish({"type": "ordered", "seq": i})

        events = event_bus.consume(count=5)
        assert len(events) == 5
        for i, event in enumerate(events):
            assert event["seq"] == i

    def test_clear(self, event_bus):
        """REQ-0001-007: 清空事件队列"""
        event_bus.publish({"type": "test"})
        event_bus.publish({"type": "test2"})

        event_bus.clear()
        events = event_bus.consume(count=10)
        assert len(events) == 0
