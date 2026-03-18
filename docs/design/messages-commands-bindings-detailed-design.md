# Messages / Commands / Bindings 配置详细设计

## 文档信息

| 项目 | 值 |
|------|-----|
| 版本 | v1.0 |
| 日期 | 2026-03-18 |
| 状态 | Draft |
| 父文档 | openclaw-config-alignment-design.md |

---

# Part A: Messages 配置详细设计

## A.1 概述

### A.1.1 Messages 配置的作用

Messages 配置控制 OpenClaw 如何：
1. **消息响应格式** - 响应前缀、确认反应
2. **消息队列** - 并发消息的处理策略
3. **入站防抖** - 批量处理快速连续消息
4. **TTS** - 文本转语音配置

### A.1.2 消息流程概览

```
入站消息
  -> 路由/绑定 -> Session Key
  -> 防抖 (inbound.debounceMs)
  -> 队列 (queue.mode)
  -> Agent 运行 (流式 + 工具)
  -> 出站回复 (渠道限制 + 分块)
```

---

## A.2 数据模型设计

### A.2.1 完整模型定义

```python
# backend/app/models/messages_config.py

from datetime import datetime
from typing import Any, Literal
from pydantic import Field
from .base import Base

# ==================== 类型定义 ====================

QueueMode = Literal["steer", "followup", "collect", "steer-backlog", "queue", "interrupt"]
AckReactionScope = Literal["group-mentions", "group-all", "direct", "all"]
TtsAutoMode = Literal["off", "always", "inbound", "tagged"]
TtsOutputMode = Literal["final", "all"]
DropPolicy = Literal["old", "new", "summarize"]

# ==================== 响应前缀配置 ====================

class ResponsePrefixConfig(Base):
    """响应前缀配置

    对应 OpenClaw: messages.responsePrefix

    支持模板变量:
    - {model} - 短模型名
    - {modelFull} - 完整模型标识
    - {provider} - 提供商名
    - {thinkingLevel} - 思考级别
    - {identity.name} - Agent 身份名称

    特殊值:
    - "auto" - 自动生成为 [{identity.name}]
    - "" - 禁用
    """
    prefix: str | None = None  # None = "auto"

    def to_openclaw(self) -> str | None:
        return self.prefix

# ==================== 确认反应配置 ====================

class AckReactionConfig(Base):
    """确认反应配置

    对应 OpenClaw: messages.ackReaction, ackReactionScope, removeAckAfterReply

    Agent 收到消息后立即发送确认反应。
    """
    emoji: str = "👀"  # 确认反应 emoji
    scope: AckReactionScope = "group-mentions"
    remove_after_reply: bool = False

    # 渠道级覆盖（存储在 separate 字段中）
    # channels.<channel>.ackReaction
    # channels.<channel>.accounts.<id>.ackReaction

    def to_openclaw(self) -> dict:
        return {
            "ackReaction": self.emoji,
            "ackReactionScope": self.scope,
            "removeAckAfterReply": self.remove_after_reply,
        }

# ==================== 入站防抖配置 ====================

class InboundDebounceConfig(Base):
    """入站防抖配置

    对应 OpenClaw: messages.inbound

    将同一发送者的快速连续消息批量为单个 Agent 轮次。
    """
    debounce_ms: int = Field(default=2000, ge=0, description="防抖毫秒数，0 禁用")
    by_channel: dict[str, int] = {}  # 按渠道覆盖

    def to_openclaw(self) -> dict:
        result = {"debounceMs": self.debounce_ms}
        if self.by_channel:
            result["byChannel"] = self.by_channel
        return result

# ==================== 消息队列配置 ====================

class MessageQueueConfig(Base):
    """消息队列配置

    对应 OpenClaw: messages.queue

    控制并发消息的处理策略。

    模式说明:
    - steer: 立即注入当前运行（在下一个工具边界取消待处理工具调用）
    - followup: 当前运行结束后排队等待下一轮
    - collect: 将所有排队消息合并为单个 followup 轮次（默认）
    - steer-backlog: 立即转向 + 保留消息用于 followup
    - interrupt: 中止当前运行，运行最新消息
    - queue: steer 的别名
    """
    mode: QueueMode = "collect"
    debounce_ms: int = Field(default=1000, ge=0, description="followup 前等待静默的毫秒数")
    cap: int = Field(default=20, ge=1, description="每会话最大排队消息数")
    drop: DropPolicy = "summarize"  # 溢出策略
    by_channel: dict[str, QueueMode] = {}  # 按渠道覆盖

    def to_openclaw(self) -> dict:
        result = {
            "mode": self.mode,
            "debounceMs": self.debounce_ms,
            "cap": self.cap,
            "drop": self.drop,
        }
        if self.by_channel:
            result["byChannel"] = self.by_channel
        return result

# ==================== TTS 配置 ====================

class ElevenLabsVoiceSettings(Base):
    """ElevenLabs 语音设置"""
    stability: float = Field(default=0.5, ge=0, le=1)
    similarity_boost: float = Field(default=0.75, ge=0, le=1)
    style: float = Field(default=0.0, ge=0, le=1)
    use_speaker_boost: bool = True
    speed: float = Field(default=1.0, ge=0.5, le=2.0)

class ElevenLabsConfig(Base):
    """ElevenLabs TTS 配置"""
    api_key: str | None = None
    base_url: str = "https://api.elevenlabs.io"
    voice_id: str | None = None
    model_id: str = "eleven_multilingual_v2"
    seed: int | None = None
    apply_text_normalization: Literal["auto", "on", "off"] = "auto"
    language_code: str | None = None
    voice_settings: ElevenLabsVoiceSettings | None = None

class OpenAITTSConfig(Base):
    """OpenAI TTS 配置"""
    api_key: str | None = None
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4o-mini-tts"
    voice: str = "alloy"

class TTSConfig(Base):
    """TTS 配置

    对应 OpenClaw: messages.tts
    """
    auto: TtsAutoMode = "off"
    mode: TtsOutputMode = "final"
    provider: Literal["elevenlabs", "openai"] = "elevenlabs"
    summary_model: str | None = None
    model_overrides: dict[str, Any] | None = None
    max_text_length: int = 4000
    timeout_ms: int = 30000
    prefs_path: str = "~/.openclaw/settings/tts.json"
    elevenlabs: ElevenLabsConfig | None = None
    openai: OpenAITTSConfig | None = None

    def to_openclaw(self) -> dict:
        result: dict[str, Any] = {
            "auto": self.auto,
            "mode": self.mode,
            "provider": self.provider,
            "maxTextLength": self.max_text_length,
            "timeoutMs": self.timeout_ms,
        }
        if self.summary_model:
            result["summaryModel"] = self.summary_model
        if self.model_overrides:
            result["modelOverrides"] = self.model_overrides
        if self.elevenlabs:
            result["elevenlabs"] = self._elevenlabs_to_openclaw(self.elevenlabs)
        if self.openai:
            result["openai"] = self._openai_to_openclaw(self.openai)
        return result

    def _elevenlabs_to_openclaw(self, config: ElevenLabsConfig) -> dict:
        result: dict[str, Any] = {
            "baseUrl": config.base_url,
            "modelId": config.model_id,
        }
        if config.api_key:
            result["apiKey"] = config.api_key
        if config.voice_id:
            result["voiceId"] = config.voice_id
        if config.seed is not None:
            result["seed"] = config.seed
        if config.voice_settings:
            result["voiceSettings"] = {
                "stability": config.voice_settings.stability,
                "similarityBoost": config.voice_settings.similarity_boost,
                "style": config.voice_settings.style,
                "useSpeakerBoost": config.voice_settings.use_speaker_boost,
                "speed": config.voice_settings.speed,
            }
        return result

    def _openai_to_openclaw(self, config: OpenAITTSConfig) -> dict:
        result: dict[str, Any] = {
            "baseUrl": config.base_url,
            "model": config.model,
            "voice": config.voice,
        }
        if config.api_key:
            result["apiKey"] = config.api_key
        return result

# ==================== 主模型 ====================

class MessagesConfig(Base):
    """Messages 配置模型

    对应 OpenClaw: messages.*
    """

    # === 响应前缀 ===
    response_prefix: str | None = None  # "auto" | 自定义 | None

    # === 确认反应 ===
    ack_reaction: str = "👀"  # 确认反应 emoji
    ack_reaction_scope: AckReactionScope = "group-mentions"
    remove_ack_after_reply: bool = False

    # === 入站防抖 ===
    inbound: InboundDebounceConfig | None = None

    # === 消息队列 ===
    queue: MessageQueueConfig | None = None

    # === TTS ===
    tts: TTSConfig | None = None

    # === 元数据 ===
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # ==================== 序列化方法 ====================

    def to_openclaw(self) -> dict:
        """转换为 OpenClaw 配置格式"""
        result: dict[str, Any] = {}

        # 响应前缀
        if self.response_prefix is not None:
            result["responsePrefix"] = self.response_prefix

        # 确认反应
        result["ackReaction"] = self.ack_reaction
        result["ackReactionScope"] = self.ack_reaction_scope
        result["removeAckAfterReply"] = self.remove_ack_after_reply

        # 入站防抖
        if self.inbound:
            result["inbound"] = self.inbound.to_openclaw()

        # 消息队列
        if self.queue:
            result["queue"] = self.queue.to_openclaw()

        # TTS
        if self.tts:
            result["tts"] = self.tts.to_openclaw()

        return result

    @classmethod
    def from_openclaw(cls, data: dict) -> "MessagesConfig":
        """从 OpenClaw 配置格式解析"""
        # 解析嵌套配置
        inbound = None
        if "inbound" in data:
            ib = data["inbound"]
            inbound = InboundDebounceConfig(
                debounce_ms=ib.get("debounceMs", 2000),
                by_channel=ib.get("byChannel", {}),
            )

        queue = None
        if "queue" in data:
            q = data["queue"]
            queue = MessageQueueConfig(
                mode=q.get("mode", "collect"),
                debounce_ms=q.get("debounceMs", 1000),
                cap=q.get("cap", 20),
                drop=q.get("drop", "summarize"),
                by_channel=q.get("byChannel", {}),
            )

        tts = None
        if "tts" in data:
            t = data["tts"]
            tts = TTSConfig(
                auto=t.get("auto", "off"),
                mode=t.get("mode", "final"),
                provider=t.get("provider", "elevenlabs"),
                summary_model=t.get("summaryModel"),
                model_overrides=t.get("modelOverrides"),
                max_text_length=t.get("maxTextLength", 4000),
                timeout_ms=t.get("timeoutMs", 30000),
            )

        return cls(
            response_prefix=data.get("responsePrefix"),
            ack_reaction=data.get("ackReaction", "👀"),
            ack_reaction_scope=data.get("ackReactionScope", "group-mentions"),
            remove_ack_after_reply=data.get("removeAckAfterReply", False),
            inbound=inbound,
            queue=queue,
            tts=tts,
        )
```

### A.2.2 与 Agent 模型的集成

```python
# backend/app/models/agent.py (更新)

from .messages_config import MessagesConfig

class Agent(Base):
    """Agent 配置模型"""
    # ... 现有字段 ...

    # === 新增：Messages 配置 ===
    messages_config: MessagesConfig | None = None
```

---

## A.3 队列模式详解

### A.3.1 模式对比

| 模式 | 行为 | 适用场景 |
|------|------|---------|
| `collect` | 合并所有排队消息为单个 followup | 默认，适合大多数场景 |
| `steer` | 立即注入当前运行 | 需要实时响应的场景 |
| `followup` | 等待当前运行结束后处理 | 长任务场景 |
| `steer-backlog` | 转向 + 保留用于 followup | 需要双重确认的场景 |
| `interrupt` | 中止当前运行 | 紧急消息场景 |

### A.3.2 溢出策略

| 策略 | 行为 |
|------|------|
| `summarize` | 保留简要摘要，注入为合成提示 |
| `old` | 丢弃最旧的消息 |
| `new` | 丢弃最新的消息 |

---

## A.4 前端设计

### A.4.1 类型定义

```typescript
// frontend/lib/types/messages.ts

export type QueueMode = 'steer' | 'followup' | 'collect' | 'steer-backlog' | 'interrupt';
export type AckReactionScope = 'group-mentions' | 'group-all' | 'direct' | 'all';
export type DropPolicy = 'old' | 'new' | 'summarize';

export interface InboundDebounceConfig {
  debounce_ms?: number;
  by_channel?: Record<string, number>;
}

export interface MessageQueueConfig {
  mode?: QueueMode;
  debounce_ms?: number;
  cap?: number;
  drop?: DropPolicy;
  by_channel?: Record<string, QueueMode>;
}

export interface TTSConfig {
  auto?: 'off' | 'always' | 'inbound' | 'tagged';
  mode?: 'final' | 'all';
  provider?: 'elevenlabs' | 'openai';
  max_text_length?: number;
  timeout_ms?: number;
}

export interface MessagesConfig {
  response_prefix?: string;
  ack_reaction?: string;
  ack_reaction_scope?: AckReactionScope;
  remove_ack_after_reply?: boolean;
  inbound?: InboundDebounceConfig;
  queue?: MessageQueueConfig;
  tts?: TTSConfig;
}
```

### A.4.2 表单组件

```tsx
// frontend/components/agents/messages-config-form/queue-section.tsx

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';

const QUEUE_MODES = [
  { value: 'collect', label: '合并收集', description: '合并所有消息为单个回复（推荐）' },
  { value: 'steer', label: '实时转向', description: '立即注入当前运行' },
  { value: 'followup', label: '后续处理', description: '等待当前运行结束后处理' },
  { value: 'steer-backlog', label: '转向+保留', description: '转向 + 保留用于后续' },
  { value: 'interrupt', label: '中断', description: '中止当前运行' },
];

const DROP_POLICIES = [
  { value: 'summarize', label: '摘要', description: '保留简要摘要' },
  { value: 'old', label: '丢弃旧消息', description: '丢弃最旧的消息' },
  { value: 'new', label: '丢弃新消息', description: '丢弃最新的消息' },
];

export function QueueSection({ form }) {
  const queueMode = form.watch('queue.mode');

  return (
    <Card>
      <CardHeader>
        <CardTitle>消息队列配置</CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* 队列模式 */}
        <div className="space-y-2">
          <Label>队列模式</Label>
          <Select
            value={queueMode}
            onValueChange={(v) => form.setValue('queue.mode', v)}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {QUEUE_MODES.map((mode) => (
                <SelectItem key={mode.value} value={mode.value}>
                  <div>
                    <div className="font-medium">{mode.label}</div>
                    <div className="text-xs text-muted-foreground">
                      {mode.description}
                    </div>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Followup 防抖 */}
        {['followup', 'collect', 'steer-backlog'].includes(queueMode) && (
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>防抖时间 (ms)</Label>
              <Input
                type="number"
                {...form.register('queue.debounce_ms', { valueAsNumber: true })}
              />
              <p className="text-xs text-muted-foreground">
                等待静默后开始 followup
              </p>
            </div>
            <div className="space-y-2">
              <Label>队列容量</Label>
              <Input
                type="number"
                {...form.register('queue.cap', { valueAsNumber: true })}
              />
              <p className="text-xs text-muted-foreground">
                每会话最大排队消息数
              </p>
            </div>
          </div>
        )}

        {/* 溢出策略 */}
        {['followup', 'collect', 'steer-backlog'].includes(queueMode) && (
          <div className="space-y-2">
            <Label>溢出策略</Label>
            <Select
              value={form.watch('queue.drop')}
              onValueChange={(v) => form.setValue('queue.drop', v)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {DROP_POLICIES.map((policy) => (
                  <SelectItem key={policy.value} value={policy.value}>
                    <div>
                      <div className="font-medium">{policy.label}</div>
                      <div className="text-xs text-muted-foreground">
                        {policy.description}
                      </div>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
```

---

# Part B: Commands 配置详细设计

## B.1 概述

### B.1.1 Commands 配置的作用

Commands 配置控制 OpenClaw 的命令系统：
1. **原生命令** - 在渠道中注册的命令菜单
2. **文本命令** - 解析聊天消息中的 /commands
3. **Bash 命令** - 允许执行 shell 命令
4. **命令权限** - 控制谁可以执行哪些命令

### B.1.2 命令层级

```
全局命令配置 (commands.*)
    ↓
渠道级覆盖 (channels.<channel>.commands.*)
    ↓
会话级覆盖 (/queue collect 等持久化到 session)
```

---

## B.2 数据模型设计

### B.2.1 完整模型定义

```python
# backend/app/models/commands_config.py

from datetime import datetime
from typing import Literal
from pydantic import Field
from .base import Base

# ==================== 类型定义 ====================

NativeCommandMode = Literal["auto", True, False]

# ==================== 命令权限配置 ====================

class CommandsAllowFromConfig(Base):
    """命令权限配置

    对应 OpenClaw: commands.allowFrom

    按渠道控制谁可以执行命令。
    当设置时，这是唯一的授权来源（渠道白名单/pairing 被忽略）。
    """
    # 键为渠道名或 "*"（通配所有渠道）
    # 值为用户 ID 列表
    rules: dict[str, list[str]] = {}

    def to_openclaw(self) -> dict:
        return self.rules

# ==================== 主模型 ====================

class CommandsConfig(Base):
    """Commands 配置模型

    对应 OpenClaw: commands.*
    """

    # === 原生命令 ===
    native: NativeCommandMode = "auto"  # "auto" | true | false
    # "auto" 为 Discord/Telegram 启用，Slack 关闭

    # === 原生技能命令 ===
    native_skills: bool = True  # 启用/禁用 Telegram 原生技能命令

    # === 文本命令 ===
    text: bool = True  # 解析 /commands 聊天消息

    # === Bash 命令 ===
    bash: bool = False  # 允许 ! (alias: /bash)
    bash_foreground_ms: int = Field(
        default=2000,
        ge=0,
        description="Bash 命令前台执行超时（毫秒），超时后转为后台"
    )

    # === 配置命令 ===
    config: bool = False  # 允许 /config

    # === 调试命令 ===
    debug: bool = False  # 允许 /debug

    # === 重启命令 ===
    restart: bool = False  # 允许 /restart + gateway restart tool

    # === 权限控制 ===
    allow_from: CommandsAllowFromConfig | None = None
    use_access_groups: bool = True  # 使用访问组策略

    # === 元数据 ===
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # ==================== 序列化方法 ====================

    def to_openclaw(self) -> dict:
        """转换为 OpenClaw 配置格式"""
        result: dict = {
            "native": self.native,
            "text": self.text,
            "bash": self.bash,
            "config": self.config,
            "debug": self.debug,
            "restart": self.restart,
            "useAccessGroups": self.use_access_groups,
        }

        if self.native_skills is not None:
            result["nativeSkills"] = self.native_skills

        if self.bash_foreground_ms != 2000:
            result["bashForegroundMs"] = self.bash_foreground_ms

        if self.allow_from:
            result["allowFrom"] = self.allow_from.to_openclaw()

        return result

    @classmethod
    def from_openclaw(cls, data: dict) -> "CommandsConfig":
        """从 OpenClaw 配置格式解析"""
        allow_from = None
        if "allowFrom" in data:
            allow_from = CommandsAllowFromConfig(rules=data["allowFrom"])

        return cls(
            native=data.get("native", "auto"),
            native_skills=data.get("nativeSkills", True),
            text=data.get("text", True),
            bash=data.get("bash", False),
            bash_foreground_ms=data.get("bashForegroundMs", 2000),
            config=data.get("config", False),
            debug=data.get("debug", False),
            restart=data.get("restart", False),
            allow_from=allow_from,
            use_access_groups=data.get("useAccessGroups", True),
        )
```

### B.2.2 与 Agent 模型的集成

```python
# backend/app/models/agent.py (更新)

from .commands_config import CommandsConfig

class Agent(Base):
    """Agent 配置模型"""
    # ... 现有字段 ...

    # === 新增：Commands 配置 ===
    commands_config: CommandsConfig | None = None
```

---

## B.3 命令权限详解

### B.3.1 权限层级

```
1. allowFrom 设置？
   ├── 是 → 仅使用 allowFrom 列表
   │       (pairing/allowFrom/useAccessGroups 被忽略)
   └── 否 → useAccessGroups?
              ├── true → 使用访问组策略
              └── false → 绕过访问组策略
```

### B.3.2 配置示例

```yaml
# 严格权限控制
commands:
  bash: true
  allow_from:
    "*": ["user:123456"]  # 所有渠道仅允许 user:123456
    discord: ["user:789"]  # Discord 额外允许 user:789

# 开放但有访问组限制
commands:
  bash: true
  use_access_groups: true  # 默认值
  # 不设置 allow_from
```

---

## B.4 前端设计

### B.4.1 类型定义

```typescript
// frontend/lib/types/commands.ts

export type NativeCommandMode = 'auto' | true | false;

export interface CommandsAllowFromConfig {
  [channel: string]: string[];
}

export interface CommandsConfig {
  native?: NativeCommandMode;
  native_skills?: boolean;
  text?: boolean;
  bash?: boolean;
  bash_foreground_ms?: number;
  config?: boolean;
  debug?: boolean;
  restart?: boolean;
  allow_from?: CommandsAllowFromConfig;
  use_access_groups?: boolean;
}
```

### B.4.2 表单组件

```tsx
// frontend/components/agents/commands-config-form/index.tsx

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertTriangleIcon } from 'lucide-react';

export function CommandsConfigForm({ form }) {
  const bashEnabled = form.watch('bash');
  const configEnabled = form.watch('config');

  return (
    <div className="space-y-6">
      {/* 原生命令 */}
      <Card>
        <CardHeader>
          <CardTitle>原生命令</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>启用原生命令</Label>
              <p className="text-sm text-muted-foreground">
                在 Discord/Telegram 注册命令菜单
              </p>
            </div>
            <select
              value={form.watch('native')}
              onChange={(e) => form.setValue('native', e.target.value)}
              className="w-24"
            >
              <option value="auto">自动</option>
              <option value="true">启用</option>
              <option value="false">禁用</option>
            </select>
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>原生技能命令</Label>
              <p className="text-sm text-muted-foreground">
                Telegram 原生技能命令菜单
              </p>
            </div>
            <Switch
              checked={form.watch('native_skills')}
              onCheckedChange={(v) => form.setValue('native_skills', v)}
            />
          </div>
        </CardContent>
      </Card>

      {/* 高风险命令 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangleIcon className="h-4 w-4 text-yellow-500" />
            高风险命令
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert variant="destructive">
            <AlertTriangleIcon className="h-4 w-4" />
            <AlertDescription>
              以下命令具有较高安全风险，请谨慎启用并配置权限控制。
            </AlertDescription>
          </Alert>

          {/* Bash 命令 */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>Bash 命令 (! 或 /bash)</Label>
              <p className="text-sm text-muted-foreground">
                允许执行 shell 命令（需要 elevated 权限）
              </p>
            </div>
            <Switch
              checked={bashEnabled}
              onCheckedChange={(v) => form.setValue('bash', v)}
            />
          </div>

          {bashEnabled && (
            <div className="ml-6 space-y-2">
              <Label>前台执行超时 (ms)</Label>
              <Input
                type="number"
                {...form.register('bash_foreground_ms', { valueAsNumber: true })}
              />
            </div>
          )}

          {/* Config 命令 */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>配置命令 (/config)</Label>
              <p className="text-sm text-muted-foreground">
                读写 openclaw.json 配置
              </p>
            </div>
            <Switch
              checked={configEnabled}
              onCheckedChange={(v) => form.setValue('config', v)}
            />
          </div>

          {/* Debug 命令 */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>调试命令 (/debug)</Label>
              <p className="text-sm text-muted-foreground">
                显示调试信息
              </p>
            </div>
            <Switch
              checked={form.watch('debug')}
              onCheckedChange={(v) => form.setValue('debug', v)}
            />
          </div>

          {/* Restart 命令 */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>重启命令 (/restart)</Label>
              <p className="text-sm text-muted-foreground">
                重启 Gateway
              </p>
            </div>
            <Switch
              checked={form.watch('restart')}
              onCheckedChange={(v) => form.setValue('restart', v)}
            />
          </div>
        </CardContent>
      </Card>

      {/* 权限控制 */}
      <Card>
        <CardHeader>
          <CardTitle>权限控制</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>使用访问组策略</Label>
              <p className="text-sm text-muted-foreground">
                未设置 allowFrom 时使用访问组
              </p>
            </div>
            <Switch
              checked={form.watch('use_access_groups')}
              onCheckedChange={(v) => form.setValue('use_access_groups', v)}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
```

---

# Part C: Bindings 配置详细设计

## C.1 概述

### C.1.1 Bindings 配置的作用

Bindings 配置控制多 Agent 路由：
1. **路由绑定** - 将特定渠道/用户/群组路由到指定 Agent
2. **ACP 绑定** - 将会话绑定到持久化 ACP 运行时
3. **匹配优先级** - 确定性匹配顺序

### C.1.2 绑定类型

| 类型 | 用途 | 说明 |
|------|------|------|
| `route` | 路由绑定 | 将消息路由到指定 Agent |
| `acp` | ACP 绑定 | 绑定到持久化 ACP 会话 |

---

## C.2 数据模型设计

### C.2.1 完整模型定义

```python
# backend/app/models/bindings_config.py

from datetime import datetime
from typing import Any, Literal
from pydantic import Field
from .base import Base

# ==================== 类型定义 ====================

BindingType = Literal["route", "acp"]
PeerKind = Literal["direct", "group", "channel"]
AcpMode = Literal["persistent", "ephemeral"]
AcpBackend = Literal["acpx"]

# ==================== 匹配配置 ====================

class PeerMatch(Base):
    """对等体匹配配置

    用于匹配特定的用户、群组或频道。
    """
    kind: PeerKind  # direct | group | channel
    id: str  # 对等体 ID

class BindingMatch(Base):
    """绑定匹配规则

    对应 OpenClaw: bindings[].match
    """
    channel: str  # 渠道名: telegram, whatsapp, discord, etc.
    account_id: str | None = None  # 账号 ID，"*" 表示任意账号
    peer: PeerMatch | None = None  # 对等体匹配
    guild_id: str | None = None  # Discord 服务器 ID
    team_id: str | None = None  # Slack/MSTeams 团队 ID

    def to_openclaw(self) -> dict:
        result: dict[str, Any] = {"channel": self.channel}
        if self.account_id is not None:
            result["accountId"] = self.account_id
        if self.peer:
            result["peer"] = {
                "kind": self.peer.kind,
                "id": self.peer.id,
            }
        if self.guild_id:
            result["guildId"] = self.guild_id
        if self.team_id:
            result["teamId"] = self.team_id
        return result

# ==================== ACP 配置 ====================

class AcpConfig(Base):
    """ACP 绑定配置

    对应 OpenClaw: bindings[].acp (仅 type="acp" 时使用)
    """
    mode: AcpMode = "persistent"  # persistent | ephemeral
    label: str | None = None  # 会话标签
    cwd: str | None = None  # 工作目录
    backend: AcpBackend = "acpx"  # 后端类型

    def to_openclaw(self) -> dict:
        result: dict[str, Any] = {"mode": self.mode, "backend": self.backend}
        if self.label:
            result["label"] = self.label
        if self.cwd:
            result["cwd"] = self.cwd
        return result

# ==================== 绑定条目 ====================

class Binding(Base):
    """绑定条目

    对应 OpenClaw: bindings[]
    """
    type: BindingType = "route"  # route | acp
    agent_id: str  # 目标 Agent ID
    match: BindingMatch  # 匹配规则
    acp: AcpConfig | None = None  # ACP 配置（仅 type="acp" 时使用）

    def to_openclaw(self) -> dict:
        result: dict[str, Any] = {
            "type": self.type,
            "agentId": self.agent_id,
            "match": self.match.to_openclaw(),
        }
        if self.acp and self.type == "acp":
            result["acp"] = self.acp.to_openclaw()
        return result

# ==================== 主模型 ====================

class BindingsConfig(Base):
    """Bindings 配置模型

    对应 OpenClaw: bindings[]

    管理多 Agent 路由配置。

    匹配优先级（从高到低）：
    1. match.peer
    2. match.guildId
    3. match.teamId
    4. match.accountId (精确，无 peer/guild/team)
    5. match.accountId: "*" (渠道范围)
    6. 默认 Agent

    在每个层级内，第一个匹配的绑定获胜。
    """

    bindings: list[Binding] = []

    # === 元数据 ===
    created_at: datetime | None = None
    updated_at: datetime | None = None

    # ==================== 序列化方法 ====================

    def to_openclaw(self) -> list[dict]:
        """转换为 OpenClaw 配置格式"""
        return [b.to_openclaw() for b in self.bindings]

    @classmethod
    def from_openclaw(cls, data: list[dict]) -> "BindingsConfig":
        """从 OpenClaw 配置格式解析"""
        bindings = []
        for entry in data:
            # 解析 match
            match_data = entry.get("match", {})
            peer = None
            if "peer" in match_data:
                peer = PeerMatch(
                    kind=match_data["peer"]["kind"],
                    id=match_data["peer"]["id"],
                )
            match = BindingMatch(
                channel=match_data.get("channel", ""),
                account_id=match_data.get("accountId"),
                peer=peer,
                guild_id=match_data.get("guildId"),
                team_id=match_data.get("teamId"),
            )

            # 解析 acp
            acp = None
            if "acp" in entry:
                acp_data = entry["acp"]
                acp = AcpConfig(
                    mode=acp_data.get("mode", "persistent"),
                    label=acp_data.get("label"),
                    cwd=acp_data.get("cwd"),
                    backend=acp_data.get("backend", "acpx"),
                )

            bindings.append(Binding(
                type=entry.get("type", "route"),
                agent_id=entry.get("agentId", ""),
                match=match,
                acp=acp,
            ))

        return cls(bindings=bindings)
```

### C.2.2 全局 Bindings 管理

```python
# backend/app/models/global_bindings.py

class GlobalBindingsConfig(Base):
    """全局 Bindings 配置

    对应 OpenClaw: bindings[] (顶层)

    这是全局配置，不属于单个 Agent，而是定义多 Agent 路由规则。
    """
    bindings: list[Binding] = []

    def add_binding(self, binding: Binding) -> None:
        """添加绑定"""
        self.bindings.append(binding)

    def remove_binding(self, index: int) -> None:
        """移除绑定"""
        if 0 <= index < len(self.bindings):
            self.bindings.pop(index)

    def get_bindings_for_agent(self, agent_id: str) -> list[Binding]:
        """获取指定 Agent 的所有绑定"""
        return [b for b in self.bindings if b.agent_id == agent_id]

    def get_bindings_for_channel(self, channel: str) -> list[Binding]:
        """获取指定渠道的所有绑定"""
        return [b for b in self.bindings if b.match.channel == channel]
```

---

## C.3 匹配优先级详解

### C.3.1 优先级顺序

```
┌─────────────────────────────────────────────────────────┐
│                    匹配优先级（高→低）                     │
├─────────────────────────────────────────────────────────┤
│  1. match.peer (精确对等体)                               │
│     - 直接消息: { kind: "direct", id: "user_id" }        │
│     - 群组: { kind: "group", id: "group_id" }            │
│     - 频道: { kind: "channel", id: "channel_id" }        │
├─────────────────────────────────────────────────────────┤
│  2. match.guildId (Discord 服务器)                       │
│     - 匹配整个服务器的所有消息                             │
├─────────────────────────────────────────────────────────┤
│  3. match.teamId (Slack/MSTeams 团队)                    │
│     - 匹配整个团队的所有消息                               │
├─────────────────────────────────────────────────────────┤
│  4. match.accountId (精确账号)                            │
│     - 匹配特定账号，无 peer/guild/team                    │
├─────────────────────────────────────────────────────────┤
│  5. match.accountId: "*" (渠道范围)                       │
│     - 匹配渠道的所有账号                                   │
├─────────────────────────────────────────────────────────┤
│  6. 默认 Agent                                            │
│     - agents.list[].default = true                       │
└─────────────────────────────────────────────────────────┘
```

### C.3.2 配置示例

```yaml
# 精确用户路由
bindings:
  - agentId: "personal"
    match:
      channel: "whatsapp"
      accountId: "personal"
      peer: { kind: "direct", id: "+15555550123" }

# 多账号路由
bindings:
  - agentId: "home"
    match:
      channel: "whatsapp"
      accountId: "personal"
  - agentId: "work"
    match:
      channel: "whatsapp"
      accountId: "biz"

# ACP 持久化绑定
bindings:
  - type: "acp"
    agentId: "codex"
    match:
      channel: "telegram"
      accountId: "default"
      peer: { kind: "group", id: "-1001234567890:topic:42" }
    acp:
      mode: "persistent"
      label: "codex-feishu-topic"
      cwd: "/workspace/openclaw"
```

---

## C.4 前端设计

### C.4.1 类型定义

```typescript
// frontend/lib/types/bindings.ts

export type BindingType = 'route' | 'acp';
export type PeerKind = 'direct' | 'group' | 'channel';
export type AcpMode = 'persistent' | 'ephemeral';

export interface PeerMatch {
  kind: PeerKind;
  id: string;
}

export interface BindingMatch {
  channel: string;
  account_id?: string;
  peer?: PeerMatch;
  guild_id?: string;
  team_id?: string;
}

export interface AcpConfig {
  mode?: AcpMode;
  label?: string;
  cwd?: string;
  backend?: string;
}

export interface Binding {
  type?: BindingType;
  agent_id: string;
  match: BindingMatch;
  acp?: AcpConfig;
}

export interface BindingsConfig {
  bindings: Binding[];
}
```

### C.4.2 表单组件

```tsx
// frontend/components/bindings/binding-form.tsx

import { useForm } from 'react-hook-form';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';

const CHANNELS = ['telegram', 'whatsapp', 'discord', 'slack', 'feishu'];
const PEER_KINDS = [
  { value: 'direct', label: '私聊' },
  { value: 'group', label: '群组' },
  { value: 'channel', label: '频道' },
];

interface BindingFormProps {
  binding?: Binding;
  onSubmit: (data: Binding) => void;
  onCancel: () => void;
}

export function BindingForm({ binding, onSubmit, onCancel }: BindingFormProps) {
  const form = useForm<Binding>({
    defaultValues: binding || {
      type: 'route',
      agent_id: '',
      match: { channel: 'telegram' },
    },
  });

  const bindingType = form.watch('type');
  const hasPeer = !!form.watch('match.peer');

  return (
    <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
      {/* 绑定类型 */}
      <div className="space-y-2">
        <Label>绑定类型</Label>
        <Select
          value={form.watch('type')}
          onValueChange={(v) => form.setValue('type', v as BindingType)}
        >
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="route">路由绑定</SelectItem>
            <SelectItem value="acp">ACP 绑定</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* 目标 Agent */}
      <div className="space-y-2">
        <Label>目标 Agent</Label>
        <Input
          {...form.register('agent_id')}
          placeholder="Agent ID"
        />
      </div>

      {/* 匹配规则 */}
      <Card>
        <CardHeader>
          <CardTitle>匹配规则</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* 渠道 */}
          <div className="space-y-2">
            <Label>渠道</Label>
            <Select
              value={form.watch('match.channel')}
              onValueChange={(v) => form.setValue('match.channel', v)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {CHANNELS.map((ch) => (
                  <SelectItem key={ch} value={ch}>
                    {ch.charAt(0).toUpperCase() + ch.slice(1)}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* 账号 */}
          <div className="space-y-2">
            <Label>账号 ID (可选)</Label>
            <Input
              {...form.register('match.account_id')}
              placeholder="留空 = 默认账号，'*' = 所有账号"
            />
          </div>

          {/* 对等体匹配 */}
          <div className="flex items-center justify-between">
            <div className="space-y-0.5">
              <Label>精确匹配</Label>
              <p className="text-sm text-muted-foreground">
                匹配特定用户/群组/频道
              </p>
            </div>
            <Switch
              checked={hasPeer}
              onCheckedChange={(v) => {
                if (v) {
                  form.setValue('match.peer', { kind: 'direct', id: '' });
                } else {
                  form.setValue('match.peer', undefined);
                }
              }}
            />
          </div>

          {hasPeer && (
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>类型</Label>
                <Select
                  value={form.watch('match.peer.kind')}
                  onValueChange={(v) =>
                    form.setValue('match.peer.kind', v as PeerKind)
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {PEER_KINDS.map((k) => (
                      <SelectItem key={k.value} value={k.value}>
                        {k.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>ID</Label>
                <Input
                  {...form.register('match.peer.id')}
                  placeholder="用户/群组/频道 ID"
                />
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* ACP 配置 */}
      {bindingType === 'acp' && (
        <Card>
          <CardHeader>
            <CardTitle>ACP 配置</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>模式</Label>
                <Select
                  value={form.watch('acp.mode')}
                  onValueChange={(v) => form.setValue('acp.mode', v as AcpMode)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="persistent">持久化</SelectItem>
                    <SelectItem value="ephemeral">临时</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>标签</Label>
                <Input
                  {...form.register('acp.label')}
                  placeholder="会话标签"
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label>工作目录</Label>
              <Input
                {...form.register('acp.cwd')}
                placeholder="/workspace/..."
              />
            </div>
          </CardContent>
        </Card>
      )}

      {/* 提交按钮 */}
      <div className="flex justify-end gap-2">
        <button type="button" onClick={onCancel} className="...">
          取消
        </button>
        <button type="submit" className="...">
          保存
        </button>
      </div>
    </form>
  );
}
```

---

# Part D: 实施计划

## D.1 优先级排序

| 阶段 | 模块 | 优先级 | 预计工时 | 原因 |
|------|------|--------|---------|------|
| 1 | Messages | HIGH | 4h | 影响用户体验，队列配置关键 |
| 2 | Commands | MEDIUM | 3h | 安全相关，需谨慎配置 |
| 3 | Bindings | HIGH | 4h | 多 Agent 核心功能 |
| **总计** | | | **11h** | |

## D.2 实施检查清单

### Messages 配置
- [ ] 后端模型定义
- [ ] 后端 API 路由
- [ ] 同步逻辑更新
- [ ] 前端类型定义
- [ ] 前端表单组件
- [ ] 单元测试
- [ ] 集成测试

### Commands 配置
- [ ] 后端模型定义
- [ ] 后端 API 路由
- [ ] 同步逻辑更新
- [ ] 前端类型定义
- [ ] 前端表单组件（含安全警告）
- [ ] 单元测试
- [ ] 集成测试

### Bindings 配置
- [ ] 后端模型定义
- [ ] 后端 API 路由（全局管理）
- [ ] 同步逻辑更新
- [ ] 前端类型定义
- [ ] 前端表单组件
- [ ] Bindings 列表管理 UI
- [ ] 单元测试
- [ ] 集成测试

---

## D.3 参考文档

- OpenClaw Messages: `/Users/roc/workspace/openclaw/docs/concepts/messages.md`
- OpenClaw Queue: `/Users/roc/workspace/openclaw/docs/concepts/queue.md`
- OpenClaw Configuration Reference: `/Users/roc/workspace/openclaw/docs/gateway/configuration-reference.md`
