"""模型配置管理服务。

REQ-0001-XXX: 模型配置管理

提供 ModelConfig 的 CRUD 操作。
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.models import PRESET_MODELS, ModelConfig


@dataclass
class ModelService:
    """模型配置管理服务

    负责模型配置的创建、更新、删除。
    支持预设模型和自定义模型。
    """

    _models: dict[str, ModelConfig] = field(default_factory=dict)

    def __post_init__(self):
        """初始化预设模型"""
        for preset in PRESET_MODELS:
            model = ModelConfig(
                id=preset["id"],
                name=preset["name"],
                type=preset["type"],
                provider=preset["provider"],
                model_id=preset["model_id"],
                base_url=preset["base_url"],
                api_key="",  # 预设模型需要用户配置 API Key
                default_params=preset.get("default_params", {}),
                dimensions=preset.get("dimensions"),
                default_size=preset.get("default_size"),
                is_default=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            self._models[preset["id"]] = model

    def list_models(self, model_type: str | None = None) -> list[ModelConfig]:
        """列出模型配置

        Args:
            model_type: 可选的模型类型过滤 (llm | embedding | image)

        Returns:
            模型配置列表
        """
        models = list(self._models.values())
        if model_type:
            models = [m for m in models if m.type == model_type]
        # 默认模型排前面
        return sorted(models, key=lambda m: (not m.is_default, m.name))

    def get_model(self, model_id: str) -> ModelConfig:
        """获取模型配置

        Args:
            model_id: 模型唯一标识

        Returns:
            模型配置

        Raises:
            KeyError: 模型不存在
        """
        if model_id not in self._models:
            raise KeyError(f"Model '{model_id}' not found")
        return self._models[model_id]

    def create_model(
        self,
        model_id: str,
        name: str,
        model_type: str,
        provider: str,
        model_id_str: str,
        base_url: str,
        api_key: str,
        default_params: dict[str, Any] | None = None,
        dimensions: int | None = None,
        default_size: str | None = None,
        is_default: bool = False,
    ) -> ModelConfig:
        """创建模型配置

        Args:
            model_id: 模型唯一标识
            name: 显示名称
            model_type: 模型类型 (llm | embedding | image)
            provider: 提供商
            model_id_str: 模型 ID
            base_url: API 端点
            api_key: API 密钥
            default_params: 默认参数
            dimensions: 向量维度 (embedding 专用)
            default_size: 默认尺寸 (image 专用)
            is_default: 是否为默认模型

        Returns:
            创建的模型配置
        """
        if model_id in self._models:
            raise ValueError(f"Model '{model_id}' already exists")

        # 如果设置为默认，先清除同类型的其他默认
        if is_default:
            for m in self._models.values():
                if m.type == model_type and m.is_default:
                    m.is_default = False

        model = ModelConfig(
            id=model_id,
            name=name,
            type=model_type,
            provider=provider,
            model_id=model_id_str,
            base_url=base_url,
            api_key=api_key,
            default_params=default_params or {},
            dimensions=dimensions,
            default_size=default_size,
            is_default=is_default,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self._models[model_id] = model
        return model

    def update_model(
        self,
        model_id: str,
        name: str | None = None,
        provider: str | None = None,
        model_id_str: str | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        default_params: dict[str, Any] | None = None,
        dimensions: int | None = None,
        default_size: str | None = None,
        is_default: bool | None = None,
    ) -> ModelConfig:
        """更新模型配置

        Args:
            model_id: 模型唯一标识
            name: 显示名称
            provider: 提供商
            model_id_str: 模型 ID
            base_url: API 端点
            api_key: API 密钥
            default_params: 默认参数
            dimensions: 向量维度
            default_size: 默认尺寸
            is_default: 是否为默认模型

        Returns:
            更新后的模型配置
        """
        model = self.get_model(model_id)

        # 如果设置为默认，先清除同类型的其他默认
        if is_default:
            for m in self._models.values():
                if m.type == model.type and m.is_default and m.id != model_id:
                    m.is_default = False

        updated = ModelConfig(
            id=model.id,
            name=name if name is not None else model.name,
            type=model.type,
            provider=provider if provider is not None else model.provider,
            model_id=model_id_str if model_id_str is not None else model.model_id,
            base_url=base_url if base_url is not None else model.base_url,
            api_key=api_key if api_key is not None else model.api_key,
            default_params=default_params if default_params is not None else model.default_params,
            dimensions=dimensions if dimensions is not None else model.dimensions,
            default_size=default_size if default_size is not None else model.default_size,
            is_default=is_default if is_default is not None else model.is_default,
            created_at=model.created_at,
            updated_at=datetime.utcnow(),
        )

        self._models[model_id] = updated
        return updated

    def delete_model(self, model_id: str) -> None:
        """删除模型配置

        Args:
            model_id: 模型唯一标识

        Raises:
            KeyError: 模型不存在
        """
        if model_id not in self._models:
            raise KeyError(f"Model '{model_id}' not found")

        del self._models[model_id]

    def get_default_model(self, model_type: str) -> ModelConfig | None:
        """获取指定类型的默认模型

        Args:
            model_type: 模型类型

        Returns:
            默认模型配置，如果没有则返回 None
        """
        for model in self._models.values():
            if model.type == model_type and model.is_default:
                return model
        return None
