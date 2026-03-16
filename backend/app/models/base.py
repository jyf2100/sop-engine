"""基础模型类。"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class Base(BaseModel):
    """所有 Pydantic 模型的基类"""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        validate_assignment=True,
        extra="forbid",
    )


class TimestampMixin(BaseModel):
    """时间戳混入类"""

    created_at: datetime | None = None
    updated_at: datetime | None = None
