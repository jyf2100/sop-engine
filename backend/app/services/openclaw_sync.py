"""OpenClaw 同步服务。

REQ-0001-003: Agent 配置管理

负责将 Agent 配置同步到 OpenClaw workspace 和 openclaw.json。
"""
import json
import shutil
from pathlib import Path
from typing import Any

from app.models import Agent, AgentConfigFile


class OpenClawSync:
    """OpenClaw 同步服务

    将 SOP Engine 中的 Agent 配置同步到 OpenClaw：
    1. 写入 workspace 文件到 {OPENCLAW_WORKSPACE_ROOT}/{agent_id}/
    2. 更新 openclaw.json 的 agents.list[] 和 bindings
    """

    def __init__(self, workspace_root: Path | str):
        if isinstance(workspace_root, str):
            workspace_root = Path(workspace_root)
        self.workspace_root = workspace_root
        self.openclaw_json_path = workspace_root / "openclaw.json"

    def sync_agent(
        self,
        agent: Agent,
        config_files: list[AgentConfigFile] | None = None,
    ) -> None:
        """同步 Agent 到 OpenClaw

        Args:
            agent: Agent 实例
            config_files: 可选的配置文件列表，不提供则只更新元数据
        """
        # 确保 workspace 目录存在
        agent_workspace = self.workspace_root / agent.id
        agent_workspace.mkdir(parents=True, exist_ok=True)

        # 同步配置文件
        if config_files:
            for config_file in config_files:
                self._write_config_file(agent.id, config_file.file_type, config_file.content)
        else:
            # 生成默认配置文件
            self._generate_default_files(agent)

        # 更新 openclaw.json
        self._update_openclaw_json(agent)

    def delete_agent(self, agent_id: str) -> None:
        """删除 Agent 并清理相关文件

        Args:
            agent_id: Agent ID
        """
        # 删除 workspace 目录
        agent_workspace = self.workspace_root / agent_id
        if agent_workspace.exists():
            shutil.rmtree(agent_workspace)

        # 更新 openclaw.json
        self._remove_from_openclaw_json(agent_id)

    def _write_config_file(self, agent_id: str, file_type: str, content: str) -> None:
        """写入配置文件"""
        file_path = self.workspace_root / agent_id / file_type
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)

    def _generate_default_files(self, agent: Agent) -> None:
        """生成默认配置文件"""
        default_files = {
            "AGENTS.md": f"""# Agent 操作指令

## 基本信息

- **Agent ID**: `{agent.id}`
- **名称**: {agent.name}

## 行为规则

1. **响应模式**：根据用户请求执行相应操作
2. **错误处理**：遇到问题时提供清晰的错误信息
3. **输出格式**：保持输出简洁、结构化

---
*此文件由 SOP Engine 自动生成*
""",
            "SOUL.md": f"""# Agent 人设

## 角色定义

你是一个专业的 AI 助手，名为 **{agent.name}**。

## 核心特质

- **专业**：提供准确、可靠的信息和服务
- **友好**：以礼貌、耐心的态度与用户沟通
- **高效**：快速理解需求并给出解决方案

---
*此文件由 SOP Engine 自动生成*
""",
            "USER.md": f"""# 用户信息

## 默认用户

- **称呼**：用户
- **角色**：操作员

---
*此文件由 SOP Engine 自动生成*
""",
            "IDENTITY.md": f"""# Agent 身份

## 基本信息

| 属性 | 值 |
|------|-----|
| ID | `{agent.id}` |
| 名称 | {agent.name} |

## 模型配置

```json
{json.dumps(agent.llm_config, indent=2, ensure_ascii=False)}
```

---
*此文件由 SOP Engine 自动生成*
""",
        }

        for file_type, content in default_files.items():
            self._write_config_file(agent.id, file_type, content)

    def _update_openclaw_json(self, agent: Agent) -> None:
        """更新 openclaw.json"""
        if self.openclaw_json_path.exists():
            config = json.loads(self.openclaw_json_path.read_text())
        else:
            config = {
                "agents": {"list": [], "defaults": {}},
                "bindings": [],
            }

        # 确保结构存在
        if "agents" not in config:
            config["agents"] = {"list": [], "defaults": {}}
        if "list" not in config["agents"]:
            config["agents"]["list"] = []
        if "bindings" not in config:
            config["bindings"] = []

        # 构建 agent 配置
        agent_config = self._build_agent_config(agent)

        # 更新或添加 agent
        existing_idx = None
        for i, a in enumerate(config["agents"]["list"]):
            if a.get("id") == agent.id:
                existing_idx = i
                break

        if existing_idx is not None:
            config["agents"]["list"][existing_idx] = agent_config
        else:
            config["agents"]["list"].append(agent_config)

        # 处理 default binding
        if agent.is_default:
            binding = {
                "agentId": agent.id,
                "type": "default",
            }
            # 移除旧的 default binding
            config["bindings"] = [b for b in config["bindings"] if b.get("type") != "default"]
            config["bindings"].append(binding)

        # 写回文件
        self.openclaw_json_path.write_text(json.dumps(config, indent=2, ensure_ascii=False))

    def _remove_from_openclaw_json(self, agent_id: str) -> None:
        """从 openclaw.json 移除 agent"""
        if not self.openclaw_json_path.exists():
            return

        config = json.loads(self.openclaw_json_path.read_text())

        # 移除 agent
        config["agents"]["list"] = [
            a for a in config["agents"]["list"] if a.get("id") != agent_id
        ]

        # 移除相关 bindings
        config["bindings"] = [
            b for b in config["bindings"] if b.get("agentId") != agent_id
        ]

        self.openclaw_json_path.write_text(json.dumps(config, indent=2, ensure_ascii=False))

    def _build_agent_config(self, agent: Agent) -> dict[str, Any]:
        """构建 openclaw.json agents.list[] 条目"""
        config: dict[str, Any] = {
            "id": agent.id,
            "name": agent.name,
            "workspace": str(self.workspace_root / agent.id),
        }

        # 模型配置
        if agent.llm_config:
            if "model" not in config:
                config["model"] = {}
            if "primary" in agent.llm_config:
                config["model"]["primary"] = agent.llm_config["primary"]
            if "fallbacks" in agent.llm_config:
                config["model"]["fallbacks"] = agent.llm_config["fallbacks"]

        # 沙箱配置
        if agent.sandbox_config:
            config["sandbox"] = agent.sandbox_config

        # 工具配置
        if agent.tools_config:
            if "tools" not in config:
                config["tools"] = {}
            config["tools"].update(agent.tools_config)

        # 心跳配置
        if agent.heartbeat_config:
            config["heartbeat"] = agent.heartbeat_config

        # 记忆搜索配置
        if agent.memory_search_config:
            config["memorySearch"] = agent.memory_search_config

        # 群聊配置
        if agent.group_chat_config:
            config["groupChat"] = agent.group_chat_config

        # 默认 Agent 标记
        if agent.is_default:
            config["default"] = True

        return config
