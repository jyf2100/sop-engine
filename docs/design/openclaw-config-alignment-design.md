# SOP Engine 与 OpenClaw 配置对齐详细设计

## 文档信息

| 项目 | 值 |
|------|-----|
| 版本 | v1.0 |
| 日期 | 2026-03-18 |
| 状态 | Design Complete - Ready for Implementation |
| 作者 | Claude |

---

## 详细设计文档索引

| 模块 | 文档 | 状态 |
|------|------|------|
| Session 配置 | [session-config-detailed-design.md](./session-config-detailed-design.md) | ✅ 完成 |
| Messages/Commands/Bindings | [messages-commands-bindings-detailed-design.md](./messages-commands-bindings-detailed-design.md) | ✅ 完成 |
| Channel 配置 | 本文档 Section 2-5 | ✅ 完成 |
| Agent 配置 | 本文档 Section 6-9 | ✅ 完成 |
| Tools 完整配置 | 本文档 Section 10.2.2 | 📋 待实现 |
| TTS 配置 | 本文档 Section 10.5 | 📋 待实现 |
| 流式与延迟配置 | 本文档 Section 10.3.3 | 📋 待实现 |

---

## 1. 概述

### 1.1 背景

SOP Engine 作为 OpenClaw Agent 和 Channel 配置的唯一来源（Source of Truth），需要与 OpenClaw 官方配置规范完全对齐。当前实现对部分配置字段支持不完整，且同步逻辑存在覆盖问题。

### 1.2 目标

1. **完整性**：支持 OpenClaw 配置规范的所有核心字段
2. **兼容性**：同步时采用 merge 策略，不覆盖非管理字段
3. **可扩展性**：支持多账号配置，便于未来扩展
4. **易用性**：前端 UI 覆盖常用配置，高级配置可选

### 1.3 范围

- Channel 配置：Telegram, WhatsApp, Feishu, Discord, Slack
- Agent 配置：Model, Sandbox, Tools, Heartbeat, Identity 等

---

## 2. 数据模型设计

### 2.1 Channel 模型

#### 2.1.1 完整字段定义

```python
# backend/app/models/channel.py

from datetime import datetime
from typing import Any, Literal
from pydantic import Field
from .base import Base

# ==================== 类型定义 ====================

ChannelType = Literal["telegram", "whatsapp", "feishu", "discord", "slack"]
DmPolicy = Literal["pairing", "allowlist", "open", "disabled"]
GroupPolicy = Literal["open", "allowlist", "disabled"]
StreamingMode = Literal["off", "partial", "block"]
ConnectionMode = Literal["websocket", "webhook"]
FeishuDomain = Literal["feishu", "lark"]

# ==================== 子模型 ====================

class GroupConfig(Base):
    """群组配置"""
    enabled: bool = True
    require_mention: bool = True
    allow_from: list[str] = []  # 群组内发送者白名单

class TelegramAccount(Base):
    """Telegram 账号配置"""
    name: str | None = None
    enabled: bool = True
    bot_token: str | None = None

class FeishuAccount(Base):
    """飞书账号配置"""
    name: str | None = None
    enabled: bool = True
    app_id: str | None = None
    app_secret: str | None = None
    domain: FeishuDomain = "feishu"
    bot_name: str | None = None

class WhatsAppAccount(Base):
    """WhatsApp 账号配置"""
    name: str | None = None
    enabled: bool = True
    phone_id: str | None = None

# ==================== 主模型 ====================

class ChannelConfig(Base):
    """Channel 配置模型

    对应 OpenClaw 配置: channels.<type>
    支持多账号结构: channels.<type>.accounts
    """

    # === 基础标识 ===
    id: str  # SOP Engine 内部 ID，如 "telegram-main"
    name: str  # 显示名称，如 "客服机器人"
    type: ChannelType  # 平台类型
    enabled: bool = True

    # === 多账号支持 ===
    accounts: dict[str, TelegramAccount | FeishuAccount | WhatsAppAccount] | None = None
    default_account: str = "default"

    # === DM 策略（通用） ===
    dm_policy: DmPolicy = "pairing"
    allow_from: list[str] = []  # DM 白名单

    # === 群组策略（通用） ===
    group_policy: GroupPolicy = "open"
    group_allow_from: list[str] = []  # 群组白名单
    groups: dict[str, GroupConfig] = {}  # 按群组 ID 配置

    # === 流式输出（通用） ===
    streaming: StreamingMode = "partial"
    block_streaming: bool = True

    # === 消息限制（通用） ===
    text_chunk_limit: int = Field(default=2000, description="文本分块大小")
    media_max_mb: int = Field(default=100, description="媒体文件最大 MB")
    history_limit: int = Field(default=50, description="历史消息限制")
    dm_history_limit: int | None = None  # DM 历史限制（可覆盖 history_limit）

    # === 安全配置（通用） ===
    config_writes: bool = True  # 是否允许通过聊天修改配置

    # ==================== Telegram 特定字段 ====================

    bot_token: str | None = None  # 主账号 Bot Token（向后兼容）
    reaction_notifications: Literal["off", "own", "all", "allowlist"] = "own"
    reaction_allowlist: list[str] = []
    custom_commands: dict[str, Any] | None = None
    dms: dict[str, Any] = {}  # 按 DM ID 的特定配置

    # ==================== Feishu 特定字段 ====================

    domain: FeishuDomain = "feishu"  # API 域名（feishu 国内 / lark 国际）
    connection_mode: ConnectionMode = "websocket"  # 连接模式

    # 凭证（主账号，向后兼容）
    app_id: str | None = None
    app_secret: str | None = None
    encrypt_key: str | None = None  # Webhook 模式必需
    verification_token: str | None = None  # Webhook 模式必需

    # 行为配置
    bot_name: str | None = None
    typing_indicator: bool = True  # 是否显示输入提示
    resolve_sender_names: bool = True  # 是否解析发送者名称

    # Webhook 配置（connection_mode = "webhook" 时使用）
    webhook_path: str = "/feishu/events"
    webhook_host: str = "127.0.0.1"
    webhook_port: int = 3000

    # ==================== WhatsApp 特定字段 ====================

    phone_id: str | None = None  # 主账号 Phone ID（向后兼容）

    # ==================== Discord 特定字段 ====================
    # （待补充）

    # ==================== Slack 特定字段 ====================
    # （待补充）

    # ==================== 元数据 ====================

    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        # 允许额外字段，便于未来扩展
        extra = "allow"
```

#### 2.1.2 字段分组说明

| 分组 | 字段 | OpenClaw 路径 | 必填 |
|------|------|--------------|------|
| **基础** | id, name, type, enabled | channels.{type}.* | Y |
| **多账号** | accounts, default_account | channels.{type}.accounts | N |
| **DM** | dm_policy, allow_from | dmPolicy, allowFrom | N |
| **群组** | group_policy, group_allow_from, groups | groupPolicy, groupAllowFrom, groups | N |
| **流式** | streaming, block_streaming | streaming, blockStreaming | N |
| **限制** | text_chunk_limit, media_max_mb, history_limit | textChunkLimit, mediaMaxMb, historyLimit | N |

### 2.2 Agent 模型

#### 2.2.1 完整字段定义

```python
# backend/app/models/agent.py

from datetime import datetime
from typing import Any, Literal
from pydantic import Field
from .base import Base

# ==================== 类型定义 ====================

SandboxMode = Literal["off", "non-main", "all"]
SandboxBackend = Literal["docker", "ssh", "openshell"]
SandboxScope = Literal["session", "agent", "shared"]
WorkspaceAccess = Literal["none", "ro", "rw"]
ThinkingLevel = Literal["off", "low", "medium", "high", "adaptive"]

# ==================== 模型配置子模型 ====================

class ModelReference(Base):
    """模型引用"""
    primary: str  # 格式: provider/model
    fallbacks: list[str] = []

class ModelCatalogEntry(Base):
    """模型目录条目"""
    alias: str | None = None  # 简短别名，如 "opus"
    params: dict[str, Any] = {}  # 模型参数，如 temperature, maxTokens

class AgentModelConfig(Base):
    """Agent 模型配置

    对应 OpenClaw: agents.defaults.model / agents.list[].model
    """
    # 模型目录（定义可用模型及其别名）
    models: dict[str, ModelCatalogEntry] = {}

    # 主模型
    model: ModelReference | None = None

    # 专用模型
    image_model: ModelReference | None = None  # 视觉模型
    image_generation_model: ModelReference | None = None  # 图像生成
    pdf_model: ModelReference | None = None  # PDF 处理

    # 模型行为
    thinking_default: ThinkingLevel = "low"
    verbose_default: Literal["off", "on"] = "off"
    elevated_default: Literal["off", "on"] = "on"

    # 超时和限制
    timeout_seconds: int = 600
    media_max_mb: int = 5
    context_tokens: int = 200000
    max_concurrent: int = 1

    # PDF 配置
    pdf_max_bytes_mb: int = 10
    pdf_max_pages: int = 20

# ==================== 沙箱配置子模型 ====================

class DockerSandboxConfig(Base):
    """Docker 沙箱配置"""
    image: str = "openclaw-sandbox:bookworm-slim"
    container_prefix: str = "openclaw-sbx-"
    workdir: str = "/workspace"
    read_only_root: bool = True
    tmpfs: list[str] = ["/tmp", "/var/tmp", "/run"]
    network: str = "none"
    user: str = "1000:1000"
    cap_drop: list[str] = ["ALL"]
    env: dict[str, str] = {}
    setup_command: str | None = None
    pids_limit: int = 256
    memory: str = "1g"
    memory_swap: str = "2g"
    cpus: float = 1.0
    dns: list[str] = []
    extra_hosts: list[str] = []
    binds: list[str] = []

class SshSandboxConfig(Base):
    """SSH 沙箱配置"""
    target: str  # user@host[:port]
    command: str = "ssh"
    workspace_root: str = "/tmp/openclaw-sandboxes"
    identity_file: str | None = None
    certificate_file: str | None = None
    known_hosts_file: str | None = None
    strict_host_key_checking: bool = True

class BrowserSandboxConfig(Base):
    """浏览器沙箱配置"""
    enabled: bool = False
    image: str = "openclaw-sandbox-browser:bookworm-slim"
    network: str = "openclaw-sandbox-browser"
    cdp_port: int = 9222
    vnc_port: int = 5900
    no_vnc_port: int = 6080
    headless: bool = True
    enable_no_vnc: bool = True

class SandboxConfig(Base):
    """沙箱配置

    对应 OpenClaw: agents.defaults.sandbox / agents.list[].sandbox
    """
    mode: SandboxMode = "non-main"
    backend: SandboxBackend = "docker"
    scope: SandboxScope = "agent"
    workspace_access: WorkspaceAccess = "none"
    workspace_root: str = "~/.openclaw/sandboxes"

    docker: DockerSandboxConfig | None = None
    ssh: SshSandboxConfig | None = None
    browser: BrowserSandboxConfig | None = None

# ==================== 工具配置子模型 ====================

class ElevatedToolsConfig(Base):
    """提升权限工具配置"""
    enabled: bool = True
    allow_from: dict[str, list[str]] = {}  # channel -> user list

class ToolsConfig(Base):
    """工具配置

    对应 OpenClaw: agents.defaults.tools / agents.list[].tools
    """
    profile: str | None = None  # 预设配置，如 "coding"
    allow: list[str] = []
    deny: list[str] = []
    elevated: ElevatedToolsConfig | None = None
    exec: dict[str, Any] | None = None

# ==================== 心跳配置子模型 ====================

class HeartbeatConfig(Base):
    """心跳配置

    对应 OpenClaw: agents.defaults.heartbeat / agents.list[].heartbeat
    """
    every: str = "30m"  # 间隔时间
    model: str | None = None  # 心跳使用的模型
    include_reasoning: bool = False
    light_context: bool = False  # 轻量上下文（仅 HEARTBEAT.md）
    isolated_session: bool = False  # 隔离会话（无历史）
    session: str = "main"
    to: str | None = None  # 目标地址
    direct_policy: Literal["allow", "block"] = "allow"
    target: str = "none"  # last | whatsapp | telegram | ...
    prompt: str | None = None
    ack_max_chars: int = 300
    suppress_tool_error_warnings: bool = False

# ==================== Compaction 配置子模型 ====================

class MemoryFlushConfig(Base):
    """内存刷新配置"""
    enabled: bool = True
    soft_threshold_tokens: int = 6000
    system_prompt: str | None = None
    prompt: str | None = None

class CompactionConfig(Base):
    """压缩配置

    对应 OpenClaw: agents.defaults.compaction
    """
    mode: Literal["default", "safeguard"] = "safeguard"
    timeout_seconds: int = 900
    reserve_tokens_floor: int = 24000
    identifier_policy: Literal["strict", "off", "custom"] = "strict"
    identifier_instructions: str | None = None
    post_compaction_sections: list[str] = ["Session Startup", "Red Lines"]
    model: str | None = None
    memory_flush: MemoryFlushConfig | None = None

# ==================== 身份配置子模型 ====================

class IdentityConfig(Base):
    """身份配置

    对应 OpenClaw: agents.list[].identity
    """
    name: str | None = None
    emoji: str = "🤖"
    avatar: str | None = None  # 路径、URL 或 data URI
    theme: str | None = None
    ack_reaction: str | None = None  # 确认反应 emoji

# ==================== 群聊配置子模型 ====================

class GroupChatConfig(Base):
    """群聊配置

    对应 OpenClaw: agents.list[].groupChat
    """
    mention_patterns: list[str] = []  # 触发模式，如 ["@bot", "bot"]

# ==================== 运行时配置子模型 ====================

class AcpRuntimeConfig(Base):
    """ACP 运行时配置"""
    agent: str | None = None
    backend: str = "acpx"
    mode: Literal["persistent", "ephemeral"] = "persistent"
    cwd: str | None = None

class RuntimeConfig(Base):
    """运行时配置"""
    type: Literal["acp"] = "acp"
    acp: AcpRuntimeConfig | None = None

# ==================== 人类延迟配置子模型 ====================

class HumanDelayConfig(Base):
    """人类延迟配置"""
    mode: Literal["off", "natural", "custom"] = "natural"
    min_ms: int | None = None  # custom 模式
    max_ms: int | None = None  # custom 模式

# ==================== 主模型 ====================

class Agent(Base):
    """Agent 配置模型

    对应 OpenClaw: agents.list[]
    SOP Engine 是 Agent 配置的唯一来源（Source of Truth）
    """

    # === 基础标识 ===
    id: str
    name: str
    workspace_path: str
    agent_dir: str | None = None  # Agent 配置目录

    # === 模型配置 ===
    llm_config: AgentModelConfig | None = None

    # === 沙箱配置 ===
    sandbox_config: SandboxConfig | None = None

    # === 工具配置 ===
    tools_config: ToolsConfig | None = None

    # === 心跳配置 ===
    heartbeat_config: HeartbeatConfig | None = None

    # === Compaction 配置 ===
    compaction_config: CompactionConfig | None = None

    # === 记忆搜索配置 ===
    memory_search_config: dict[str, Any] | None = None

    # === 群聊配置 ===
    group_chat_config: GroupChatConfig | None = None

    # === 身份配置 ===
    identity: IdentityConfig | None = None

    # === 运行时配置 ===
    runtime_config: RuntimeConfig | None = None

    # === 人类延迟 ===
    human_delay: HumanDelayConfig | None = None

    # === 子 Agent 配置 ===
    subagents_config: dict[str, Any] | None = None  # allowAgents

    # === 模型参数覆盖 ===
    params: dict[str, Any] = {}

    # === 元数据 ===
    is_default: bool = False
    is_active: bool = True
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        extra = "allow"
```

---

## 3. 同步逻辑设计

### 3.1 设计原则

1. **Merge 策略**：只更新 SOP Engine 管理的字段，保留其他字段
2. **字段标记**：明确定义哪些字段由 SOP Engine 管理
3. **备份机制**：每次修改前自动备份
4. **错误恢复**：同步失败时可从备份恢复

### 3.2 Channel 同步逻辑

```python
# backend/app/services/channel_service.py

class ChannelService:
    # SOP Engine 管理的字段（按平台类型）
    MANAGED_FIELDS_COMMON = {
        "enabled", "dmPolicy", "allowFrom", "groupPolicy",
        "groupAllowFrom", "groups", "streaming", "blockStreaming",
        "textChunkLimit", "mediaMaxMb", "historyLimit", "configWrites"
    }

    MANAGED_FIELDS_TELEGRAM = MANAGED_FIELDS_COMMON | {
        "botToken", "reactionNotifications", "reactionAllowlist",
        "customCommands", "dms", "dmHistoryLimit"
    }

    MANAGED_FIELDS_FEISHU = MANAGED_FIELDS_COMMON | {
        "appId", "appSecret", "encryptKey", "verificationToken",
        "domain", "connectionMode", "botName", "typingIndicator",
        "resolveSenderNames", "webhookPath", "webhookHost", "webhookPort",
        "accounts", "defaultAccount"
    }

    MANAGED_FIELDS_WHATSAPP = MANAGED_FIELDS_COMMON | {
        "phoneId", "accounts", "defaultAccount"
    }

    def _get_managed_fields(self, channel_type: str) -> set[str]:
        """获取指定平台类型的受管字段"""
        field_map = {
            "telegram": self.MANAGED_FIELDS_TELEGRAM,
            "feishu": self.MANAGED_FIELDS_FEISHU,
            "whatsapp": self.MANAGED_FIELDS_WHATSAPP,
            "discord": self.MANAGED_FIELDS_COMMON,
            "slack": self.MANAGED_FIELDS_COMMON,
        }
        return field_map.get(channel_type, self.MANAGED_FIELDS_COMMON)

    def _sync_to_openclaw(self) -> None:
        """同步 Channel 到 OpenClaw（merge 策略）"""
        self._backup_openclaw_config()
        config = self._read_openclaw_config()

        if "channels" not in config:
            config["channels"] = {}

        for channel in self._channels.values():
            channel_key = channel.type
            existing = config["channels"].get(channel_key, {})
            managed_fields = self._get_managed_fields(channel.type)

            # 构建 OpenClaw 格式配置
            new_config = self._channel_to_openclaw_format(channel)

            # Merge: 保留非管理字段，覆盖管理字段
            merged = {}
            for key, value in existing.items():
                if key not in managed_fields:
                    merged[key] = value
            merged.update(new_config)

            config["channels"][channel_key] = merged

        self._write_openclaw_config(config)

    def _channel_to_openclaw_format(self, channel: ChannelConfig) -> dict:
        """转换为 OpenClaw 格式（camelCase）"""
        result = {
            "enabled": channel.enabled,
            "dmPolicy": channel.dm_policy,
            "allowFrom": channel.allow_from,
            "groupPolicy": channel.group_policy,
            "groupAllowFrom": channel.group_allow_from,
            "groups": self._groups_to_openclaw(channel.groups),
            "streaming": channel.streaming,
            "textChunkLimit": channel.text_chunk_limit,
            "mediaMaxMb": channel.media_max_mb,
            "historyLimit": channel.history_limit,
            "configWrites": channel.config_writes,
        }

        # 多账号支持
        if channel.accounts:
            result["accounts"] = self._accounts_to_openclaw(channel)
            if channel.default_account:
                result["defaultAccount"] = channel.default_account

        # 平台特定字段
        if channel.type == "telegram":
            result.update({
                "botToken": channel.bot_token,
                "reactionNotifications": channel.reaction_notifications,
                "reactionAllowlist": channel.reaction_allowlist,
                "customCommands": channel.custom_commands,
                "dms": channel.dms,
            })
            if channel.dm_history_limit:
                result["dmHistoryLimit"] = channel.dm_history_limit

        elif channel.type == "feishu":
            result.update({
                "domain": channel.domain,
                "connectionMode": channel.connection_mode,
                "typingIndicator": channel.typing_indicator,
                "resolveSenderNames": channel.resolve_sender_names,
            })
            if channel.bot_name:
                result["botName"] = channel.bot_name
            if channel.connection_mode == "webhook":
                result.update({
                    "encryptKey": channel.encrypt_key,
                    "verificationToken": channel.verification_token,
                    "webhookPath": channel.webhook_path,
                    "webhookHost": channel.webhook_host,
                    "webhookPort": channel.webhook_port,
                })
            # 凭证（支持主账号或多账号）
            if not channel.accounts:
                result.update({
                    "appId": channel.app_id,
                    "appSecret": channel.app_secret,
                })

        elif channel.type == "whatsapp":
            if channel.phone_id:
                result["phoneId"] = channel.phone_id

        # 移除 None 值
        return {k: v for k, v in result.items() if v is not None}

    def _groups_to_openclaw(self, groups: dict) -> dict:
        """转换群组配置"""
        result = {}
        for chat_id, config in groups.items():
            entry = {
                "enabled": config.enabled,
                "requireMention": config.require_mention,
            }
            if config.allow_from:
                entry["allowFrom"] = config.allow_from
            result[chat_id] = entry
        return result

    def _accounts_to_openclaw(self, channel: ChannelConfig) -> dict:
        """转换多账号配置"""
        if not channel.accounts:
            return {}

        result = {}
        for account_id, account in channel.accounts.items():
            entry = {
                "name": account.name,
                "enabled": account.enabled,
            }
            if channel.type == "telegram" and hasattr(account, 'bot_token'):
                entry["botToken"] = account.bot_token
            elif channel.type == "feishu" and hasattr(account, 'app_id'):
                entry.update({
                    "appId": account.app_id,
                    "appSecret": account.app_secret,
                    "domain": account.domain,
                })
                if account.bot_name:
                    entry["botName"] = account.bot_name
            elif channel.type == "whatsapp" and hasattr(account, 'phone_id'):
                entry["phoneId"] = account.phone_id
            result[account_id] = entry
        return result
```

### 3.3 Agent 同步逻辑

```python
# backend/app/services/agent_service.py

class AgentService:
    # SOP Engine 管理的 Agent 字段
    MANAGED_AGENT_FIELDS = {
        "id", "workspace", "agentDir", "model", "sandbox", "tools",
        "heartbeat", "compaction", "identity", "groupChat", "runtime",
        "subagents", "params", "humanDelay"
    }

    def _register_to_openclaw(self, agent: Agent) -> None:
        """将 Agent 注册到 OpenClaw（merge 策略）"""
        self._backup_openclaw_config()
        config = self._read_openclaw_config()

        if "agents" not in config:
            config["agents"] = {}
        if "list" not in config["agents"]:
            config["agents"]["list"] = []

        # 构建完整 agent 条目
        agent_entry = self._agent_to_openclaw_format(agent)

        # 查找现有条目
        existing_idx = next(
            (i for i, a in enumerate(config["agents"]["list"])
             if a.get("id") == agent.id),
            None
        )

        if existing_idx is not None:
            # Merge: 保留非管理字段
            existing = config["agents"]["list"][existing_idx]
            merged = {}
            for key, value in existing.items():
                if key not in self.MANAGED_AGENT_FIELDS:
                    merged[key] = value
            merged.update(agent_entry)
            config["agents"]["list"][existing_idx] = merged
        else:
            config["agents"]["list"].append(agent_entry)

        self._write_openclaw_config(config)

    def _agent_to_openclaw_format(self, agent: Agent) -> dict:
        """转换为 OpenClaw 格式"""
        entry = {
            "id": agent.id,
            "workspace": agent.workspace_path,
        }

        if agent.agent_dir:
            entry["agentDir"] = agent.agent_dir

        # 模型配置
        if agent.llm_config:
            entry["model"] = self._model_config_to_openclaw(agent.llm_config)

        # 沙箱配置
        if agent.sandbox_config:
            entry["sandbox"] = self._sandbox_config_to_openclaw(agent.sandbox_config)

        # 工具配置
        if agent.tools_config:
            entry["tools"] = self._tools_config_to_openclaw(agent.tools_config)

        # 心跳配置
        if agent.heartbeat_config:
            entry["heartbeat"] = self._heartbeat_config_to_openclaw(agent.heartbeat_config)

        # Compaction 配置
        if agent.compaction_config:
            entry["compaction"] = self._compaction_config_to_openclaw(agent.compaction_config)

        # 身份配置
        if agent.identity:
            entry["identity"] = {
                "name": agent.identity.name or agent.name,
                "emoji": agent.identity.emoji,
            }
            if agent.identity.avatar:
                entry["identity"]["avatar"] = agent.identity.avatar
            if agent.identity.theme:
                entry["identity"]["theme"] = agent.identity.theme

        # 群聊配置
        if agent.group_chat_config and agent.group_chat_config.mention_patterns:
            entry["groupChat"] = {
                "mentionPatterns": agent.group_chat_config.mention_patterns
            }

        # 运行时配置
        if agent.runtime_config:
            entry["runtime"] = {
                "type": agent.runtime_config.type,
                "acp": self._acp_config_to_openclaw(agent.runtime_config.acp)
            }

        # 子 Agent 配置
        if agent.subagents_config:
            entry["subagents"] = agent.subagents_config

        # 人类延迟
        if agent.human_delay:
            entry["humanDelay"] = {
                "mode": agent.human_delay.mode,
            }
            if agent.human_delay.mode == "custom":
                entry["humanDelay"]["minMs"] = agent.human_delay.min_ms
                entry["humanDelay"]["maxMs"] = agent.human_delay.max_ms

        # 模型参数覆盖
        if agent.params:
            entry["params"] = agent.params

        # 默认标记
        if agent.is_default:
            entry["default"] = True

        return entry

    def _model_config_to_openclaw(self, config: AgentModelConfig) -> dict:
        """转换模型配置"""
        result = {}

        if config.model:
            if config.model.fallbacks:
                result = {
                    "primary": config.model.primary,
                    "fallbacks": config.model.fallbacks,
                }
            else:
                result = config.model.primary  # 简单字符串形式

        return result

    def _sandbox_config_to_openclaw(self, config: SandboxConfig) -> dict:
        """转换沙箱配置"""
        result = {
            "mode": config.mode,
            "backend": config.backend,
            "scope": config.scope,
            "workspaceAccess": config.workspace_access,
        }

        if config.docker and config.backend == "docker":
            result["docker"] = {
                "image": config.docker.image,
                "containerPrefix": config.docker.container_prefix,
                "workdir": config.docker.workdir,
                "network": config.docker.network,
                "user": config.docker.user,
            }

        return result
```

---

## 4. API 设计

### 4.1 Channel API 增强

```python
# backend/app/api/channels.py

from fastapi import APIRouter, Request, HTTPException
from typing import Any

router = APIRouter(prefix="/api/channels", tags=["channels"])

@router.get("")
async def list_channels(request: Request) -> list[dict]:
    """列出所有 Channel"""
    service = request.app.state.channel_service
    return [_channel_to_dict(ch) for ch in service.list_channels()]

@router.post("", status_code=201)
async def create_channel(request: Request, data: dict) -> dict:
    """创建 Channel"""
    service = request.app.state.channel_service
    try:
        channel = service.create_channel(
            channel_id=data["id"],
            name=data["name"],
            type=data["type"],
            enabled=data.get("enabled", True),
            # 多账号
            accounts=_parse_accounts(data.get("accounts")),
            default_account=data.get("default_account", "default"),
            # DM 配置
            dm_policy=data.get("dm_policy", "pairing"),
            allow_from=data.get("allow_from", []),
            # 群组配置
            group_policy=data.get("group_policy", "open"),
            group_allow_from=data.get("group_allow_from", []),
            groups=_parse_groups(data.get("groups", {})),
            # 流式配置
            streaming=data.get("streaming", "partial"),
            block_streaming=data.get("block_streaming", True),
            # 消息限制
            text_chunk_limit=data.get("text_chunk_limit", 2000),
            media_max_mb=data.get("media_max_mb", 100),
            history_limit=data.get("history_limit", 50),
            # 安全配置
            config_writes=data.get("config_writes", True),
            # Telegram 特定
            bot_token=data.get("bot_token"),
            reaction_notifications=data.get("reaction_notifications", "own"),
            reaction_allowlist=data.get("reaction_allowlist", []),
            custom_commands=data.get("custom_commands"),
            dms=data.get("dms", {}),
            dm_history_limit=data.get("dm_history_limit"),
            # Feishu 特定
            domain=data.get("domain", "feishu"),
            connection_mode=data.get("connection_mode", "websocket"),
            app_id=data.get("app_id"),
            app_secret=data.get("app_secret"),
            encrypt_key=data.get("encrypt_key"),
            verification_token=data.get("verification_token"),
            bot_name=data.get("bot_name"),
            typing_indicator=data.get("typing_indicator", True),
            resolve_sender_names=data.get("resolve_sender_names", True),
            webhook_path=data.get("webhook_path", "/feishu/events"),
            webhook_host=data.get("webhook_host", "127.0.0.1"),
            webhook_port=data.get("webhook_port", 3000),
            # WhatsApp 特定
            phone_id=data.get("phone_id"),
        )
        return _channel_to_dict(channel)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{channel_id}")
async def update_channel(request: Request, channel_id: str, data: dict) -> dict:
    """更新 Channel（部分更新）"""
    service = request.app.state.channel_service
    try:
        # 过滤掉 None 值，只更新提供的字段
        update_data = {k: v for k, v in data.items() if v is not None}
        channel = service.update_channel(channel_id, **update_data)
        return _channel_to_dict(channel)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{channel_id}", status_code=204)
async def delete_channel(request: Request, channel_id: str) -> None:
    """删除 Channel"""
    service = request.app.state.channel_service
    try:
        service.delete_channel(channel_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

# ==================== 辅助函数 ====================

def _channel_to_dict(channel: ChannelConfig) -> dict:
    """转换为 API 响应格式（隐藏敏感字段）"""
    return {
        "id": channel.id,
        "name": channel.name,
        "type": channel.type,
        "enabled": channel.enabled,
        # 多账号
        "accounts": _accounts_to_dict(channel.accounts),
        "default_account": channel.default_account,
        # DM 配置
        "dm_policy": channel.dm_policy,
        "allow_from": channel.allow_from,
        # 群组配置
        "group_policy": channel.group_policy,
        "group_allow_from": channel.group_allow_from,
        "groups": channel.groups,
        # 流式配置
        "streaming": channel.streaming,
        "block_streaming": channel.block_streaming,
        # 消息限制
        "text_chunk_limit": channel.text_chunk_limit,
        "media_max_mb": channel.media_max_mb,
        "history_limit": channel.history_limit,
        # 安全配置
        "config_writes": channel.config_writes,
        # Telegram（隐藏 token）
        "bot_token": "***" if channel.bot_token else None,
        "reaction_notifications": channel.reaction_notifications,
        "reaction_allowlist": channel.reaction_allowlist,
        "custom_commands": channel.custom_commands,
        "dms": channel.dms,
        # Feishu（隐藏 secret）
        "domain": channel.domain,
        "connection_mode": channel.connection_mode,
        "app_id": channel.app_id,
        "app_secret": "***" if channel.app_secret else None,
        "encrypt_key": "***" if channel.encrypt_key else None,
        "verification_token": "***" if channel.verification_token else None,
        "bot_name": channel.bot_name,
        "typing_indicator": channel.typing_indicator,
        "resolve_sender_names": channel.resolve_sender_names,
        # WhatsApp
        "phone_id": channel.phone_id,
        # 元数据
        "created_at": channel.created_at.isoformat() if channel.created_at else None,
        "updated_at": channel.updated_at.isoformat() if channel.updated_at else None,
    }

def _parse_accounts(data: dict | None) -> dict | None:
    """解析多账号配置"""
    if not data:
        return None
    # 实现账号解析逻辑
    return data

def _parse_groups(data: dict) -> dict:
    """解析群组配置"""
    return data

def _accounts_to_dict(accounts: dict | None) -> dict | None:
    """转换账号配置（隐藏敏感字段）"""
    if not accounts:
        return None
    result = {}
    for account_id, account in accounts.items():
        entry = {"name": account.name, "enabled": account.enabled}
        if hasattr(account, 'bot_token') and account.bot_token:
            entry["bot_token"] = "***"
        if hasattr(account, 'app_secret') and account.app_secret:
            entry["app_secret"] = "***"
        result[account_id] = entry
    return result
```

### 4.2 Agent API 增强

```python
# backend/app/api/agents.py

# 增强现有的 Agent API，支持新字段

@router.post("", status_code=201)
async def create_agent(request: Request, data: dict) -> dict:
    """创建 Agent"""
    service = request.app.state.agent_service

    # 解析模型配置
    llm_config = _parse_llm_config(data.get("llm_config"))

    # 解析沙箱配置
    sandbox_config = _parse_sandbox_config(data.get("sandbox_config"))

    # 解析工具配置
    tools_config = _parse_tools_config(data.get("tools_config"))

    # 解析心跳配置
    heartbeat_config = _parse_heartbeat_config(data.get("heartbeat_config"))

    # 解析身份配置
    identity = data.get("identity") or {"name": data["name"], "emoji": "🤖"}

    agent = service.create_agent(
        agent_id=data["id"],
        name=data["name"],
        llm_config=llm_config,
        sandbox_config=sandbox_config,
        tools_config=tools_config,
        heartbeat_config=heartbeat_config,
        identity=identity,
        is_default=data.get("is_default", False),
    )

    return _agent_to_dict(agent)
```

---

## 5. 前端设计

### 5.1 Channel 表单结构

```
frontend/components/channels/channel-form/
├── index.tsx                    # 表单容器
├── basic-info-tab.tsx           # 基本信息Tab
├── dm-policy-tab.tsx            # DM 策略Tab
├── group-policy-tab.tsx         # 群组策略Tab
├── streaming-tab.tsx            # 流式配置Tab
├── accounts-tab.tsx             # 多账号管理Tab
├── platform-config/
│   ├── telegram-config.tsx      # Telegram 专用配置
│   ├── feishu-config.tsx        # 飞书专用配置
│   ├── whatsapp-config.tsx      # WhatsApp 专用配置
│   └── index.tsx                # 平台配置路由
└── advanced-tab.tsx             # 高级配置Tab
```

### 5.2 Agent 表单结构

```
frontend/components/agents/agent-form/
├── index.tsx                    # 表单容器
├── basic-info-tab.tsx           # 基本信息
├── model-config-tab.tsx         # 模型配置（增强）
│   ├── model-selector.tsx       # 模型选择器
│   ├── fallbacks-config.tsx     # Fallback 配置
│   └── model-params.tsx         # 模型参数
├── sandbox-config-tab.tsx       # 沙箱配置（增强）
│   ├── sandbox-mode.tsx         # 沙箱模式
│   ├── docker-config.tsx        # Docker 配置
│   └── ssh-config.tsx           # SSH 配置
├── tools-config-tab.tsx         # 工具配置
├── heartbeat-config-tab.tsx     # 心跳配置（增强）
├── identity-config-tab.tsx      # 身份配置
└── advanced-tab.tsx             # 高级配置
    ├── compaction-config.tsx    # Compaction 配置
    ├── runtime-config.tsx       # 运行时配置
    └── human-delay-config.tsx   # 人类延迟配置
```

### 5.3 前端类型定义

```typescript
// frontend/lib/types/channel.ts

export type ChannelType = 'telegram' | 'whatsapp' | 'feishu' | 'discord' | 'slack';
export type DmPolicy = 'pairing' | 'allowlist' | 'open' | 'disabled';
export type GroupPolicy = 'open' | 'allowlist' | 'disabled';
export type StreamingMode = 'off' | 'partial' | 'block';

export interface GroupConfig {
  enabled?: boolean;
  require_mention?: boolean;
  allow_from?: string[];
}

export interface TelegramAccount {
  name?: string;
  enabled?: boolean;
  bot_token?: string;
}

export interface FeishuAccount {
  name?: string;
  enabled?: boolean;
  app_id?: string;
  app_secret?: string;
  domain?: 'feishu' | 'lark';
  bot_name?: string;
}

export interface WhatsAppAccount {
  name?: string;
  enabled?: boolean;
  phone_id?: string;
}

export interface ChannelConfig {
  id: string;
  name: string;
  type: ChannelType;
  enabled: boolean;

  // 多账号
  accounts?: Record<string, TelegramAccount | FeishuAccount | WhatsAppAccount>;
  default_account?: string;

  // DM 配置
  dm_policy: DmPolicy;
  allow_from: string[];

  // 群组配置
  group_policy: GroupPolicy;
  group_allow_from: string[];
  groups: Record<string, GroupConfig>;

  // 流式配置
  streaming: StreamingMode;
  block_streaming?: boolean;

  // 消息限制
  text_chunk_limit?: number;
  media_max_mb: number;
  history_limit?: number;
  dm_history_limit?: number;

  // 安全配置
  config_writes?: boolean;

  // Telegram 特定
  bot_token?: string;
  reaction_notifications?: 'off' | 'own' | 'all' | 'allowlist';
  reaction_allowlist?: string[];
  custom_commands?: Record<string, unknown>;
  dms?: Record<string, unknown>;

  // Feishu 特定
  domain?: 'feishu' | 'lark';
  connection_mode?: 'websocket' | 'webhook';
  app_id?: string;
  app_secret?: string;
  encrypt_key?: string;
  verification_token?: string;
  bot_name?: string;
  typing_indicator?: boolean;
  resolve_sender_names?: boolean;
  webhook_path?: string;
  webhook_host?: string;
  webhook_port?: number;

  // WhatsApp 特定
  phone_id?: string;

  // 元数据
  created_at?: string;
  updated_at?: string;
}
```

```typescript
// frontend/lib/types/agent.ts

export type SandboxMode = 'off' | 'non-main' | 'all';
export type SandboxBackend = 'docker' | 'ssh' | 'openshell';
export type ThinkingLevel = 'off' | 'low' | 'medium' | 'high' | 'adaptive';

export interface ModelReference {
  primary: string;
  fallbacks?: string[];
}

export interface ModelCatalogEntry {
  alias?: string;
  params?: Record<string, unknown>;
}

export interface AgentModelConfig {
  models?: Record<string, ModelCatalogEntry>;
  model?: ModelReference | string;
  image_model?: ModelReference;
  image_generation_model?: ModelReference;
  pdf_model?: ModelReference;
  thinking_default?: ThinkingLevel;
  timeout_seconds?: number;
  context_tokens?: number;
  max_concurrent?: number;
}

export interface DockerSandboxConfig {
  image?: string;
  container_prefix?: string;
  network?: string;
  user?: string;
  memory?: string;
}

export interface SandboxConfig {
  mode?: SandboxMode;
  backend?: SandboxBackend;
  scope?: 'session' | 'agent' | 'shared';
  workspace_access?: 'none' | 'ro' | 'rw';
  docker?: DockerSandboxConfig;
}

export interface HeartbeatConfig {
  every?: string;
  model?: string;
  light_context?: boolean;
  isolated_session?: boolean;
  target?: string;
}

export interface IdentityConfig {
  name?: string;
  emoji?: string;
  avatar?: string;
  theme?: string;
}

export interface CompactionConfig {
  mode?: 'default' | 'safeguard';
  timeout_seconds?: number;
  reserve_tokens_floor?: number;
}

export interface Agent {
  id: string;
  name: string;
  workspace_path: string;
  agent_dir?: string;

  llm_config?: AgentModelConfig;
  sandbox_config?: SandboxConfig;
  tools_config?: ToolsConfig;
  heartbeat_config?: HeartbeatConfig;
  compaction_config?: CompactionConfig;
  identity?: IdentityConfig;

  is_default?: boolean;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}
```

---

## 6. 迁移策略

### 6.1 数据迁移

现有配置无需特殊迁移，因为：
1. 新字段都有默认值
2. 同步逻辑使用 merge 策略，不会破坏现有配置
3. 前端表单增量更新

### 6.2 向后兼容

```python
# 保持向后兼容的模型转换

class ChannelConfig(Base):
    @classmethod
    def from_legacy(cls, data: dict) -> "ChannelConfig":
        """从旧格式转换"""
        return cls(
            id=data["id"],
            name=data["name"],
            type=data["type"],
            enabled=data.get("enabled", True),
            bot_token=data.get("bot_token"),  # 旧格式支持
            # ... 其他字段
        )
```

---

## 7. 测试策略

### 7.1 单元测试

```python
# tests/unit/test_channel_sync.py

def test_sync_preserves_unmanaged_fields():
    """测试同步保留非管理字段"""
    service = ChannelService()
    service._write_openclaw_config({
        "channels": {
            "telegram": {
                "enabled": True,
                "botToken": "existing-token",
                "customField": "should-preserve",  # 非管理字段
            }
        }
    })

    service.create_channel(
        channel_id="test",
        name="Test",
        type="telegram",
        bot_token="new-token",
    )

    config = service._read_openclaw_config()
    assert config["channels"]["telegram"]["customField"] == "should-preserve"
    assert config["channels"]["telegram"]["botToken"] == "new-token"

def test_multi_account_sync():
    """测试多账号同步"""
    service = ChannelService()
    service.create_channel(
        channel_id="feishu-multi",
        name="Multi Feishu",
        type="feishu",
        accounts={
            "main": {"app_id": "cli_xxx", "app_secret": "xxx"},
            "backup": {"app_id": "cli_yyy", "app_secret": "yyy"},
        },
    )

    config = service._read_openclaw_config()
    assert "accounts" in config["channels"]["feishu"]
    assert "main" in config["channels"]["feishu"]["accounts"]
    assert "backup" in config["channels"]["feishu"]["accounts"]
```

### 7.2 集成测试

```python
# tests/integration/test_channel_api.py

def test_create_channel_with_all_fields(client):
    """测试创建包含所有字段的 Channel"""
    response = client.post("/api/channels", json={
        "id": "test-feishu",
        "name": "Test Feishu",
        "type": "feishu",
        "domain": "lark",
        "connection_mode": "websocket",
        "typing_indicator": False,
        "accounts": {
            "main": {
                "app_id": "cli_test",
                "app_secret": "secret",
            }
        }
    })
    assert response.status_code == 201
    data = response.json()
    assert data["domain"] == "lark"
    assert data["typing_indicator"] is False
```

---

## 8. 实施计划

| 阶段 | 任务 | 预计工时 | 依赖 |
|------|------|---------|------|
| **Phase 1** | 同步逻辑修复 | 2h | - |
| **Phase 2** | Channel 模型增强 | 4h | Phase 1 |
| **Phase 3** | Agent 模型增强 | 4h | Phase 1 |
| **Phase 4** | API 增强 | 3h | Phase 2, 3 |
| **Phase 5** | 前端适配 | 4h | Phase 4 |
| **Phase 6** | 测试完善 | 3h | All |
| **总计** | | **20h** | |

---

## 9. 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| 同步逻辑破坏现有配置 | HIGH | 自动备份 + merge 策略 |
| 前端表单过于复杂 | MEDIUM | 分 Tab + 高级配置折叠 |
| 多账号 UI 实现复杂 | MEDIUM | 第一版仅 API 支持 |
| 字段过多导致维护困难 | LOW | 按平台分组 + 类型安全 |

---

## 10. 遗漏分析（Gap Analysis）

基于 OpenClaw 官方文档 `/Users/roc/workspace/openclaw/docs` 的完整审阅，以下为设计遗漏项：

### 10.1 CRITICAL 级别遗漏

#### 10.1.1 Session 配置（完全缺失）

OpenClaw 的 Session 配置是核心功能，当前设计完全缺失：

```python
# backend/app/models/session.py (新建)

class SessionResetConfig(Base):
    """会话重置配置"""
    mode: Literal["daily", "idle"] | None = None
    at_hour: int = 4  # daily 模式重置时间
    idle_minutes: int = 60  # idle 模式超时分钟

class SessionMaintenanceConfig(Base):
    """会话维护配置"""
    mode: Literal["warn", "enforce"] = "warn"
    prune_after: str = "30d"
    max_entries: int = 500
    rotate_bytes: str = "10mb"
    reset_archive_retention: str | bool = "30d"
    max_disk_bytes: str | None = None
    high_water_bytes: str | None = None

class SessionConfig(Base):
    """会话配置

    对应 OpenClaw: session.*
    """
    scope: str = "per-sender"
    dm_scope: Literal["main", "per-peer", "per-channel-peer", "per-account-channel-peer"] = "main"
    identity_links: dict[str, list[str]] = {}  # 跨渠道身份映射
    reset: SessionResetConfig | None = None
    reset_by_type: dict[str, SessionResetConfig] = {}  # direct, group, thread
    reset_triggers: list[str] = ["/new", "/reset"]
    store: str = "~/.openclaw/agents/{agentId}/sessions/sessions.json"
    parent_fork_max_tokens: int = 100000
    maintenance: SessionMaintenanceConfig | None = None
    thread_bindings: dict[str, Any] = {}
    main_key: str = "main"
    agent_to_agent: dict[str, Any] = {}
    send_policy: dict[str, Any] = {}
```

**影响**：无法配置会话隔离、重置策略、存储维护等核心功能

#### 10.1.2 Messages 配置（部分缺失）

```python
# backend/app/models/messages.py (新建或合并到 agent)

class MessageQueueConfig(Base):
    """消息队列配置"""
    mode: Literal["steer", "followup", "collect", "queue", "interrupt"] = "collect"
    debounce_ms: int = 1000
    cap: int = 20
    drop: Literal["old", "new", "summarize"] = "summarize"
    by_channel: dict[str, str] = {}

class InboundConfig(Base):
    """入站消息配置"""
    debounce_ms: int = 2000
    by_channel: dict[str, int] = {}

class MessagesConfig(Base):
    """消息配置

    对应 OpenClaw: messages.*
    """
    response_prefix: str | None = None  # 或 "auto"
    ack_reaction: str = "👀"
    ack_reaction_scope: Literal["group-mentions", "group-all", "direct", "all"] = "group-mentions"
    remove_ack_after_reply: bool = False
    queue: MessageQueueConfig | None = None
    inbound: InboundConfig | None = None
```

**影响**：无法配置响应前缀、确认反应、消息队列、防抖等

### 10.2 HIGH 级别遗漏

#### 10.2.1 Commands 配置

```python
class CommandsConfig(Base):
    """命令配置

    对应 OpenClaw: commands.*
    """
    native: Literal["auto"] | bool = "auto"
    text: bool = True
    bash: bool = False
    bash_foreground_ms: int = 2000
    config: bool = False
    debug: bool = False
    restart: bool = False
    allow_from: dict[str, list[str]] = {}  # channel -> user list
    use_access_groups: bool = True
```

#### 10.2.2 Tools 完整配置

```python
class WebSearchConfig(Base):
    """Web 搜索配置"""
    enabled: bool = True
    api_key: str | None = None
    max_results: int = 5
    timeout_seconds: int = 30
    cache_ttl_minutes: int = 15

class WebFetchConfig(Base):
    """Web 获取配置"""
    enabled: bool = True
    max_chars: int = 50000
    timeout_seconds: int = 30
    cache_ttl_minutes: int = 15

class MediaConfig(Base):
    """媒体处理配置"""
    concurrency: int = 2
    audio: dict[str, Any] = {}
    video: dict[str, Any] = {}

class LoopDetectionConfig(Base):
    """工具循环检测配置"""
    enabled: bool = False
    history_size: int = 30
    warning_threshold: int = 10
    critical_threshold: int = 20
    global_circuit_breaker_threshold: int = 30
    detectors: dict[str, bool] = {}

class ToolsConfig(Base):
    """完整工具配置"""
    profile: str | None = None
    allow: list[str] = []
    deny: list[str] = []
    elevated: ElevatedToolsConfig | None = None
    exec: dict[str, Any] | None = None
    loop_detection: LoopDetectionConfig | None = None
    web: dict[str, WebSearchConfig | WebFetchConfig] | None = None
    media: MediaConfig | None = None
    agent_to_agent: dict[str, Any] | None = None
    sessions: dict[str, Any] | None = None
    by_provider: dict[str, dict[str, Any]] = {}  # 按提供商覆盖
```

### 10.3 MEDIUM 级别遗漏

#### 10.3.1 Telegram 完整字段

| 缺失字段 | 类型 | 说明 |
|---------|------|------|
| `token_file` | str | 从文件读取 token（安全特性） |
| `timeout_seconds` | int | API 客户端超时 |
| `retry` | dict | 重试策略 |
| `link_preview` | bool | 链接预览开关 |
| `reply_to_mode` | str | 回复线程模式 |
| `network` | dict | 网络配置（autoSelectFamily, dnsResultOrder） |
| `proxy` | str | 代理 URL |
| `webhook_url` | str | Webhook 模式 URL |
| `webhook_secret` | str | Webhook 密钥 |
| `capabilities` | dict | 能力配置（inlineButtons 等） |
| `actions` | dict | 动作开关（sendMessage, reactions, sticker 等） |
| `exec_approvals` | dict | Exec 审批配置 |

#### 10.3.2 WhatsApp 完整字段

| 缺失字段 | 类型 | 说明 |
|---------|------|------|
| `ack_reaction` | dict | 确认反应配置 |
| `send_read_receipts` | bool | 已读回执 |
| `chunk_mode` | str | 分块模式 |
| `debounce_ms` | int | 防抖毫秒 |
| `self_chat_mode` | bool | 自聊模式 |
| `web` | dict | Web 连接配置 |

#### 10.3.3 流式与延迟配置

```python
class BlockStreamingConfig(Base):
    """块级流式配置"""
    block_streaming_default: Literal["on", "off"] = "off"
    block_streaming_break: Literal["text_end", "message_end"] = "text_end"
    block_streaming_chunk: dict[str, int] = {"minChars": 800, "maxChars": 1200}
    block_streaming_coalesce: dict[str, int] = {"idleMs": 1000}

class HumanDelayConfig(Base):
    """人类延迟配置"""
    mode: Literal["off", "natural", "custom"] = "natural"
    min_ms: int | None = None
    max_ms: int | None = None

class TypingConfig(Base):
    """输入提示配置"""
    typing_mode: Literal["never", "instant", "thinking", "message"] = "instant"
    typing_interval_seconds: int = 6
```

### 10.4 Bindings 配置（多 Agent 路由）

```python
class BindingMatch(Base):
    """绑定匹配规则"""
    channel: str
    account_id: str | None = None
    peer: dict[str, Any] | None = None  # { kind: direct|group|channel, id }
    guild_id: str | None = None
    team_id: str | None = None

class AcpBindingConfig(Base):
    """ACP 绑定配置"""
    mode: str = "persistent"
    label: str | None = None
    cwd: str | None = None
    backend: str = "acpx"

class Binding(Base):
    """Agent 绑定"""
    type: Literal["route", "acp"] = "route"
    agent_id: str
    match: BindingMatch
    acp: AcpBindingConfig | None = None  # 仅 type="acp" 时使用
```

### 10.5 TTS 配置（可选）

```python
class ElevenLabsConfig(Base):
    """ElevenLabs TTS 配置"""
    api_key: str | None = None
    base_url: str = "https://api.elevenlabs.io"
    voice_id: str | None = None
    model_id: str = "eleven_multilingual_v2"
    voice_settings: dict[str, Any] = {}

class OpenAITTSConfig(Base):
    """OpenAI TTS 配置"""
    api_key: str | None = None
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini-tts"
    voice: str = "alloy"

class TTSConfig(Base):
    """TTS 配置"""
    auto: Literal["off", "always", "inbound", "tagged"] = "off"
    mode: Literal["final", "all"] = "final"
    provider: str = "elevenlabs"
    max_text_length: int = 4000
    timeout_ms: int = 30000
    elevenlabs: ElevenLabsConfig | None = None
    openai: OpenAITTSConfig | None = None
```

---

## 11. 补充实施计划

### 11.1 优先级调整

| 阶段 | 任务 | 优先级 | 预计工时 |
|------|------|--------|---------|
| **Phase 0** | 遗漏分析验证 | CRITICAL | 1h |
| **Phase 1** | 同步逻辑修复 | CRITICAL | 2h |
| **Phase 2a** | Session 配置支持 | HIGH | 3h |
| **Phase 2b** | Messages 配置支持 | HIGH | 2h |
| **Phase 2c** | Commands 配置支持 | HIGH | 2h |
| **Phase 3a** | Channel 模型完整字段 | HIGH | 4h |
| **Phase 3b** | Agent 模型增强 | HIGH | 4h |
| **Phase 4** | Bindings 支持 | MEDIUM | 3h |
| **Phase 5** | API 增强 | MEDIUM | 3h |
| **Phase 6** | 前端适配 | MEDIUM | 4h |
| **Phase 7** | 测试完善 | LOW | 3h |
| **总计** | | | **31h** |

### 11.2 建议实施顺序

1. **Phase 1-2**（核心修复 + 关键缺失）：11h
   - 同步逻辑修复
   - Session、Messages、Commands 配置

2. **Phase 3-4**（完整模型）：11h
   - Channel 完整字段
   - Agent 增强
   - Bindings 支持

3. **Phase 5-7**（前端与测试）：10h
   - API 增强
   - 前端适配
   - 测试完善

---

## 12. 验收标准

### 12.1 功能验收

- [ ] Channel 同步采用 merge 策略，保留非管理字段
- [ ] 支持 Telegram 完整配置（30+ 字段）
- [ ] 支持 Feishu 完整配置（15+ 字段）
- [ ] 支持 WhatsApp 完整配置（15+ 字段）
- [ ] 支持多账号配置结构
- [ ] Agent 支持 Session 配置
- [ ] Agent 支持 Messages 配置
- [ ] Agent 支持 Commands 配置
- [ ] 支持 Bindings 多 Agent 路由

### 12.2 兼容性验收

- [ ] 现有配置无需迁移
- [ ] 新字段有合理默认值
- [ ] 非管理字段不被覆盖

### 12.3 测试验收

- [ ] 单元测试覆盖率 ≥80%
- [ ] 集成测试通过
- [ ] 手动验证同步逻辑
