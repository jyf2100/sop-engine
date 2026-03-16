"""模板管理服务。

REQ-0001-016: REST API - 模板管理
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

import yaml

from app.models.template import Template


@dataclass
class TemplateService:
    """模板管理服务

    提供模板的 CRUD 操作。
    """

    _templates: dict[str, Template] = field(default_factory=dict)

    def create_template(
        self,
        name: str,
        yaml_content: str,
        version: str = "1.0",
        description: Optional[str] = None,
    ) -> Template:
        """创建模板

        Args:
            name: 模板名称
            yaml_content: YAML 内容
            version: 版本号
            description: 描述（暂不使用）

        Returns:
            创建的模板实例

        Raises:
            ValueError: YAML 解析失败
        """
        # 基本验证 YAML 格式
        try:
            yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {e}")

        template_id = f"template-{uuid.uuid4().hex[:8]}"
        now = datetime.utcnow()

        template = Template(
            id=template_id,
            name=name,
            version=version,
            yaml_content=yaml_content,
            created_at=now,
            updated_at=now,
        )

        self._templates[template_id] = template
        return template

    def get_template(self, template_id: str) -> Template:
        """获取模板

        Args:
            template_id: 模板 ID

        Returns:
            模板实例

        Raises:
            KeyError: 模板不存在
        """
        if template_id not in self._templates:
            raise KeyError(f"Template '{template_id}' not found")
        return self._templates[template_id]

    def list_templates(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[list[Template], int]:
        """列出模板

        Args:
            skip: 跳过数量
            limit: 返回数量

        Returns:
            (模板列表, 总数)
        """
        all_templates = list(self._templates.values())
        total = len(all_templates)
        return all_templates[skip:skip + limit], total

    def delete_template(self, template_id: str) -> None:
        """删除模板

        Args:
            template_id: 模板 ID

        Raises:
            KeyError: 模板不存在
        """
        if template_id not in self._templates:
            raise KeyError(f"Template '{template_id}' not found")
        del self._templates[template_id]

    def upload_yaml(self, yaml_content: str) -> Template:
        """从 YAML 上传模板

        Args:
            yaml_content: YAML 内容

        Returns:
            创建的模板实例

        Raises:
            ValueError: YAML 解析失败
        """
        # 解析 YAML 获取 name 和 version
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML: {e}")

        if not isinstance(data, dict):
            raise ValueError("YAML must be a dictionary")

        name = data.get("name", "unnamed")
        version = str(data.get("version", "1.0"))

        return self.create_template(
            name=name,
            yaml_content=yaml_content,
            version=version,
        )
