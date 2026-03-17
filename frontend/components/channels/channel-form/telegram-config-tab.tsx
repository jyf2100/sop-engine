"use client";

import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { AlertCircle } from "lucide-react";

interface ChannelFormData {
  id: string;
  type: string;
  name: string;
  enabled: boolean;
  bot_token?: string;
  dm_policy?: string;
  allow_from?: string[];
  group_policy?: string;
  group_allow_from?: string[];
  groups?: Record<string, { requireMention?: boolean; allowFrom?: string[] }>;
  streaming?: string;
  media_max_mb?: number;
  phone_id?: string;
}

interface TelegramConfigTabProps {
  data: ChannelFormData;
  updateField: <K extends keyof ChannelFormData>(field: K, value: ChannelFormData[K]) => void;
  hasExistingToken?: boolean;
}

export function TelegramConfigTab({ data, updateField, hasExistingToken }: TelegramConfigTabProps) {
  const handleAllowFromChange = (value: string) => {
    const ids = value.split("\n").map(s => s.trim()).filter(Boolean);
    updateField("allow_from", ids);
  };

  const handleGroupAllowFromChange = (value: string) => {
    const ids = value.split("\n").map(s => s.trim()).filter(Boolean);
    updateField("group_allow_from", ids);
  };

  return (
    <div className="space-y-6">
      {/* Bot Token */}
      <div className="space-y-2">
        <Label htmlFor="bot_token">Bot Token</Label>
        {hasExistingToken && !data.bot_token && (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 text-sm mb-2">
            <AlertCircle className="h-4 w-4" />
            已配置 Token，留空保持不变
          </div>
        )}
        <Input
          id="bot_token"
          type="password"
          value={data.bot_token || ""}
          onChange={(e) => updateField("bot_token", e.target.value || undefined)}
          placeholder="从 BotFather 获取的 Token"
        />
        <p className="text-xs text-zinc-500">
          在 Telegram 中与 @BotFather 对话创建 Bot 并获取 Token
        </p>
      </div>

      {/* DM Policy */}
      <div className="space-y-2">
        <Label htmlFor="dm_policy">私聊策略</Label>
        <Select
          value={data.dm_policy || "pairing"}
          onValueChange={(value) => updateField("dm_policy", value)}
        >
          <SelectTrigger id="dm_policy">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="pairing">配对 - 需要配对才能私聊</SelectItem>
            <SelectItem value="allowlist">白名单 - 仅白名单用户可私聊</SelectItem>
            <SelectItem value="open">开放 - 所有人可私聊</SelectItem>
            <SelectItem value="disabled">禁用 - 不接受私聊</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* DM Allow List */}
      <div className="space-y-2">
        <Label htmlFor="allow_from">私聊白名单</Label>
        <Textarea
          id="allow_from"
          value={data.allow_from?.join("\n") || ""}
          onChange={(e) => handleAllowFromChange(e.target.value)}
          placeholder="每行一个 Telegram 用户 ID&#10;例如:&#10;123456789&#10;987654321"
          rows={4}
        />
        <p className="text-xs text-zinc-500">
          当私聊策略为&quot;白名单&quot;时，仅这些用户可以发送私聊消息
        </p>
      </div>

      {/* Group Policy */}
      <div className="space-y-2">
        <Label htmlFor="group_policy">群组策略</Label>
        <Select
          value={data.group_policy || "allowlist"}
          onValueChange={(value) => updateField("group_policy", value)}
        >
          <SelectTrigger id="group_policy">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="open">开放 - 所有人可在群组发送消息</SelectItem>
            <SelectItem value="allowlist">白名单 - 仅白名单用户可在群组发送消息</SelectItem>
            <SelectItem value="disabled">禁用 - 不响应群组消息</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Group Allow List */}
      <div className="space-y-2">
        <Label htmlFor="group_allow_from">群组发送者白名单</Label>
        <Textarea
          id="group_allow_from"
          value={data.group_allow_from?.join("\n") || ""}
          onChange={(e) => handleGroupAllowFromChange(e.target.value)}
          placeholder="每行一个 Telegram 用户 ID&#10;例如:&#10;123456789&#10;987654321"
          rows={4}
        />
        <p className="text-xs text-zinc-500">
          当群组策略为&quot;白名单&quot;时，仅这些用户可以在群组中触发 Agent 响应
        </p>
      </div>

      {/* Groups Config - Simplified */}
      <div className="space-y-2">
        <Label htmlFor="groups">群组配置 (JSON)</Label>
        <Textarea
          id="groups"
          value={JSON.stringify(data.groups || {}, null, 2)}
          onChange={(e) => {
            try {
              const parsed = JSON.parse(e.target.value);
              updateField("groups", parsed);
            } catch {
              // Invalid JSON, ignore
            }
          }}
          placeholder={'{\n  "-1001234567890": {\n    "requireMention": false,\n    "allowFrom": ["123456789"]\n  }\n}'}
          rows={6}
          className="font-mono text-sm"
        />
        <p className="text-xs text-zinc-500">
          高级配置：为特定群组设置 requireMention 和 allowFrom
        </p>
      </div>
    </div>
  );
}
