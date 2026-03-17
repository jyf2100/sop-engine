"use client";

import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

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
  // 飞书配置
  app_id?: string;
  app_secret?: string;
  encrypt_key?: string;
  verification_token?: string;
}

interface BasicInfoTabProps {
  data: ChannelFormData;
  updateField: <K extends keyof ChannelFormData>(field: K, value: ChannelFormData[K]) => void;
  isNew: boolean;
}

export function BasicInfoTab({ data, updateField, isNew }: BasicInfoTabProps) {
  return (
    <div className="space-y-6">
      {/* Channel ID */}
      <div className="space-y-2">
        <Label htmlFor="id">Channel ID</Label>
        <Input
          id="id"
          value={data.id}
          onChange={(e) => updateField("id", e.target.value)}
          placeholder="例如: feishu-main"
          disabled={!isNew}
          className={!isNew ? "bg-zinc-50 dark:bg-zinc-800" : ""}
        />
        <p className="text-xs text-zinc-500">
          唯一标识符，创建后不可修改
        </p>
      </div>

      {/* Name */}
      <div className="space-y-2">
        <Label htmlFor="name">显示名称</Label>
        <Input
          id="name"
          value={data.name}
          onChange={(e) => updateField("name", e.target.value)}
          placeholder="例如: 主飞书机器人"
        />
      </div>

      {/* Type */}
      <div className="space-y-2">
        <Label htmlFor="type">平台类型</Label>
        <Select
          value={data.type}
          onValueChange={(value) => updateField("type", value)}
          disabled={!isNew}
        >
          <SelectTrigger id="type" className={!isNew ? "bg-zinc-50 dark:bg-zinc-800" : ""}>
            <SelectValue placeholder="选择平台类型" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="telegram">📱 Telegram</SelectItem>
            <SelectItem value="whatsapp">💬 WhatsApp</SelectItem>
            <SelectItem value="feishu">🔶 飞书</SelectItem>
            <SelectItem value="discord">🎮 Discord</SelectItem>
            <SelectItem value="slack">💼 Slack</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Enabled */}
      <div className="flex items-center justify-between">
        <div className="space-y-0.5">
          <Label htmlFor="enabled">启用状态</Label>
          <p className="text-xs text-zinc-500">
            禁用后该 Channel 将不会接收消息
          </p>
        </div>
        <Switch
          id="enabled"
          checked={data.enabled}
          onCheckedChange={(checked: boolean) => updateField("enabled", checked)}
        />
      </div>

      {/* Streaming Mode - Common for all channels */}
      <div className="space-y-2">
        <Label htmlFor="streaming">流式输出模式</Label>
        <Select
          value={data.streaming || "partial"}
          onValueChange={(value) => updateField("streaming", value)}
        >
          <SelectTrigger id="streaming">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="off">关闭 - 等待完整回复</SelectItem>
            <SelectItem value="partial">部分 - 边生成边发送</SelectItem>
            <SelectItem value="block">块 - 按段落发送</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Media Max MB - Common for all channels */}
      <div className="space-y-2">
        <Label htmlFor="media_max_mb">媒体文件最大大小 (MB)</Label>
        <Input
          id="media_max_mb"
          type="number"
          value={data.media_max_mb || 100}
          onChange={(e) => updateField("media_max_mb", parseInt(e.target.value) || 100)}
          min={1}
          max={500}
        />
      </div>
    </div>
  );
}
