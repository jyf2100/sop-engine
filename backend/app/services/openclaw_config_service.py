"""OpenClaw 主配置管理服务。

REQ-0001-004: OpenClaw 主配置管理

管理 openclaw.json 的读写、验证和热重载通知。
SOP Engine 是 OpenClaw 配置的唯一来源（Source of Truth）。
"""
import json
import shutil
from pathlib import Path
from typing import Any

import httpx

from app.config import settings


class ConfigValidationError(ValueError):
    """配置验证失败异常"""

    pass


class OpenClawConfigService:
    """OpenClaw 主配置管理服务

    负责 openclaw.json 的 CRUD 操作、配置验证和热重载通知。
    """

    def __init__(
        self,
        config_path: Path | str,
        reload_webhook_url: str | None = None,
    ):
        if isinstance(config_path, str):
            config_path = Path(config_path)

        self.config_path = config_path
        self.reload_webhook_url = reload_webhook_url
        self._config: dict[str, Any] | None = None

    def load_config(self) -> dict[str, Any]:
        """加载 openclaw.json

        Returns:
            配置字典

        Raises:
            FileNotFoundError: 配置文件不存在
            json.JSONDecodeError: JSON 格式错误
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")

        content = self.config_path.read_text()
        self._config = json.loads(content)
        return self._config

    def save_config(self, config: dict[str, Any]) -> None:
        """保存配置到 openclaw.json

        Args:
            config: 配置字典

        Raises:
            ConfigValidationError: 配置验证失败
        """
        # 验证配置
        self._validate_config(config)

        # 原子写入：先写临时文件，再重命名
        temp_path = self.config_path.with_suffix(".tmp")
        try:
            temp_path.write_text(json.dumps(config, indent=2, ensure_ascii=False))
            shutil.move(str(temp_path), str(self.config_path))
        except Exception:
            if temp_path.exists():
                temp_path.unlink()
            raise

        self._config = config

    def update_config(self, updates: dict[str, Any]) -> dict[str, Any]:
        """更新配置

        Args:
            updates: 要更新的配置项

        Returns:
            更新后的完整配置

        Raises:
            ConfigValidationError: 配置验证失败
        """
        config = self.load_config()

        # 深度合并
        def deep_merge(base: dict, updates: dict) -> dict:
            result = base.copy()
            for key, value in updates.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        merged = deep_merge(config, updates)
        self.save_config(merged)

        # 发送重载通知
        self._notify_reload()

        return merged

    def update_agents_list(self, agents: list[dict[str, Any]]) -> dict[str, Any]:
        """更新 agents.list

        Args:
            agents: Agent 列表

        Returns:
            更新后的完整配置
        """
        return self.update_config({"agents": {"list": agents}})

    def update_bindings(self, bindings: list[dict[str, Any]]) -> dict[str, Any]:
        """更新 bindings

        Args:
            bindings: 绑定列表

        Returns:
            更新后的完整配置
        """
        return self.update_config({"bindings": bindings})

    def update_global_settings(self, settings: dict[str, Any]) -> dict[str, Any]:
        """更新全局设置

        Args:
            settings: 全局设置（如 logging, env 等）

        Returns:
            更新后的完整配置
        """
        return self.update_config(settings)

    def get_agents_list(self) -> list[dict[str, Any]]:
        """获取 agents.list

        Returns:
            Agent 列表
        """
        config = self.load_config()
        return config.get("agents", {}).get("list", [])

    # Alias for backward compatibility
    get_agent_list = get_agents_list

    def add_agent(self, agent_config: dict[str, Any]) -> dict[str, Any]:
        """添加 Agent 到 agents.list

        Args:
            agent_config: Agent 配置字典

        Returns:
            更新后的完整配置
        """
        config = self.load_config()
        agents_list = config.get("agents", {}).get("list", [])

        # 检查 ID 是否已存在
        agent_id = agent_config.get("id")
        if any(a.get("id") == agent_id for a in agents_list):
            raise ValueError(f"Agent '{agent_id}' already exists")

        agents_list.append(agent_config)
        return self.update_agents_list(agents_list)

    def remove_agent(self, agent_id: str) -> dict[str, Any]:
        """从 agents.list 移除 Agent

        Args:
            agent_id: Agent ID

        Returns:
            更新后的完整配置
        """
        config = self.load_config()
        agents_list = config.get("agents", {}).get("list", [])

        # 过滤掉要删除的 agent
        new_list = [a for a in agents_list if a.get("id") != agent_id]

        if len(new_list) == len(agents_list):
            raise KeyError(f"Agent '{agent_id}' not found")

        return self.update_agents_list(new_list)

    def add_binding(self, binding_config: dict[str, Any]) -> dict[str, Any]:
        """添加绑定

        Args:
            binding_config: 绑定配置字典

        Returns:
            更新后的完整配置
        """
        config = self.load_config()
        bindings = config.get("bindings", [])
        bindings.append(binding_config)
        return self.update_bindings(bindings)

    def remove_binding(self, binding_id: dict[str, Any]) -> dict[str, Any]:
        """移除绑定

        Args:
            binding_id: 绑定标识（用于匹配的字段）

        Returns:
            更新后的完整配置
        """
        config = self.load_config()
        bindings = config.get("bindings", [])

        # 过滤匹配的绑定
        new_bindings = [
            b for b in bindings
            if not all(b.get(k) == v for k, v in binding_id.items())
        ]

        return self.update_bindings(new_bindings)

    def get_bindings(self) -> list[dict[str, Any]]:
        """获取 bindings

        Returns:
            绑定列表
        """
        config = self.load_config()
        return config.get("bindings", [])

    def validate_config(self, config: dict[str, Any]) -> bool:
        """验证配置结构（公共方法）

        Args:
            config: 配置字典

        Returns:
            True 如果配置有效

        Raises:
            ConfigValidationError: 配置验证失败
        """
        self._validate_config(config)
        return True

    def _validate_config(self, config: dict[str, Any]) -> None:
        """验证配置结构

        Args:
            config: 配置字典

        Raises:
            ConfigValidationError: 配置验证失败
        """
        # 基本结构验证
        if not isinstance(config, dict):
            raise ConfigValidationError("Config must be a dictionary")

        # agents 字段必须存在
        if "agents" not in config:
            raise ConfigValidationError("agents field is required")

        # agents 结构验证
        agents = config["agents"]
        if not isinstance(agents, dict):
            raise ConfigValidationError("agents must be a dictionary")

        if "list" in agents and not isinstance(agents["list"], list):
            raise ConfigValidationError("agents.list must be an array")

        # bindings 结构验证
        if "bindings" in config and not isinstance(config["bindings"], list):
            raise ConfigValidationError("bindings must be an array")

        # Agent ID 验证
        agents_list = config.get("agents", {}).get("list", [])
        for agent in agents_list:
            agent_id = agent.get("id")
            if not agent_id or (isinstance(agent_id, str) and not agent_id.strip()):
                raise ConfigValidationError("agent id cannot be empty")

        # Agent ID 唯一性验证
        agent_ids = [a.get("id") for a in agents_list if a.get("id")]
        if len(agent_ids) != len(set(agent_ids)):
            raise ConfigValidationError("Duplicate agent IDs found")

    def _notify_reload(self) -> None:
        """发送配置重载通知"""
        if not self.reload_webhook_url:
            return

        try:
            with httpx.Client(timeout=5.0) as client:
                client.post(
                    self.reload_webhook_url,
                    json={"action": "reload", "source": "sop-engine"},
                    headers={"Content-Type": "application/json"},
                )
        except httpx.HTTPError:
            # 记录日志但不阻塞保存操作
            pass  # TODO: 使用 structlog 记录警告
