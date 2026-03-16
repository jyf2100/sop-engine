"""Agent 配置管理服务。

REQ-0001-003: Agent 配置管理

提供 Agent 的 CRUD 操作和配置文件管理。
SOP Engine 是 Agent 配置的唯一来源（Source of Truth）。
"""
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, TemplateNotFound, select_autoescape

from app.config import settings
from app.models import Agent, AgentConfigFile


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

    def __post_init__(self):
        """初始化 Jinja 环境"""
        if isinstance(self.workspace_root, str):
            self.workspace_root = Path(self.workspace_root)

        template_dir = Path(__file__).parent.parent / "templates" / "agent_defaults"
        if template_dir.exists():
            self._jinja_env = Environment(
                loader=FileSystemLoader(template_dir),
                autoescape=select_autoescape(["html", "xml"]),
            )

    def create_agent(
        self,
        agent_id: str,
        name: str,
        llm_config: dict[str, Any] | None = None,
        sandbox_config: dict[str, Any] | None = None,
        tools_config: dict[str, Any] | None = None,
        is_default: bool = False,
    ) -> Agent:
        """创建 Agent 并生成默认配置文件

        Args:
            agent_id: Agent 唯一标识
            name: Agent 显示名称
            llm_config: 模型配置 (primary, fallbacks)
            sandbox_config: 沙箱配置 (mode, workspaceAccess, scope)
            tools_config: 工具配置 (allow, deny)
            is_default: 是否为默认 Agent

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
            is_default=is_default,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self._agents[agent_id] = agent

        # 生成默认配置文件
        self._generate_default_config_files(agent)

        # 创建 workspace 目录
        self._ensure_workspace(agent_id)

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
        is_default: bool | None = None,
        is_active: bool | None = None,
    ) -> Agent:
        """更新 Agent

        Args:
            agent_id: Agent 唯一标识
            name: 新的显示名称
            llm_config: 新的模型配置
            sandbox_config: 新的沙箱配置
            tools_config: 新的工具配置
            is_default: 是否为默认 Agent
            is_active: 是否激活

        Returns:
            更新后的 Agent 实例
        """
        agent = self.get_agent(agent_id)

        if name is not None:
            agent = Agent(
                id=agent.id,
                name=name,
                workspace_path=agent.workspace_path,
                llm_config=llm_config or agent.llm_config,
                sandbox_config=sandbox_config or agent.sandbox_config,
                tools_config=tools_config or agent.tools_config,
                heartbeat_config=agent.heartbeat_config,
                memory_search_config=agent.memory_search_config,
                group_chat_config=agent.group_chat_config,
                is_default=is_default if is_default is not None else agent.is_default,
                is_active=is_active if is_active is not None else agent.is_active,
                created_at=agent.created_at,
                updated_at=datetime.utcnow(),
            )
        elif llm_config or sandbox_config or tools_config:
            agent = Agent(
                id=agent.id,
                name=agent.name,
                workspace_path=agent.workspace_path,
                llm_config=llm_config or agent.llm_config,
                sandbox_config=sandbox_config or agent.sandbox_config,
                tools_config=tools_config or agent.tools_config,
                heartbeat_config=agent.heartbeat_config,
                memory_search_config=agent.memory_search_config,
                group_chat_config=agent.group_chat_config,
                is_default=is_default if is_default is not None else agent.is_default,
                is_active=is_active if is_active is not None else agent.is_active,
                created_at=agent.created_at,
                updated_at=datetime.utcnow(),
            )

        self._agents[agent_id] = agent
        return agent

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
