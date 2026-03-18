"""Agent 配置管理服务。

REQ-0001-003: Agent 配置管理
REQ-0001-027: Agent 配置完整对齐

提供 Agent 的 CRUD 操作和配置文件管理。
SOP Engine 是 Agent 配置的唯一来源（Source of Truth）。
"""
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape

from app.models import Agent, AgentConfigFile
from app.models.commands_config import CommandsConfig
from app.models.messages_config import MessagesConfig
from app.models.session_config import SessionConfig


@dataclass
class AgentService:
    """Agent 配置管理服务

    负责 Agent 的创建、更新、删除和配置文件管理。
    所有配置变更都会同步到 OpenClaw workspace。
    """

    workspace_root: Path
    _agents: dict[str, Agent] = field(default_factory=dict)
    _config_files: dict[str, list[AgentConfigFile]] = field(default_factory=dict)
    _jinja_env: Environment | None = field(default=None, repr=False)
    _openclaw_config_path: Path = field(default=None, repr=False)

    def __post_init__(self):
        """初始化 Jinja 环境和 OpenClaw 配置路径"""
        if isinstance(self.workspace_root, str):
            self.workspace_root = Path(self.workspace_root)

        template_dir = Path(__file__).parent.parent / "templates" / "agent_defaults"
        if template_dir.exists():
            self._jinja_env = Environment(
                loader=FileSystemLoader(template_dir),
                autoescape=select_autoescape(["html", "xml"]),
            )

        # OpenClaw 配置文件路径
        self._openclaw_config_path = Path.home() / ".openclaw" / "openclaw.json"

    def create_agent(
        self,
        agent_id: str,
        name: str,
        llm_config: dict[str, Any] | None = None,
        sandbox_config: dict[str, Any] | None = None,
        tools_config: dict[str, Any] | None = None,
        heartbeat_config: dict[str, Any] | None = None,
        memory_search_config: dict[str, Any] | None = None,
        group_chat_config: dict[str, Any] | None = None,
        identity: dict[str, Any] | None = None,
        is_default: bool = False,
        # REQ-0001-027: OpenClaw 完整配置对齐
        session_config: SessionConfig | None = None,
        messages_config: MessagesConfig | None = None,
        commands_config: CommandsConfig | None = None,
    ) -> Agent:
        """创建 Agent 并生成默认配置文件

        Args:
            agent_id: Agent 唯一标识
            name: Agent 显示名称
            llm_config: 模型配置 (primary, fallbacks)
            sandbox_config: 沙箱配置 (mode, workspaceAccess, scope)
            tools_config: 工具配置 (allow, deny)
            heartbeat_config: 心跳配置 (every, target)
            memory_search_config: 记忆搜索配置 (enabled, provider, model)
            group_chat_config: 群聊配置 (mentionPatterns)
            identity: 身份标识 (name, emoji)
            is_default: 是否为默认 Agent
            session_config: Session 配置 (dmScope, reset, maintenance)
            messages_config: Messages 配置 (queue, inbound, responsePrefix)
            commands_config: Commands 配置 (native, text, bash)

        Returns:
            创建的 Agent 实例
        """
        if agent_id in self._agents:
            raise ValueError(f"Agent '{agent_id}' already exists")

        workspace_path = str(self.workspace_root / agent_id)

        agent = Agent(
            id=agent_id,
            name=name,
            workspace_path=workspace_path,
            llm_config=llm_config or {"primary": "claude-3-5-sonnet"},
            sandbox_config=sandbox_config or {"mode": "non-main"},
            tools_config=tools_config or {"allow": []},
            heartbeat_config=heartbeat_config,
            memory_search_config=memory_search_config,
            group_chat_config=group_chat_config,
            identity=identity or {"name": name, "emoji": "🤖"},
            is_default=is_default,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            # REQ-0001-027
            session_config=session_config,
            messages_config=messages_config,
            commands_config=commands_config,
        )

        self._agents[agent_id] = agent

        # 生成默认配置文件
        self._generate_default_config_files(agent)

        # 创建 workspace 目录并写入文件
        self._ensure_workspace(agent_id)

        # 注册到 OpenClaw（写入 openclaw.json）
        self._register_to_openclaw(agent)

        return agent

    def get_agent(self, agent_id: str) -> Agent:
        """获取 Agent

        Args:
            agent_id: Agent 唯一标识

        Returns:
            Agent 实例

        Raises:
            KeyError: Agent 不存在
        """
        if agent_id not in self._agents:
            raise KeyError(f"Agent '{agent_id}' not found")
        return self._agents[agent_id]

    def list_agents(self) -> list[Agent]:
        """列出所有 Agent

        Returns:
            Agent 列表
        """
        return list(self._agents.values())

    def update_agent(
        self,
        agent_id: str,
        name: str | None = None,
        llm_config: dict[str, Any] | None = None,
        sandbox_config: dict[str, Any] | None = None,
        tools_config: dict[str, Any] | None = None,
        heartbeat_config: dict[str, Any] | None = None,
        memory_search_config: dict[str, Any] | None = None,
        group_chat_config: dict[str, Any] | None = None,
        identity: dict[str, Any] | None = None,
        is_default: bool | None = None,
        is_active: bool | None = None,
        # REQ-0001-027: OpenClaw 完整配置对齐
        session_config: SessionConfig | None = None,
        messages_config: MessagesConfig | None = None,
        commands_config: CommandsConfig | None = None,
    ) -> Agent:
        """更新 Agent

        Args:
            agent_id: Agent 唯一标识
            name: 新的显示名称
            llm_config: 新的模型配置
            sandbox_config: 新的沙箱配置
            tools_config: 新的工具配置
            heartbeat_config: 新的心跳配置
            memory_search_config: 新的记忆搜索配置
            group_chat_config: 新的群聊配置
            identity: 新的身份标识
            is_default: 是否为默认 Agent
            is_active: 是否激活
            session_config: 新的 Session 配置
            messages_config: 新的 Messages 配置
            commands_config: 新的 Commands 配置

        Returns:
            更新后的 Agent 实例
        """
        agent = self.get_agent(agent_id)

        # 构建更新后的 Agent
        updated_agent = Agent(
            id=agent.id,
            name=name if name is not None else agent.name,
            workspace_path=agent.workspace_path,
            llm_config=llm_config if llm_config is not None else agent.llm_config,
            sandbox_config=sandbox_config if sandbox_config is not None else agent.sandbox_config,
            tools_config=tools_config if tools_config is not None else agent.tools_config,
            heartbeat_config=heartbeat_config if heartbeat_config is not None else agent.heartbeat_config,
            memory_search_config=memory_search_config if memory_search_config is not None else agent.memory_search_config,
            group_chat_config=group_chat_config if group_chat_config is not None else agent.group_chat_config,
            identity=identity if identity is not None else agent.identity,
            is_default=is_default if is_default is not None else agent.is_default,
            is_active=is_active if is_active is not None else agent.is_active,
            created_at=agent.created_at,
            updated_at=datetime.utcnow(),
            # REQ-0001-027
            session_config=session_config if session_config is not None else agent.session_config,
            messages_config=messages_config if messages_config is not None else agent.messages_config,
            commands_config=commands_config if commands_config is not None else agent.commands_config,
        )

        self._agents[agent_id] = updated_agent

        # 重新生成配置文件
        self._generate_default_config_files(updated_agent)
        self._ensure_workspace(agent_id)

        # 更新 OpenClaw 注册
        self._register_to_openclaw(updated_agent)

        return updated_agent

    def delete_agent(self, agent_id: str) -> None:
        """删除 Agent

        Args:
            agent_id: Agent 唯一标识

        Raises:
            KeyError: Agent 不存在
        """
        if agent_id not in self._agents:
            raise KeyError(f"Agent '{agent_id}' not found")

        del self._agents[agent_id]

        # 清理配置文件
        if agent_id in self._config_files:
            del self._config_files[agent_id]

        # 清理 workspace 目录
        workspace_path = self.workspace_root / agent_id
        if workspace_path.exists():
            import shutil
            shutil.rmtree(workspace_path)

        # 从 OpenClaw 注销
        self._unregister_from_openclaw(agent_id)

    def sync_agent(self, agent_id: str) -> dict[str, Any]:
        """手动同步 Agent 到 OpenClaw

        Args:
            agent_id: Agent 唯一标识

        Returns:
            同步结果

        Raises:
            KeyError: Agent 不存在
        """
        agent = self.get_agent(agent_id)

        # 重新生成配置文件
        self._generate_default_config_files(agent)
        self._ensure_workspace(agent_id)

        # 注册到 OpenClaw
        self._register_to_openclaw(agent)

        return {
            "status": "synced",
            "agent_id": agent_id,
            "workspace": agent.workspace_path,
            "files": [f.file_type for f in self._config_files.get(agent_id, [])],
        }

    def get_config_file(self, agent_id: str, file_type: str) -> str:
        """获取配置文件内容

        Args:
            agent_id: Agent 唯一标识
            file_type: 文件类型 (AGENTS.md, SOUL.md 等)

        Returns:
            文件内容

        Raises:
            KeyError: Agent 或文件不存在
        """
        files = self._config_files.get(agent_id, [])
        for f in files:
            if f.file_type == file_type:
                return f.content

        # 尝试从文件系统读取
        file_path = self.workspace_root / agent_id / file_type
        if file_path.exists():
            return file_path.read_text()

        raise KeyError(f"Config file '{file_type}' not found for agent '{agent_id}'")

    def update_config_file(
        self,
        agent_id: str,
        file_type: str,
        content: str,
    ) -> AgentConfigFile:
        """更新配置文件

        Args:
            agent_id: Agent 唯一标识
            file_type: 文件类型
            content: 文件内容

        Returns:
            更新后的配置文件
        """
        # 验证 Agent 存在
        self.get_agent(agent_id)

        config_file = AgentConfigFile(
            id=f"{agent_id}-{file_type}",
            agent_id=agent_id,
            file_type=file_type,
            content=content,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        if agent_id not in self._config_files:
            self._config_files[agent_id] = []

        # 更新或添加
        files = self._config_files[agent_id]
        for i, f in enumerate(files):
            if f.file_type == file_type:
                files[i] = config_file
                break
        else:
            files.append(config_file)

        # 写入文件系统
        self._write_config_file(agent_id, file_type, content)

        return config_file

    def list_config_files(self, agent_id: str) -> list[AgentConfigFile]:
        """列出 Agent 的所有配置文件

        Args:
            agent_id: Agent 唯一标识

        Returns:
            配置文件列表
        """
        # 验证 Agent 存在
        self.get_agent(agent_id)

        files = self._config_files.get(agent_id, [])

        # 从文件系统补充
        workspace_path = self.workspace_root / agent_id
        if workspace_path.exists():
            for file_path in workspace_path.iterdir():
                if file_path.is_file() and file_path.suffix == ".md":
                    file_type = file_path.name
                    # 检查是否已在内存中
                    if not any(f.file_type == file_type for f in files):
                        files.append(AgentConfigFile(
                            id=f"{agent_id}-{file_type}",
                            agent_id=agent_id,
                            file_type=file_type,
                            content=file_path.read_text(),
                        ))

        return files

    # ==================== OpenClaw 注册相关方法 ====================

    def _register_to_openclaw(self, agent: Agent) -> None:
        """将 Agent 注册到 ~/.openclaw/openclaw.json

        同步完整的 Agent 配置，包括：
        - id, workspace
        - model (primary, fallbacks)
        - sandbox (mode, workspaceAccess, scope, docker)
        - tools (profile, allow, deny)
        - identity (name, emoji)
        - subagents (allowAgents)
        - session (dmScope, reset, maintenance) - REQ-0001-027
        - messages (queue, inbound, responsePrefix) - REQ-0001-027
        - commands (native, text, bash) - REQ-0001-027

        Args:
            agent: Agent 实例
        """
        # 1. 备份现有配置
        self._backup_openclaw_config()

        config = self._read_openclaw_config()

        # 确保 agents.list 存在
        if "agents" not in config:
            config["agents"] = {}
        if "list" not in config["agents"]:
            config["agents"]["list"] = []

        # 2. 构建完整 agent 条目
        agent_entry: dict[str, Any] = {
            "id": agent.id,
            "workspace": agent.workspace_path,
        }

        # model 配置
        if agent.llm_config:
            model: dict[str, Any] = {}
            if "primary" in agent.llm_config:
                model["primary"] = agent.llm_config["primary"]
            if "fallbacks" in agent.llm_config:
                model["fallbacks"] = agent.llm_config["fallbacks"]
            if model:
                agent_entry["model"] = model

        # sandbox 配置
        if agent.sandbox_config:
            agent_entry["sandbox"] = agent.sandbox_config.copy()

        # tools 配置
        if agent.tools_config:
            tools: dict[str, Any] = {}
            for key in ["profile", "allow", "deny"]:
                if key in agent.tools_config:
                    tools[key] = agent.tools_config[key]
            if tools:
                agent_entry["tools"] = tools

        # identity 配置
        agent_entry["identity"] = agent.identity or {
            "name": agent.name,
            "emoji": "🤖",
        }

        # subagents 配置 (从 group_chat_config 提取)
        group_chat = agent.group_chat_config or {}
        agent_entry["subagents"] = {
            "allowAgents": group_chat.get("mentionPatterns", [])
        }

        # === REQ-0001-027: Session/Messages/Commands 配置 ===

        # session 配置
        if agent.session_config:
            agent_entry["session"] = agent.session_config.to_openclaw()

        # messages 配置
        if agent.messages_config:
            agent_entry["messages"] = agent.messages_config.to_openclaw()

        # commands 配置
        if agent.commands_config:
            agent_entry["commands"] = agent.commands_config.to_openclaw()

        # 3. 更新或添加到 agents.list
        existing_idx = next(
            (i for i, a in enumerate(config["agents"]["list"])
             if a.get("id") == agent.id),
            None
        )

        if existing_idx is not None:
            # 使用 merge 策略：保留现有条目中未由 SOP Engine 管理的字段
            existing = config["agents"]["list"][existing_idx]
            # 只更新 SOP Engine 管理的字段
            managed_keys = [
                "model", "sandbox", "tools", "identity", "subagents",
                "session", "messages", "commands",  # REQ-0001-027
            ]
            for key in managed_keys:
                if key in agent_entry:
                    existing[key] = agent_entry[key]
                elif key in existing:
                    del existing[key]
            # 更新 id 和 workspace
            existing["id"] = agent_entry["id"]
            existing["workspace"] = agent_entry["workspace"]
        else:
            config["agents"]["list"].append(agent_entry)

        # 写回配置
        self._write_openclaw_config(config)

    def _backup_openclaw_config(self) -> None:
        """备份 openclaw.json

        在每次修改前创建时间戳备份文件。
        """
        if self._openclaw_config_path.exists():
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_path = self._openclaw_config_path.with_suffix(
                f".json.backup.{timestamp}"
            )
            import shutil
            shutil.copy2(self._openclaw_config_path, backup_path)

    def _unregister_from_openclaw(self, agent_id: str) -> None:
        """从 ~/.openclaw/openclaw.json 移除 Agent

        Args:
            agent_id: Agent 唯一标识
        """
        config = self._read_openclaw_config()

        if "agents" not in config or "list" not in config["agents"]:
            return

        # 过滤掉该 agent
        config["agents"]["list"] = [
            a for a in config["agents"]["list"]
            if a.get("id") != agent_id
        ]

        self._write_openclaw_config(config)

    def _read_openclaw_config(self) -> dict[str, Any]:
        """读取 OpenClaw 配置文件

        Returns:
            配置字典
        """
        if self._openclaw_config_path.exists():
            try:
                content = self._openclaw_config_path.read_text()
                return json.loads(content)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _write_openclaw_config(self, config: dict[str, Any]) -> None:
        """写入 OpenClaw 配置文件

        Args:
            config: 配置字典
        """
        self._openclaw_config_path.parent.mkdir(parents=True, exist_ok=True)
        self._openclaw_config_path.write_text(
            json.dumps(config, indent=2, ensure_ascii=False) + "\n"
        )

    # ==================== 配置文件生成相关方法 ====================

    def _generate_default_config_files(self, agent: Agent) -> None:
        """生成默认配置文件"""
        default_files = ["AGENTS.md", "SOUL.md", "USER.md", "IDENTITY.md"]

        self._config_files[agent.id] = []

        for file_type in default_files:
            content = self._render_template(agent, file_type)
            config_file = AgentConfigFile(
                id=f"{agent.id}-{file_type}",
                agent_id=agent.id,
                file_type=file_type,
                content=content,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            self._config_files[agent.id].append(config_file)

    def _render_template(self, agent: Agent, file_type: str) -> str:
        """渲染配置文件模板"""
        template_name = f"{file_type}.jinja"

        if self._jinja_env:
            try:
                template = self._jinja_env.get_template(template_name)
                return template.render(
                    agent=agent,
                    agent_type="assistant",
                    model_config=agent.llm_config,
                    sandbox_config=agent.sandbox_config,
                    tools_config=agent.tools_config,
                    heartbeat_config=agent.heartbeat_config,
                    memory_search_config=agent.memory_search_config,
                    group_chat_config=agent.group_chat_config,
                )
            except TemplateNotFound:
                pass  # Fall through to default template

        # 默认模板
        return f"# {file_type.replace('.md', '')}\n\nAgent: {agent.name} ({agent.id})\n"

    def _ensure_workspace(self, agent_id: str) -> None:
        """确保 workspace 目录存在"""
        workspace_path = self.workspace_root / agent_id
        workspace_path.mkdir(parents=True, exist_ok=True)

        # 写入默认配置文件
        for config_file in self._config_files.get(agent_id, []):
            self._write_config_file(
                agent_id,
                config_file.file_type,
                config_file.content,
            )

    def _write_config_file(self, agent_id: str, file_type: str, content: str) -> None:
        """写入配置文件到文件系统"""
        file_path = self.workspace_root / agent_id / file_type
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)
