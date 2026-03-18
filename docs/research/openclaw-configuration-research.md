# OpenClaw 配置机制研究报告

> 研究日期：2026-03-17
> 目的：了解 SOP Engine 如何正确地将 Agent 配置同步到 OpenClaw

## 1. OpenClaw 架构概述

OpenClaw 是一个**自托管的网关**（Self-hosted Gateway），连接聊天应用（WhatsApp、Telegram、Discord 等）到 AI Agent。

核心概念：
- **Gateway**：单一直通进程，管理会话、路由、Channel 连接
- **多 Channel 支持**：一个 Gateway 同时服务多个聊天平台
- **身份绑定**：跨平台的用户身份映射

## 2. 配置文件层次结构

```
~/.openclaw/
├── openclaw.json              # 主配置文件（全局配置）
├── identity/
│   └── device-auth.json       # 设备认证
├── agents/
│   └── {agent_id}/
│       ├── agent/
│       │   ├── models.json       # Agent 级别的模型配置
│       │   └── auth-profiles.json # Agent 级别的认证配置（含 API Key）
│       └── sessions/             # 会话记录
└── workspace-{id}/
    ├── AGENTS.md          # Agent 操作协议
    ├── SOUL.md            # Agent 人设
    ├── USER.md            # 用户信息
    ├── IDENTITY.md        # 身份标识（名称、emoji、头像）
    ├── TOOLS.md           # 工具配置说明
    └── HEARTBEAT.md       # 心跳任务
```

## 3. openclaw.json 核心配置结构

### 3.1 完整结构

```json
{
  "meta": { "lastTouchedVersion": "2026.3.13" },
  "wizard": { "lastRunAt": "...", "lastRunVersion": "..." },

  // 认证配置
  "auth": {
    "profiles": {
      "zai:default": { "provider": "zai", "mode": "api_key" },
      "anthropic:default": { "provider": "anthropic", "mode": "api_key" }
    }
  },

  // 模型提供商配置
  "models": {
    "mode": "merge",
    "providers": {
      "zai": {
        "baseUrl": "https://open.bigmodel.cn/api/coding/paas/v4",
        "api": "openai-completions",
        "models": [
          { "id": "glm-5", "name": "GLM-5", "contextWindow": 204800 }
        ]
      },
      "anthropic": { ... }
    }
  },

  // Agent 配置
  "agents": {
    "defaults": {
      "model": { "primary": "zai/glm-5" },
      "workspace": "/Users/roc/.openclaw/workspace",
      "compaction": { "mode": "safeguard" }
    },
    "list": [ ... ]
  },

  // 工具配置
  "tools": { "profile": "coding" },

  // Channel 配置
  "channels": {
    "telegram": { "enabled": true, "botToken": "...", "dmPolicy": "pairing" },
    "whatsapp": { ... }
  },

  // 其他配置
  "commands": { "native": "auto", "nativeSkills": "auto" },
  "session": { "dmScope": "per-channel-peer" },
  "hooks": { ... },
  "gateway": { "port": 18789, "mode": "local" },
  "skills": { ... }
}
```

### 3.2 agents.list[] Agent 条目详解

```json
{
  "id": "taizi",                                    // Agent 唯一标识
  "workspace": "/Users/roc/.openclaw/workspace-taizi", // Workspace 路径
  "subagents": {
    "allowAgents": ["zhongshu", "hubu"]             // 可调用的子 Agent
  },
  // 以下为可选的 per-agent 覆盖配置：
  "model": {                                        // LLM 模型配置
    "primary": "anthropic/claude-opus-4-6",
    "fallbacks": ["anthropic/claude-sonnet-4-6"]
  },
  "tools": {                                        // 工具权限配置
    "profile": "coding",                            // minimal | coding | messaging | full
    "allow": [],                                    // 允许的工具列表
    "deny": []                                      // 禁止的工具列表
  },
  "sandbox": {                                      // 沙箱配置
    "mode": "non-main",                             // non-main | full-access | restricted | docker
    "workspaceAccess": "read-write",                // none | read-only | read-write | full
    "scope": [],                                    // 允许访问的目录
    "docker": {}                                    // Docker 配置（仅 docker 模式）
  },
  "identity": {                                     // 身份标识
    "name": "太子",                                  // 显示名称
    "emoji": "👑",                                  // Emoji 标识
    "theme": "professional",                        // 主题
    "avatar": "avatars/taizi.png"                   // 头像路径
  }
}
```

## 4. Agent 级别配置文件

### 4.1 models.json（~/.openclaw/agents/{id}/agent/models.json）

Agent 专用的模型提供商配置，覆盖全局配置：

```json
{
  "version": 1,
  "providers": {
    "zai": {
      "baseUrl": "https://open.bigmodel.cn/api/coding/paas/v4",
      "api": "openai-completions",
      "models": [{ "id": "glm-5", "name": "GLM-5", ... }],
      "apiKey": "xxx"
    }
  }
}
```

### 4.2 auth-profiles.json（~/.openclaw/agents/{id}/agent/auth-profiles.json）

Agent 级别的认证配置，包含 API Key：

```json
{
  "version": 1,
  "profiles": {
    "zai:default": {
      "type": "api_key",
      "provider": "zai",
      "key": "xxx"
    }
  },
  "lastGood": { "zai": "zai:default" },
  "usageStats": { ... }
}
```

## 5. Workspace 配置文件

| 文件 | 用途 | 内容示例 |
|------|------|---------|
| AGENTS.md | Agent 操作协议 | 工作流程、协作规则 |
| SOUL.md | Agent 人设 | 性格、说话风格、专业领域 |
| USER.md | 用户信息 | 用户偏好、背景信息 |
| IDENTITY.md | 身份标识 | 名称、Creature、Emoji、Avatar |
| TOOLS.md | 工具配置说明 | 环境特定的工具配置 |
| HEARTBEAT.md | 心跳任务 | 定期检查的任务列表 |

## 6. Channel 配置

### 6.1 Telegram 配置

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "xxx",                              // Bot Token（从 BotFather 获取）
      "dmPolicy": "pairing",                          // pairing | allowlist | open | disabled
      "allowFrom": [],                                // DM 允许列表（用户 ID）
      "groupPolicy": "allowlist",                     // open | allowlist | disabled
      "groupAllowFrom": [],                           // 群组发送者允许列表
      "groups": {                                     // 群组配置
        "-1001234567890": {
          "requireMention": false,
          "allowFrom": ["8734062810"]
        }
      },
      "streaming": "partial",                         // off | partial | block
      "mediaMaxMb": 100
    }
  }
}
```

### 6.2 WhatsApp 配置

```json
{
  "channels": {
    "whatsapp": {
      "enabled": true,
      "allowFrom": ["+15555550123"],
      "groups": { "*": { "requireMention": true } }
    }
  }
}
```

## 7. 当前 SOP Engine 实现分析

### 7.1 当前 _register_to_openclaw() 方法

```python
def _register_to_openclaw(self, agent: Agent) -> None:
    config = self._read_openclaw_config()

    if "agents" not in config:
        config["agents"] = {}
    if "list" not in config["agents"]:
        config["agents"]["list"] = []

    group_chat_config = agent.group_chat_config or {}
    allow_agents = group_chat_config.get("mentionPatterns", [])

    agent_entry = {
        "id": agent.id,
        "workspace": agent.workspace_path,
        "subagents": { "allowAgents": allow_agents }
    }

    # ... 更新或添加逻辑
```

### 7.2 问题：配置不完整

当前实现只写入了：
- ✅ `id` - Agent ID
- ✅ `workspace` - Workspace 路径
- ✅ `subagents.allowAgents` - 子 Agent 列表

**缺失的配置**：
- ❌ `model` - LLM 模型配置（primary, fallbacks）
- ❌ `tools` - 工具权限配置（profile, allow, deny）
- ❌ `sandbox` - 沙箱配置（mode, workspaceAccess, scope）
- ❌ `identity` - 身份标识（name, emoji）
- ❌ Agent 级别的 `models.json` 文件
- ❌ Agent 级别的 `auth-profiles.json` 文件

## 8. 配置优先级

```
agents.list[{id}].{field} > agents.defaults.{field} > 全局默认值
```

示例：
- `agents.list["taizi"].model` > `agents.defaults.model` > 内置默认
- `agents.list["taizi"].tools` > `tools` (全局)

## 9. 关键发现

1. **模型配置**：可以在 `agents.list[].model` 中配置，也可以在 Agent 级别的 `models.json` 中配置提供商
2. **API Key 存储**：敏感信息存储在 `~/.openclaw/agents/{id}/agent/auth-profiles.json`
3. **Channel 独立管理**：Channel 配置通常需要通过 `openclaw onboard` 或手动配置
4. **Workspace 文件**：Workspace 中的 MD 文件用于 Agent 运行时读取，不是配置注册

## 10. 参考资料

- OpenClaw 官方文档：https://docs.openclaw.ai/
- Telegram Channel 配置：https://docs.openclaw.ai/channels/telegram
- 模型提供商：https://docs.openclaw.ai/providers/models
- Anthropic 配置：https://docs.openclaw.ai/providers/anthropic
