# Session 配置详细设计

## 文档信息

| 项目 | 值 |
|------|-----|
| 版本 | v1.0 |
| 日期 | 2026-03-18 |
| 状态 | Draft |
| 父文档 | openclaw-config-alignment-design.md |

---

## 1. 概述

### 1.1 Session 配置的作用

Session 配置控制 OpenClaw 如何：
1. **隔离会话** - 不同用户/群组/频道的对话如何隔离
2. **重置会话** - 会话何时自动重置（每日/空闲）
3. **维护会话** - 会话存储的清理和轮转策略
4. **路由会话** - 多渠道/多账号场景下的会话映射

### 1.2 设计目标

1. **安全性**：支持安全 DM 模式，防止多用户间信息泄露
2. **灵活性**：支持按类型、按渠道的细粒度重置策略
3. **可维护性**：自动化的会话存储维护和磁盘预算
4. **兼容性**：与 OpenClaw 配置完全对齐

---

## 2. 数据模型设计

### 2.1 完整模型定义

```python
# backend/app/models/session_config.py

from datetime import datetime
from typing import Any, Literal
from pydantic import Field, field_validator
from .base import Base

# ==================== 类型定义 ====================

DmScope = Literal["main", "per-peer", "per-channel-peer", "per-account-channel-peer"]
ResetMode = Literal["daily", "idle"]
MaintenanceMode = Literal["warn", "enforce"]
ChatType = Literal["direct", "group", "thread"]

# ==================== 重置配置 ====================

class SessionResetConfig(Base):
    """会话重置配置

    对应 OpenClaw: session.reset

    Examples:
        # 每日 4:00 AM 重置
        {"mode": "daily", "atHour": 4}

        # 空闲 2 小时重置
        {"mode": "idle", "idleMinutes": 120}

        # 每日重置，同时设置空闲超时（先到期者生效）
        {"mode": "daily", "atHour": 4, "idleMinutes": 120}
    """
    mode: ResetMode = "daily"
    at_hour: int = Field(default=4, ge=0, le=23, description="每日重置时间（0-23，本地时区）")
    idle_minutes: int | None = Field(default=None, ge=1, description="空闲超时分钟数")

    # OpenClaw 同步时转换为 camelCase
    def to_openclaw(self) -> dict:
        result = {"mode": self.mode}
        if self.mode == "daily" or self.at_hour != 4:
            result["atHour"] = self.at_hour
        if self.idle_minutes is not None:
            result["idleMinutes"] = self.idle_minutes
        return result

class SessionResetByTypeConfig(Base):
    """按会话类型的重置配置

    对应 OpenClaw: session.resetByType

    可为不同会话类型设置不同的重置策略：
    - direct: 私聊
    - group: 群组
    - thread: 话题/线程（Slack threads, Discord threads, Telegram topics）
    """
    direct: SessionResetConfig | None = None
    group: SessionResetConfig | None = None
    thread: SessionResetConfig | None = None

    def to_openclaw(self) -> dict:
        result = {}
        if self.direct:
            result["direct"] = self.direct.to_openclaw()
        if self.group:
            result["group"] = self.group.to_openclaw()
        if self.thread:
            result["thread"] = self.thread.to_openclaw()
        return result

class SessionResetByChannelConfig(Base):
    """按渠道的重置配置

    对应 OpenClaw: session.resetByChannel

    为特定渠道设置不同的重置策略，优先级高于 resetByType。
    """
    # 使用 dict 而非具体字段，因为渠道名是动态的
    channels: dict[str, SessionResetConfig] = {}

    def to_openclaw(self) -> dict:
        return {k: v.to_openclaw() for k, v in self.channels.items()}

# ==================== 维护配置 ====================

class SessionMaintenanceConfig(Base):
    """会话维护配置

    对应 OpenClaw: session.maintenance

    控制 sessions.json 和 transcript 文件的自动维护。
    """
    mode: MaintenanceMode = "warn"
    prune_after: str = "30d"  # 持续时间字符串
    max_entries: int = Field(default=500, ge=1, description="最大会话条目数")
    rotate_bytes: str = "10mb"  # 文件大小字符串
    reset_archive_retention: str | bool = "30d"  # 重置归档保留时间，false 禁用
    max_disk_bytes: str | None = None  # 磁盘预算
    high_water_bytes: str | None = None  # 清理目标，默认 maxDiskBytes 的 80%

    def to_openclaw(self) -> dict:
        result = {
            "mode": self.mode,
            "pruneAfter": self.prune_after,
            "maxEntries": self.max_entries,
            "rotateBytes": self.rotate_bytes,
        }
        if self.reset_archive_retention is not None:
            result["resetArchiveRetention"] = self.reset_archive_retention
        if self.max_disk_bytes:
            result["maxDiskBytes"] = self.max_disk_bytes
        if self.high_water_bytes:
            result["highWaterBytes"] = self.high_water_bytes
        return result

# ==================== 线程绑定配置 ====================

class SessionThreadBindingsConfig(Base):
    """线程绑定配置

    对应 OpenClaw: session.threadBindings

    控制线程绑定会话功能。
    """
    enabled: bool = True
    idle_hours: int = Field(default=24, ge=0, description="不活动自动解绑小时数，0 禁用")
    max_age_hours: int = Field(default=0, ge=0, description="硬性最大存活小时数，0 禁用")

    def to_openclaw(self) -> dict:
        return {
            "enabled": self.enabled,
            "idleHours": self.idle_hours,
            "maxAgeHours": self.max_age_hours,
        }

# ==================== 发送策略配置 ====================

class SendPolicyMatch(Base):
    """发送策略匹配规则"""
    channel: str | None = None
    chat_type: str | None = None  # direct | group | channel
    key_prefix: str | None = None
    raw_key_prefix: str | None = None

class SendPolicyRule(Base):
    """发送策略规则"""
    action: Literal["allow", "deny"]
    match: SendPolicyMatch

class SessionSendPolicyConfig(Base):
    """发送策略配置

    对应 OpenClaw: session.sendPolicy

    按会话类型阻止发送。
    """
    rules: list[SendPolicyRule] = []
    default: Literal["allow", "deny"] = "allow"

    def to_openclaw(self) -> dict:
        return {
            "rules": [
                {
                    "action": rule.action,
                    "match": rule.match.model_dump(exclude_none=True)
                }
                for rule in self.rules
            ],
            "default": self.default,
        }

# ==================== Agent 间通信配置 ====================

class SessionAgentToAgentConfig(Base):
    """Agent 间通信配置

    对应 OpenClaw: session.agentToAgent
    """
    max_ping_pong_turns: int = Field(default=5, ge=0, description="最大乒乓交互轮数")

    def to_openclaw(self) -> dict:
        return {"maxPingPongTurns": self.max_ping_pong_turns}

# ==================== 主配置模型 ====================

class SessionConfig(Base):
    """Session 配置模型

    对应 OpenClaw: session.*

    完整的会话管理配置，包括：
    - DM 隔离策略
    - 跨渠道身份映射
    - 会话重置策略
    - 存储维护
    - 线程绑定
    - 发送策略
    """

    # === DM 隔离策略 ===
    scope: str = "per-sender"  # 保留字段，OpenClaw 使用 dmScope
    dm_scope: DmScope = Field(
        default="main",
        description=(
            "DM 隔离策略："
            "main=所有 DM 共享主会话，"
            "per-peer=按发送者隔离，"
            "per-channel-peer=按渠道+发送者隔离（推荐多用户收件箱），"
            "per-account-channel-peer=按账号+渠道+发送者隔离（推荐多账号收件箱）"
        )
    )

    # === 跨渠道身份映射 ===
    identity_links: dict[str, list[str]] = Field(
        default={},
        description=(
            "将规范 ID 映射到提供者前缀的对等 ID，用于跨渠道会话共享。"
            "例如：{'alice': ['telegram:123456789', 'discord:987654321012345678']}"
        )
    )

    # === 重置策略 ===
    reset: SessionResetConfig | None = None
    reset_by_type: SessionResetByTypeConfig | None = None
    reset_by_channel: SessionResetByChannelConfig | None = None
    reset_triggers: list[str] = ["/new", "/reset"]

    # === 存储配置 ===
    store: str = "~/.openclaw/agents/{agentId}/sessions/sessions.json"
    main_key: str = "main"
    parent_fork_max_tokens: int = Field(
        default=100000,
        ge=0,
        description="创建线程会话时父会话最大 token 数，超限则启动新会话。0 禁用限制。"
    )

    # === 维护配置 ===
    maintenance: SessionMaintenanceConfig | None = None

    # === 线程绑定 ===
    thread_bindings: SessionThreadBindingsConfig | None = None

    # === Agent 间通信 ===
    agent_to_agent: SessionAgentToAgentConfig | None = None

    # === 发送策略 ===
    send_policy: SessionSendPolicyConfig | None = None

    # === 元数据 ===
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # ==================== 序列化方法 ====================

    def to_openclaw(self) -> dict:
        """转换为 OpenClaw 配置格式（camelCase）"""
        result: dict[str, Any] = {}

        # 基础字段
        result["scope"] = self.scope
        result["dmScope"] = self.dm_scope

        # 身份映射
        if self.identity_links:
            result["identityLinks"] = self.identity_links

        # 重置策略
        if self.reset:
            result["reset"] = self.reset.to_openclaw()
        if self.reset_by_type:
            result["resetByType"] = self.reset_by_type.to_openclaw()
        if self.reset_by_channel:
            result["resetByChannel"] = self.reset_by_channel.to_openclaw()

        # 重置触发器
        if self.reset_triggers:
            result["resetTriggers"] = self.reset_triggers

        # 存储配置
        result["store"] = self.store
        result["mainKey"] = self.main_key
        result["parentForkMaxTokens"] = self.parent_fork_max_tokens

        # 维护配置
        if self.maintenance:
            result["maintenance"] = self.maintenance.to_openclaw()

        # 线程绑定
        if self.thread_bindings:
            result["threadBindings"] = self.thread_bindings.to_openclaw()

        # Agent 间通信
        if self.agent_to_agent:
            result["agentToAgent"] = self.agent_to_agent.to_openclaw()

        # 发送策略
        if self.send_policy:
            result["sendPolicy"] = self.send_policy.to_openclaw()

        return result

    @classmethod
    def from_openclaw(cls, data: dict) -> "SessionConfig":
        """从 OpenClaw 配置格式解析"""
        # 解析嵌套配置
        reset = None
        if "reset" in data:
            reset = SessionResetConfig(
                mode=data["reset"].get("mode", "daily"),
                at_hour=data["reset"].get("atHour", 4),
                idle_minutes=data["reset"].get("idleMinutes"),
            )

        reset_by_type = None
        if "resetByType" in data:
            rbt = data["resetByType"]
            reset_by_type = SessionResetByTypeConfig(
                direct=SessionResetConfig(**rbt["direct"]) if "direct" in rbt else None,
                group=SessionResetConfig(**rbt["group"]) if "group" in rbt else None,
                thread=SessionResetConfig(**rbt["thread"]) if "thread" in rbt else None,
            )

        reset_by_channel = None
        if "resetByChannel" in data:
            channels = {
                k: SessionResetConfig(
                    mode=v.get("mode", "daily"),
                    at_hour=v.get("atHour", 4),
                    idle_minutes=v.get("idleMinutes"),
                )
                for k, v in data["resetByChannel"].items()
            }
            reset_by_channel = SessionResetByChannelConfig(channels=channels)

        maintenance = None
        if "maintenance" in data:
            m = data["maintenance"]
            maintenance = SessionMaintenanceConfig(
                mode=m.get("mode", "warn"),
                prune_after=m.get("pruneAfter", "30d"),
                max_entries=m.get("maxEntries", 500),
                rotate_bytes=m.get("rotateBytes", "10mb"),
                reset_archive_retention=m.get("resetArchiveRetention", "30d"),
                max_disk_bytes=m.get("maxDiskBytes"),
                high_water_bytes=m.get("highWaterBytes"),
            )

        thread_bindings = None
        if "threadBindings" in data:
            tb = data["threadBindings"]
            thread_bindings = SessionThreadBindingsConfig(
                enabled=tb.get("enabled", True),
                idle_hours=tb.get("idleHours", 24),
                max_age_hours=tb.get("maxAgeHours", 0),
            )

        agent_to_agent = None
        if "agentToAgent" in data:
            agent_to_agent = SessionAgentToAgentConfig(
                max_ping_pong_turns=data["agentToAgent"].get("maxPingPongTurns", 5)
            )

        send_policy = None
        if "sendPolicy" in data:
            sp = data["sendPolicy"]
            rules = [
                SendPolicyRule(
                    action=r["action"],
                    match=SendPolicyMatch(**r.get("match", {}))
                )
                for r in sp.get("rules", [])
            ]
            send_policy = SessionSendPolicyConfig(
                rules=rules,
                default=sp.get("default", "allow")
            )

        return cls(
            scope=data.get("scope", "per-sender"),
            dm_scope=data.get("dmScope", "main"),
            identity_links=data.get("identityLinks", {}),
            reset=reset,
            reset_by_type=reset_by_type,
            reset_by_channel=reset_by_channel,
            reset_triggers=data.get("resetTriggers", ["/new", "/reset"]),
            store=data.get("store", "~/.openclaw/agents/{agentId}/sessions/sessions.json"),
            main_key=data.get("mainKey", "main"),
            parent_fork_max_tokens=data.get("parentForkMaxTokens", 100000),
            maintenance=maintenance,
            thread_bindings=thread_bindings,
            agent_to_agent=agent_to_agent,
            send_policy=send_policy,
        )
```

### 2.2 与 Agent 模型的集成

```python
# backend/app/models/agent.py (更新)

from .session_config import SessionConfig

class Agent(Base):
    """Agent 配置模型"""
    id: str
    name: str
    workspace_path: str

    # ... 其他现有字段 ...

    # === 新增：Session 配置 ===
    session_config: SessionConfig | None = None

    # ... 其他字段 ...
```

---

## 3. API 设计

### 3.1 Session 配置 API

```python
# backend/app/api/agents.py (增强)

@router.get("/{agent_id}/session")
async def get_session_config(request: Request, agent_id: str) -> dict:
    """获取 Agent 的 Session 配置"""
    service = request.app.state.agent_service
    agent = service.get_agent(agent_id)

    if not agent.session_config:
        # 返回默认配置
        return {"session": SessionConfig().to_openclaw()}

    return {"session": agent.session_config.to_openclaw()}

@router.patch("/{agent_id}/session")
async def update_session_config(
    request: Request,
    agent_id: str,
    data: dict
) -> dict:
    """更新 Agent 的 Session 配置（部分更新）"""
    service = request.app.state.agent_service
    agent = service.get_agent(agent_id)

    # 解析现有配置或创建新配置
    existing = agent.session_config or SessionConfig()

    # 部分更新逻辑
    if "dmScope" in data:
        existing.dm_scope = data["dmScope"]
    if "identityLinks" in data:
        existing.identity_links = data["identityLinks"]
    if "reset" in data:
        existing.reset = SessionResetConfig.from_openclaw({"reset": data["reset"]}).reset
    if "resetByType" in data:
        existing.reset_by_type = SessionResetByTypeConfig.from_openclaw(
            {"resetByType": data["resetByType"]}
        ).reset_by_type
    if "maintenance" in data:
        existing.maintenance = SessionMaintenanceConfig.from_openclaw(
            {"maintenance": data["maintenance"]}
        ).maintenance
    if "threadBindings" in data:
        existing.thread_bindings = SessionThreadBindingsConfig.from_openclaw(
            {"threadBindings": data["threadBindings"]}
        ).thread_bindings
    if "sendPolicy" in data:
        existing.send_policy = SessionSendPolicyConfig.from_openclaw(
            {"sendPolicy": data["sendPolicy"]}
        ).send_policy

    # 更新 Agent
    updated_agent = service.update_agent(
        agent_id,
        session_config=existing
    )

    return {"session": updated_agent.session_config.to_openclaw()}
```

### 3.2 Session 管理命令 API

```python
# backend/app/api/sessions.py (新建)

from fastapi import APIRouter, Request, HTTPException

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

@router.get("")
async def list_sessions(
    request: Request,
    agent_id: str | None = None,
    active_minutes: int | None = None
) -> list[dict]:
    """列出会话

    对应 OpenClaw: openclaw sessions --json
    """
    # 这里需要与 OpenClaw Gateway 通信
    # 暂时返回模拟数据
    pass

@router.post("/cleanup")
async def cleanup_sessions(
    request: Request,
    agent_id: str,
    dry_run: bool = True,
    enforce: bool = False
) -> dict:
    """清理会话

    对应 OpenClaw: openclaw sessions cleanup
    """
    pass

@router.delete("/{session_key}")
async def reset_session(
    request: Request,
    agent_id: str,
    session_key: str
) -> dict:
    """重置指定会话"""
    pass
```

---

## 4. 同步逻辑设计

### 4.1 Agent 服务更新

```python
# backend/app/services/agent_service.py (增强)

class AgentService:
    # Session 配置受管字段
    MANAGED_SESSION_FIELDS = {
        "scope", "dmScope", "identityLinks", "reset", "resetByType",
        "resetByChannel", "resetTriggers", "store", "mainKey",
        "parentForkMaxTokens", "maintenance", "threadBindings",
        "agentToAgent", "sendPolicy"
    }

    def _agent_to_openclaw_format(self, agent: Agent) -> dict:
        """转换为 OpenClaw 格式"""
        entry = super()._agent_to_openclaw_format(agent)

        # 添加 Session 配置
        if agent.session_config:
            entry["session"] = agent.session_config.to_openclaw()

        return entry

    def update_agent_session(
        self,
        agent_id: str,
        session_config: SessionConfig
    ) -> Agent:
        """更新 Agent 的 Session 配置"""
        agent = self.get_agent(agent_id)

        updated_agent = Agent(
            **agent.model_dump(),
            session_config=session_config,
            updated_at=datetime.utcnow(),
        )

        self._agents[agent_id] = updated_agent
        self._register_to_openclaw(updated_agent)

        return updated_agent
```

---

## 5. 前端设计

### 5.1 Session 配置表单组件

```typescript
// frontend/lib/types/session.ts

export type DmScope = 'main' | 'per-peer' | 'per-channel-peer' | 'per-account-channel-peer';
export type ResetMode = 'daily' | 'idle';
export type MaintenanceMode = 'warn' | 'enforce';

export interface SessionResetConfig {
  mode: ResetMode;
  at_hour?: number;
  idle_minutes?: number;
}

export interface SessionResetByTypeConfig {
  direct?: SessionResetConfig;
  group?: SessionResetConfig;
  thread?: SessionResetConfig;
}

export interface SessionMaintenanceConfig {
  mode: MaintenanceMode;
  prune_after?: string;
  max_entries?: number;
  rotate_bytes?: string;
  reset_archive_retention?: string | boolean;
  max_disk_bytes?: string;
  high_water_bytes?: string;
}

export interface SessionThreadBindingsConfig {
  enabled?: boolean;
  idle_hours?: number;
  max_age_hours?: number;
}

export interface SessionConfig {
  scope?: string;
  dm_scope: DmScope;
  identity_links?: Record<string, string[]>;
  reset?: SessionResetConfig;
  reset_by_type?: SessionResetByTypeConfig;
  reset_by_channel?: Record<string, SessionResetConfig>;
  reset_triggers?: string[];
  store?: string;
  main_key?: string;
  parent_fork_max_tokens?: number;
  maintenance?: SessionMaintenanceConfig;
  thread_bindings?: SessionThreadBindingsConfig;
  agent_to_agent?: { max_ping_pong_turns?: number };
  send_policy?: {
    rules?: Array<{
      action: 'allow' | 'deny';
      match: {
        channel?: string;
        chat_type?: string;
      };
    }>;
    default?: 'allow' | 'deny';
  };
}
```

### 5.2 表单组件结构

```
frontend/components/agents/session-config-form/
├── index.tsx                    # 主表单容器
├── dm-scope-section.tsx         # DM 隔离策略
├── identity-links-section.tsx   # 跨渠道身份映射
├── reset-policy-section.tsx     # 重置策略
│   ├── daily-reset-config.tsx   # 每日重置
│   ├── idle-reset-config.tsx    # 空闲重置
│   └── per-type-override.tsx    # 按类型覆盖
├── maintenance-section.tsx      # 维护配置
├── thread-bindings-section.tsx  # 线程绑定
└── advanced-section.tsx         # 高级配置（发送策略等）
```

### 5.3 DM 隔离策略 UI

```tsx
// frontend/components/agents/session-config-form/dm-scope-section.tsx

import { useForm } from 'react-hook-form';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { InfoIcon, AlertTriangleIcon } from 'lucide-react';

const DM_SCOPE_OPTIONS = [
  {
    value: 'main',
    label: '共享主会话',
    description: '所有 DM 共享同一个会话，适合单人使用',
    warning: null,
  },
  {
    value: 'per-peer',
    label: '按用户隔离',
    description: '按发送者 ID 隔离，同一用户跨渠道共享',
    warning: null,
  },
  {
    value: 'per-channel-peer',
    label: '按渠道+用户隔离',
    description: '按渠道 + 发送者隔离，推荐用于多用户收件箱',
    warning: '推荐用于多用户场景',
  },
  {
    value: 'per-account-channel-peer',
    label: '按账号+渠道+用户隔离',
    description: '按账号 + 渠道 + 发送者隔离，推荐用于多账号收件箱',
    warning: '推荐用于多账号场景',
  },
];

export function DmScopeSection({ form }) {
  const dmScope = form.watch('dm_scope');

  const selectedOption = DM_SCOPE_OPTIONS.find(o => o.value === dmScope);

  return (
    <Card>
      <CardHeader>
        <CardTitle>DM 隔离策略</CardTitle>
        <CardDescription>
          控制私聊消息如何隔离，防止多用户间信息泄露
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <Select
          value={dmScope}
          onValueChange={(value) => form.setValue('dm_scope', value)}
        >
          <SelectTrigger>
            <SelectValue placeholder="选择 DM 隔离策略" />
          </SelectTrigger>
          <SelectContent>
            {DM_SCOPE_OPTIONS.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                <div className="flex flex-col">
                  <span>{option.label}</span>
                  <span className="text-xs text-muted-foreground">
                    {option.description}
                  </span>
                </div>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        {selectedOption && (
          <Alert variant={selectedOption.warning ? 'default' : 'info'}>
            {selectedOption.warning ? (
              <AlertTriangleIcon className="h-4 w-4" />
            ) : (
              <InfoIcon className="h-4 w-4" />
            )}
            <AlertDescription>
              {selectedOption.warning || selectedOption.description}
            </AlertDescription>
          </Alert>
        )}

        {dmScope === 'main' && (
          <Alert variant="destructive">
            <AlertTriangleIcon className="h-4 w-4" />
            <AlertDescription>
              <strong>安全警告：</strong>
              如果多个用户可以 DM 你的 Agent，所有用户将共享同一会话上下文。
              建议使用 "按渠道+用户隔离" 以保护用户隐私。
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}
```

### 5.4 重置策略 UI

```tsx
// frontend/components/agents/session-config-form/reset-policy-section.tsx

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export function ResetPolicySection({ form }) {
  const resetMode = form.watch('reset.mode');
  const hasIdleReset = form.watch('reset.idle_minutes') !== null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>会话重置策略</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <Tabs value={resetMode} onValueChange={(v) => form.setValue('reset.mode', v)}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="daily">每日重置</TabsTrigger>
            <TabsTrigger value="idle">空闲重置</TabsTrigger>
          </TabsList>

          <TabsContent value="daily" className="space-y-4">
            <div className="flex items-center gap-4">
              <Label>重置时间（本地时区）</Label>
              <Input
                type="number"
                min={0}
                max={23}
                {...form.register('reset.at_hour', { valueAsNumber: true })}
                className="w-20"
              />
              <span className="text-muted-foreground">:00 AM</span>
            </div>
          </TabsContent>

          <TabsContent value="idle" className="space-y-4">
            <div className="flex items-center gap-4">
              <Label>空闲超时（分钟）</Label>
              <Input
                type="number"
                min={1}
                {...form.register('reset.idle_minutes', { valueAsNumber: true })}
                className="w-32"
              />
            </div>
          </TabsContent>
        </Tabs>

        {/* 同时启用两种策略 */}
        {resetMode === 'daily' && (
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>同时启用空闲超时</Label>
              <p className="text-sm text-muted-foreground">
                每日重置和空闲超时先到期者生效
              </p>
            </div>
            <Switch
              checked={hasIdleReset}
              onCheckedChange={(checked) => {
                form.setValue('reset.idle_minutes', checked ? 120 : null);
              }}
            />
          </div>
        )}

        {hasIdleReset && resetMode === 'daily' && (
          <div className="flex items-center gap-4">
            <Label>空闲超时（分钟）</Label>
            <Input
              type="number"
              min={1}
              {...form.register('reset.idle_minutes', { valueAsNumber: true })}
              className="w-32"
            />
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

---

## 6. 配置预设

### 6.1 单用户预设

```python
SINGLE_USER_PRESET = SessionConfig(
    dm_scope="main",  # 所有 DM 共享
    reset=SessionResetConfig(mode="daily", at_hour=4),
    maintenance=SessionMaintenanceConfig(mode="warn"),
)
```

### 6.2 多用户收件箱预设

```python
MULTI_USER_INBOX_PRESET = SessionConfig(
    dm_scope="per-channel-peer",  # 按渠道+用户隔离
    reset=SessionResetConfig(
        mode="daily",
        at_hour=4,
        idle_minutes=240  # 4 小时空闲也重置
    ),
    reset_by_type=SessionResetByTypeConfig(
        direct=SessionResetConfig(mode="idle", idle_minutes=480),  # DM 8小时
        group=SessionResetConfig(mode="idle", idle_minutes=120),   # 群组 2小时
    ),
    maintenance=SessionMaintenanceConfig(
        mode="enforce",
        prune_after="14d",
        max_entries=1000,
    ),
)
```

### 6.3 高流量预设

```python
HIGH_TRAFFIC_PRESET = SessionConfig(
    dm_scope="per-account-channel-peer",
    reset=SessionResetConfig(mode="idle", idle_minutes=60),
    maintenance=SessionMaintenanceConfig(
        mode="enforce",
        prune_after="7d",
        max_entries=2000,
        max_disk_bytes="2gb",
        high_water_bytes="1.6gb",
    ),
    thread_bindings=SessionThreadBindingsConfig(
        enabled=True,
        idle_hours=12,
        max_age_hours=72,
    ),
)
```

---

## 7. 验证规则

### 7.1 后端验证

```python
# backend/app/validators/session.py

from pydantic import field_validator, model_validator

class SessionConfig(Base):
    # ... 字段定义 ...

    @field_validator('dm_scope')
    @classmethod
    def validate_dm_scope_for_multi_user(cls, v: str, info) -> str:
        """如果启用了多用户，警告应使用更严格的隔离"""
        # 这个验证在业务层实现更合适
        return v

    @field_validator('reset')
    @classmethod
    def validate_reset_config(cls, v: SessionResetConfig | None) -> SessionResetConfig | None:
        if v and v.mode == "idle" and not v.idle_minutes:
            raise ValueError("idle mode requires idle_minutes to be set")
        return v

    @field_validator('maintenance')
    @classmethod
    def validate_maintenance_config(cls, v: SessionMaintenanceConfig | None) -> SessionMaintenanceConfig | None:
        if v and v.max_disk_bytes and v.high_water_bytes:
            # 确保 high_water_bytes < max_disk_bytes
            # 这里需要解析字节字符串
            pass
        return v
```

---

## 8. 测试用例

### 8.1 单元测试

```python
# tests/unit/test_session_config.py

import pytest
from app.models.session_config import (
    SessionConfig,
    SessionResetConfig,
    SessionMaintenanceConfig,
)

def test_default_session_config():
    """测试默认配置"""
    config = SessionConfig()
    assert config.dm_scope == "main"
    assert config.reset is None
    assert config.maintenance is None

def test_to_openclaw_format():
    """测试转换为 OpenClaw 格式"""
    config = SessionConfig(
        dm_scope="per-channel-peer",
        reset=SessionResetConfig(mode="daily", at_hour=4, idle_minutes=120),
        maintenance=SessionMaintenanceConfig(mode="enforce", max_entries=500),
    )

    oc = config.to_openclaw()

    assert oc["dmScope"] == "per-channel-peer"
    assert oc["reset"]["mode"] == "daily"
    assert oc["reset"]["atHour"] == 4
    assert oc["reset"]["idleMinutes"] == 120
    assert oc["maintenance"]["mode"] == "enforce"
    assert oc["maintenance"]["maxEntries"] == 500

def test_from_openclaw_format():
    """测试从 OpenClaw 格式解析"""
    oc_data = {
        "dmScope": "per-peer",
        "reset": {"mode": "idle", "idleMinutes": 60},
        "maintenance": {"mode": "enforce", "pruneAfter": "14d"},
    }

    config = SessionConfig.from_openclaw(oc_data)

    assert config.dm_scope == "per-peer"
    assert config.reset.mode == "idle"
    assert config.reset.idle_minutes == 60
    assert config.maintenance.mode == "enforce"
    assert config.maintenance.prune_after == "14d"

def test_reset_config_validation():
    """测试重置配置验证"""
    # idle 模式必须设置 idle_minutes
    with pytest.raises(ValueError):
        SessionResetConfig(mode="idle")

def test_identity_links():
    """测试身份映射"""
    config = SessionConfig(
        identity_links={
            "alice": ["telegram:123", "discord:456"],
        }
    )

    oc = config.to_openclaw()
    assert oc["identityLinks"]["alice"] == ["telegram:123", "discord:456"]
```

### 8.2 集成测试

```python
# tests/integration/test_session_api.py

import pytest
from fastapi.testclient import TestClient

def test_update_session_config(client: TestClient, test_agent_id: str):
    """测试更新 Session 配置"""
    response = client.patch(
        f"/api/agents/{test_agent_id}/session",
        json={
            "dmScope": "per-channel-peer",
            "reset": {"mode": "daily", "atHour": 4},
        }
    )
    assert response.status_code == 200

    data = response.json()
    assert data["session"]["dmScope"] == "per-channel-peer"
    assert data["session"]["reset"]["mode"] == "daily"

def test_get_session_config(client: TestClient, test_agent_id: str):
    """测试获取 Session 配置"""
    response = client.get(f"/api/agents/{test_agent_id}/session")
    assert response.status_code == 200
    assert "session" in response.json()

def test_session_sync_to_openclaw(client: TestClient, test_agent_id: str):
    """测试 Session 配置同步到 OpenClaw"""
    # 更新配置
    client.patch(
        f"/api/agents/{test_agent_id}/session",
        json={"dmScope": "per-peer"}
    )

    # 验证同步
    # 这里需要检查 openclaw.json
    pass
```

---

## 9. 实施检查清单

- [ ] 后端模型定义 (`backend/app/models/session_config.py`)
- [ ] 后端 API 路由 (`backend/app/api/agents.py` 增强)
- [ ] 同步逻辑更新 (`backend/app/services/agent_service.py`)
- [ ] 前端类型定义 (`frontend/lib/types/session.ts`)
- [ ] 前端表单组件
- [ ] 配置预设
- [ ] 单元测试
- [ ] 集成测试
- [ ] 文档更新

---

## 10. 参考文档

- OpenClaw Session 配置: `/Users/roc/workspace/openclaw/docs/concepts/session.md`
- OpenClaw Session 管理: `/Users/roc/workspace/openclaw/docs/reference/session-management-compaction.md`
- OpenClaw 配置参考: `/Users/roc/workspace/openclaw/docs/gateway/configuration-reference.md`
