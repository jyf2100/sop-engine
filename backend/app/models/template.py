"""流程模板模型。

REQ-0001-002: 数据库模型定义
"""
from datetime import datetime

from .base import Base


class Template(Base):
    """流程模板模型

    存储解析后的 YAML 流程定义。
    """

    id: str
    name: str
    version: str
    yaml_content: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
