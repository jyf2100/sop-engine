"""Commands 配置模型。

控制 OpenClaw 的命令处理，包括：
- 原生命令
- 文本命令
- Bash 命令

对应 OpenClaw: commands.*

参考:
- /Users/roc/workspace/openclaw/docs/concepts/commands.md
"""
from typing import Any

from pydantic import Field

from .base import Base


# ==================== 原生命令配置 ====================


class NativeCommandsConfig(Base):
    """原生命令配置

    对应 OpenClaw: commands.native

    原生命令是 OpenClaw 内置的斜杠命令。
    常见命令：/new, /reset, /status, /help 等
    """
    enabled: bool = True
    use_access_groups: bool = True  # 是否使用访问组控制

    def to_openclaw(self) -> dict:
        result: dict[str, Any] = {"enabled": self.enabled}
        if self.use_access_groups:
            result["useAccessGroups"] = self.use_access_groups
        return result

    @classmethod
    def from_openclaw(cls, data: dict) -> "NativeCommandsConfig":
        return cls(
            enabled=data.get("enabled", True),
            use_access_groups=data.get("useAccessGroups", True),
        )


# ==================== 文本命令配置 ====================


class TextCommandsConfig(Base):
    """文本命令配置

    对应 OpenClaw: commands.text

    文本命令是非斜杠的自定义命令。

    Examples:
        {"prefix": "!", "enabled": true}  # !weather, !joke
        {"prefix": "~", "enabled": true}  # ~weather, ~joke
    """
    prefix: str = "!"
    enabled: bool = True
    allow_from: list[str] = Field(default_factory=list)  # 用户白名单

    def to_openclaw(self) -> dict:
        result: dict[str, Any] = {
            "prefix": self.prefix,
            "enabled": self.enabled,
        }
        if self.allow_from:
            result["allowFrom"] = self.allow_from
        return result

    @classmethod
    def from_openclaw(cls, data: dict) -> "TextCommandsConfig":
        return cls(
            prefix=data.get("prefix", "!"),
            enabled=data.get("enabled", True),
            allow_from=data.get("allowFrom", []),
        )


# ==================== Bash 命令配置 ====================


class BashCommandsConfig(Base):
    """Bash 命令配置

    对应 OpenClaw: commands.bash

    控制通过 !bash 执行 shell 命令。

    安全注意事项：
    - 建议使用 safe_bins 限制可用命令
    - 在生产环境考虑禁用或使用沙箱
    """
    enabled: bool = False
    timeout_seconds: int = Field(default=30, ge=1, description="命令超时秒数")
    safe_bins: list[str] = Field(default_factory=lambda: ["ls", "cat", "echo", "pwd"])
    allow_from: list[str] = Field(default_factory=list)  # 用户白名单
    use_access_groups: bool = True

    def to_openclaw(self) -> dict:
        result: dict[str, Any] = {
            "enabled": self.enabled,
            "timeoutSeconds": self.timeout_seconds,
        }
        if self.safe_bins:
            result["safeBins"] = self.safe_bins
        if self.allow_from:
            result["allowFrom"] = self.allow_from
        if self.use_access_groups:
            result["useAccessGroups"] = self.use_access_groups
        return result

    @classmethod
    def from_openclaw(cls, data: dict) -> "BashCommandsConfig":
        return cls(
            enabled=data.get("enabled", False),
            timeout_seconds=data.get("timeoutSeconds", 30),
            safe_bins=data.get("safeBins", ["ls", "cat", "echo", "pwd"]),
            allow_from=data.get("allowFrom", []),
            use_access_groups=data.get("useAccessGroups", True),
        )


# ==================== 调试命令配置 ====================


class DebugCommandsConfig(Base):
    """调试命令配置

    对应 OpenClaw: commands.debug

    控制调试命令如 /dump, /tool, /memory 等。
    """
    enabled: bool = False
    allow_from: list[str] = Field(default_factory=list)  # 仅管理员

    def to_openclaw(self) -> dict:
        result: dict[str, Any] = {"enabled": self.enabled}
        if self.allow_from:
            result["allowFrom"] = self.allow_from
        return result

    @classmethod
    def from_openclaw(cls, data: dict) -> "DebugCommandsConfig":
        return cls(
            enabled=data.get("enabled", False),
            allow_from=data.get("allowFrom", []),
        )


# ==================== 配置命令配置 ====================


class ConfigCommandsConfig(Base):
    """配置命令配置

    对应 OpenClaw: commands.config

    控制配置管理命令如 /config get, /config set 等。
    """
    enabled: bool = False
    allow_from: list[str] = Field(default_factory=list)  # 仅管理员

    def to_openclaw(self) -> dict:
        result: dict[str, Any] = {"enabled": self.enabled}
        if self.allow_from:
            result["allowFrom"] = self.allow_from
        return result

    @classmethod
    def from_openclaw(cls, data: dict) -> "ConfigCommandsConfig":
        return cls(
            enabled=data.get("enabled", False),
            allow_from=data.get("allowFrom", []),
        )


# ==================== 主配置模型 ====================


class CommandsConfig(Base):
    """Commands 配置模型

    对应 OpenClaw: commands.*

    完整的命令处理配置。
    """

    # === 原生命令 ===
    native: NativeCommandsConfig = Field(default_factory=NativeCommandsConfig)

    # === 文本命令 ===
    text: TextCommandsConfig = Field(default_factory=TextCommandsConfig)

    # === Bash 命令 ===
    bash: BashCommandsConfig = Field(default_factory=BashCommandsConfig)

    # === 调试命令 ===
    debug: DebugCommandsConfig | None = None

    # === 配置命令 ===
    config: ConfigCommandsConfig | None = None

    def to_openclaw(self) -> dict:
        """转换为 OpenClaw 配置格式（camelCase）"""
        result: dict[str, Any] = {}

        # 原生命令
        result["native"] = self.native.to_openclaw()

        # 文本命令
        result["text"] = self.text.to_openclaw()

        # Bash 命令
        result["bash"] = self.bash.to_openclaw()

        # 调试命令
        if self.debug:
            result["debug"] = self.debug.to_openclaw()

        # 配置命令
        if self.config:
            result["config"] = self.config.to_openclaw()

        return result

    @classmethod
    def from_openclaw(cls, data: dict) -> "CommandsConfig":
        """从 OpenClaw 配置格式解析"""
        native = NativeCommandsConfig.from_openclaw(data.get("native", {}))
        text = TextCommandsConfig.from_openclaw(data.get("text", {}))
        bash = BashCommandsConfig.from_openclaw(data.get("bash", {}))

        debug = None
        if "debug" in data:
            debug = DebugCommandsConfig.from_openclaw(data["debug"])

        config = None
        if "config" in data:
            config = ConfigCommandsConfig.from_openclaw(data["config"])

        return cls(
            native=native,
            text=text,
            bash=bash,
            debug=debug,
            config=config,
        )
