"use client";

import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
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

interface WhatsAppConfigTabProps {
  data: ChannelFormData;
  updateField: <K extends keyof ChannelFormData>(field: K, value: ChannelFormData[K]) => void;
}

export function WhatsAppConfigTab({ data, updateField }: WhatsAppConfigTabProps) {
  const handleAllowFromChange = (value: string) => {
    const phones = value.split("\n").map(s => s.trim()).filter(Boolean);
    updateField("allow_from", phones);
  };

  return (
    <div className="space-y-6">
      {/* Phone ID */}
      <div className="space-y-2">
        <Label htmlFor="phone_id">Phone ID</Label>
        {data.phone_id === undefined && (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 text-sm mb-2">
            <AlertCircle className="h-4 w-4" />
            WhatsApp Business API Phone ID
          </div>
        )}
        <Input
          id="phone_id"
          type="password"
          value={data.phone_id || ""}
          onChange={(e) => updateField("phone_id", e.target.value || undefined)}
          placeholder="WhatsApp Business Phone ID"
        />
        <p className="text-xs text-zinc-500">
          从 Meta for Developers 获取的 WhatsApp Business Phone ID
        </p>
      </div>

      {/* Allow From */}
      <div className="space-y-2">
        <Label htmlFor="allow_from">允许的发送者</Label>
        <Textarea
          id="allow_from"
          value={data.allow_from?.join("\n") || ""}
          onChange={(e) => handleAllowFromChange(e.target.value)}
          placeholder="每行一个电话号码&#10;例如:&#10;+15555550123&#10;+15555550456"
          rows={4}
        />
        <p className="text-xs text-zinc-500">
          仅这些电话号码可以向 Agent 发送消息
        </p>
      </div>

      {/* Groups Config */}
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
          placeholder={'{\n  "*": {\n    "requireMention": true\n  }\n}'}
          rows={6}
          className="font-mono text-sm"
        />
        <p className="text-xs text-zinc-500">
          高级配置：设置群组的 requireMention 和 allowFrom
        </p>
      </div>
    </div>
  );
}
