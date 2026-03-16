# Agent 配置编辑器设计文档

> 创建日期: 2026-03-16
> 状态: 已确认

## 概述

增强 Agent 管理模块，提供完整的 Agent 配置编辑能力。采用**混合模式**：常用配置使用表单编辑，高级配置使用 JSON 编辑器。

## 设计原则

1. **表单优先** - 常用配置使用表单，降低出错率
2. **JSON 灵活** - 高级配置使用 JSON 编辑器，支持完整控制
3. **双向同步** - 表单与 JSON 编辑器实时同步
4. **即时校验** - 输入时校验，保存前验证

## 页面结构

```
Agent 管理页面
├── Agent 列表（现有）
│   └── 操作：详情 | 编辑 | 同步 | 删除
│
└── Agent 编辑对话框（新增/增强）
    ├── 基本信息 Tab（表单）
    ├── LLM 配置 Tab（表单 + 高级 JSON）
    ├── 沙箱配置 Tab（表单 + 高级 JSON）
    ├── 工具配置 Tab（表单 + 高级 JSON）
    └── 高级配置 Tab（纯 JSON 编辑器）
```

## Tab 详情

### 1. 基本信息 Tab

| 字段 | 类型 | 说明 |
|-----|------|------|
| 名称 | text | Agent 显示名称 |
| 工作目录 | text | 只读，自动生成 |
| 状态 | toggle | 激活/停用 |

### 2. LLM 配置 Tab

**表单区域：**

| 字段 | 类型 | 说明 |
|-----|------|------|
| API 端点 | select + text | 预设或自定义 URL |
| API 密钥 | password | 密文显示 |
| 主模型 | select | primary 模型选择 |
| 备用模型 | list | fallbacks 列表，可添加/删除 |

**API 端点预设：**
- Anthropic: `https://api.anthropic.com`
- OpenAI: `https://api.openai.com/v1`
- Azure: 用户自定义
- 自定义: 用户输入

**模型选项：**
- `claude-3-5-sonnet` (推荐)
- `claude-3-opus`
- `claude-3-sonnet`
- `claude-3-haiku`
- `claude-sonnet-4-20250514`
- `claude-opus-4-20250514`

**高级 JSON 配置：**
```json
{
  "base_url": "https://api.anthropic.com",
  "api_key": "sk-ant-xxx",
  "primary": "claude-3-5-sonnet",
  "fallbacks": ["claude-3-opus"]
}
```

### 3. 沙箱配置 Tab

**表单区域：**

| 字段 | 类型 | 说明 |
|-----|------|------|
| 沙箱模式 | select | Non-Main / Full-Access / Restricted / Docker |
| 工作区访问 | select | None / Read-Only / Read-Write / Full |
| 作用域 | list | 路径列表 |

**模式说明：**
- **Non-Main**: 非主进程隔离（推荐，安全且高效）
- **Full-Access**: 完全访问权限（仅限信任环境）
- **Restricted**: 受限模式，仅允许白名单操作
- **Docker**: 容器隔离，最安全但开销最大

**Docker 高级配置（仅 Docker 模式）：**

| 字段 | 类型 | 说明 | 默认值 |
|-----|------|------|--------|
| image | string | Docker 镜像 | `ubuntu:22.04` |
| memory | string | 内存限制 | `2g` |
| cpu_count | number | CPU 核心数 | `1` |
| timeout | string | 执行超时 | `30m` |
| network | string | 网络模式 | `bridge` |
| volumes | string[] | 挂载卷 | `[]` |
| environment | object | 环境变量 | `{}` |

**高级 JSON 配置：**
```json
{
  "mode": "non-main",
  "workspaceAccess": "read-write",
  "scope": ["/workspace"],
  "docker": {
    "image": "ubuntu:22.04",
    "memory": "2g",
    "cpu_count": 1,
    "timeout": "30m",
    "network": "bridge",
    "volumes": [],
    "environment": {}
  }
}
```

### 4. 工具配置 Tab

**表单区域：**

| 字段 | 类型 | 说明 |
|-----|------|------|
| 工具配置文件 | select | 预设配置选择 |
| 允许的工具 | tags | 多选标签 |
| 禁止的工具 | tags | 多选标签 |
| 执行命令白名单 | text | 逗号分隔（仅自定义模式） |

**预设配置文件：**
- **默认配置**: 允许常用工具 (Bash, Read, Edit, Glob, Grep, Write)
- **受限配置**: 仅允许读取类工具 (Read, Glob, Grep)
- **完全访问**: 允许所有工具
- **自定义**: 手动配置 allow/deny/exec

**高级 JSON 配置：**
```json
{
  "profile": "default",
  "allow": ["Bash", "Read", "Edit", "Glob", "Grep", "Write"],
  "deny": ["WebFetch", "Agent"],
  "exec": ["git", "npm", "pip", "python"]
}
```

### 5. 高级配置 Tab

采用纯 JSON 编辑器形式，包含以下配置：

**心跳配置 (heartbeat):**
| 字段 | 类型 | 说明 |
|-----|------|------|
| every | string | 心跳间隔 (30m, 1h, 5m) |
| target | string | 心跳目标文件 |

**记忆搜索配置 (memorySearch):**
| 字段 | 类型 | 说明 |
|-----|------|------|
| enabled | boolean | 是否启用 |
| provider | string | 向量数据库提供商 |
| model | string | 嵌入模型 |

**群聊配置 (groupChat):**
| 字段 | 类型 | 说明 |
|-----|------|------|
| mentionPatterns | string[] | @ 提及正则模式 |

**完整 JSON 示例：**
```json
{
  "heartbeat": {
    "every": "30m",
    "target": "heartbeat.md"
  },
  "memorySearch": {
    "enabled": true,
    "provider": "openai",
    "model": "text-embedding-3-small"
  },
  "groupChat": {
    "mentionPatterns": ["@\\w+", "@[a-z]+"]
  }
}
```

## 交互流程

### 创建 Agent

```
1. 用户点击 "创建 Agent"
2. 弹出对话框，输入基本信息（名称）
3. 可选：配置 LLM/沙箱/工具（或使用默认值）
4. 点击 "创建" → POST /api/agents
5. 成功：关闭对话框，刷新列表，显示成功 Toast
   失败：显示错误信息
```

### 编辑 Agent

```
1. 用户点击 Agent 列表中的 "编辑" 按钮
2. 弹出编辑对话框，加载当前 Agent 配置
3. 用户修改配置（表单或 JSON）
4. 点击 "保存" → PATCH /api/agents/{id}
5. 成功：关闭对话框，刷新列表，显示成功 Toast
   失败：显示错误信息
```

### 表单与 JSON 同步

```
表单修改 → 自动同步到 JSON 编辑器
JSON 编辑器修改 → 解析后更新表单（格式正确时）
JSON 格式错误 → 显示错误提示，不更新表单
```

## 组件结构

```
components/agents/
├── agent-list.tsx              # 现有，添加编辑按钮
├── create-agent-dialog.tsx     # 增强，支持完整配置
├── edit-agent-dialog.tsx       # 新增，编辑对话框
├── agent-form/
│   ├── index.tsx               # 表单主组件
│   ├── basic-info-tab.tsx      # 基本信息表单
│   ├── llm-config-tab.tsx      # LLM 配置表单
│   ├── sandbox-config-tab.tsx  # 沙箱配置表单
│   ├── tools-config-tab.tsx    # 工具配置表单
│   ├── advanced-config-tab.tsx # 高级配置 JSON 编辑器
│   └── json-editor.tsx         # 可复用的 JSON 编辑器组件
```

## API 依赖

后端 API 已支持：

| 端点 | 方法 | 用途 |
|-----|------|------|
| `/api/agents` | GET | 获取 Agent 列表 |
| `/api/agents` | POST | 创建 Agent |
| `/api/agents/{id}` | GET | 获取 Agent 详情 |
| `/api/agents/{id}` | PATCH | 更新 Agent 配置 |
| `/api/agents/{id}` | DELETE | 删除 Agent |
| `/api/agents/{id}/sync` | POST | 同步到 OpenClaw |

## 验收标准

1. ✅ 用户可通过表单配置 LLM（包括 base_url, api_key, 模型）
2. ✅ 用户可通过表单配置沙箱（包括 Docker 高级选项）
3. ✅ 用户可通过表单配置工具（允许/禁止列表）
4. ✅ 用户可通过 JSON 编辑器修改任意配置
5. ✅ 表单与 JSON 编辑器双向同步
6. ✅ 保存时校验配置格式
7. ✅ 错误时显示友好提示
