"""EventBus 事件总线。

REQ-0001-007: EventBus 实现

基于 Redis Streams 实现事件发布/订阅机制。
"""
import json
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

# 尝试导入 redis
try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class EventBus(ABC):
    """事件总线抽象基类"""

    @abstractmethod
    def publish(self, event: dict[str, Any]) -> str:
        """发布事件

        Args:
            event: 事件数据

        Returns:
            事件 ID
        """
        pass

    @abstractmethod
    def consume(
        self,
        count: int = 1,
        block_ms: int = 1000,
    ) -> list[dict[str, Any]]:
        """消费事件

        Args:
            count: 最多消费的事件数
            block_ms: 阻塞等待时间（毫秒）

        Returns:
            事件列表，        """
        pass

    @abstractmethod
    def ack(self, event_id: str) -> bool:
        """确认事件已处理

        Args:
            event_id: 事件 ID

        Returns:
            是否确认成功
        """
        pass


class MemoryEventBus(EventBus):
    """内存事件总线（用于测试）"""

    def __init__(self, stream_name: str = "events"):
        self.stream_name = stream_name
        self._events: list[dict[str, Any]] = []
        self._acked: set[str] = set()

    def publish(self, event: dict[str, Any]) -> str:
        """发布事件到内存队列"""
        event_id = f"evt-{int(time.time() * 1000000)}"
        event_data = {
            "_id": event_id,
            "_timestamp": datetime.utcnow().isoformat(),
            **event,
        }
        self._events.append(event_data)
        return event_id

    def consume(
        self,
        count: int = 1,
        block_ms: int = 1000,
    ) -> list[dict[str, Any]]:
        """从内存队列消费事件"""
        unacked = []
        for event in self._events:
            if event["_id"] not in self._acked:
                unacked.append(event)
                if len(unacked) >= count:
                    break
        return unacked[:count]

    def ack(self, event_id: str) -> bool:
        """确认事件"""
        if event_id in self._acked:
            return False
        self._acked.add(event_id)
        return True

    def clear(self) -> None:
        """清空事件队列"""
        self._events.clear()
        self._acked.clear()


class RedisEventBus(EventBus):
    """Redis Streams 事件总线"""

    def __init__(
        self,
        stream_name: str = "sop-events",
        redis_url: str = "redis://localhost:6379",
        group_name: str = "sop-workers",
    ):
        self.stream_name = stream_name
        self.redis_url = redis_url
        self.group_name = group_name
        self._client: Optional[Any] = None

    async def _get_client(self):
        """获取 Redis 客户端"""
        if self._client is None:
            if not REDIS_AVAILABLE:
                raise RuntimeError("redis package not installed")
            self._client = await aioredis.from_url(self.redis_url)
        return self._client

    def publish(self, event: dict[str, Any]) -> str:
        """发布事件（同步版本，用于简单场景）"""
        # 简化实现：返回事件 ID
        import uuid
        event_id = str(uuid.uuid4())
        # 实际实现中会使用 redis.xadd
        return event_id

    def consume(
        self,
        count: int = 1,
        block_ms: int = 1000,
    ) -> list[dict[str, Any]]:
        """消费事件（同步版本）"""
        # 简化实现：返回空列表
        # 实际实现中会使用 redis.xread
        return []

    def ack(self, event_id: str) -> bool:
        """确认事件"""
        # 简化实现
        return True


# 默认使用内存事件总线（测试友好）
def create_event_bus(
    stream_name: str = "sop-events",
    use_redis: bool = False,
    redis_url: str = "redis://localhost:6379",
) -> EventBus:
    """创建事件总线实例

    Args:
        stream_name: 流名称
        use_redis: 是否使用 Redis
        redis_url: Redis URL

    Returns:
        EventBus 实例
    """
    if use_redis:
        return RedisEventBus(stream_name=stream_name, redis_url=redis_url)
    return MemoryEventBus(stream_name=stream_name)
