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
  // 飞书配置
  app_id?: string;
  app_secret?: string;
  encrypt_key?: string;
  verification_token?: string;
  // 凭据状态标记
  has_app_id?: boolean;
}

interface FeishuConfigTabProps {
  data: ChannelFormData;
  updateField: <K extends keyof ChannelFormData>(field: K, value: ChannelFormData[K]) => void;
  hasExistingCredentials?: boolean;
}

export function FeishuConfigTab({ data, updateField, hasExistingCredentials }: FeishuConfigTabProps) {
  const handleAllowFromChange = (value: string) => {
    const ids = value.split("\n").map(s => s.trim()).filter(Boolean);
    updateField("allow_from", ids);
  };

  const hasExisting = hasExistingCredentials || data.has_app_id;

  return (
    <div className="space-y-6">
      {/* App ID */}
      <div className="space-y-2">
        <Label htmlFor="app_id">App ID</Label>
        {hasExisting && !data.app_id && (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400 text-sm mb-2">
            <AlertCircle className="h-4 w-4" />
            已配置 App ID，留空保持不变
          </div>
        )}
        <Input
          id="app_id"
          value={data.app_id || ""}
          onChange={(e) => updateField("app_id", e.target.value || undefined)}
          placeholder="cli_xxxxxxxxxxxxxxxx"
        />
        <p className="text-xs text-zinc-500">
          在飞书开放平台创建企业自建应用后获取
        </p>
      </div>

      {/* App Secret */}
      <div className="space-y-2">
        <Label htmlFor="app_secret">App Secret</Label>
        <Input
          id="app_secret"
          type="password"
          value={data.app_secret || ""}
          onChange={(e) => updateField("app_secret", e.target.value || undefined)}
          placeholder="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        />
        <p className="text-xs text-zinc-500">
          飞书开放平台应用详情页获取
        </p>
      </div>

      {/* Encrypt Key */}
      <div className="space-y-2">
        <Label htmlFor="encrypt_key">Encrypt Key（可选）</Label>
        <Input
          id="encrypt_key"
          type="password"
          value={data.encrypt_key || ""}
          onChange={(e) => updateField("encrypt_key", e.target.value || undefined)}
          placeholder="用于消息加密的密钥"
        />
        <p className="text-xs text-zinc-500">
          如需启用消息加密，在飞书开放平台配置
        </p>
      </div>

      {/* Verification Token */}
      <div className="space-y-2">
        <Label htmlFor="verification_token">Verification Token</Label>
        <Input
          id="verification_token"
          type="password"
          value={data.verification_token || ""}
          onChange={(e) => updateField("verification_token", e.target.value || undefined)}
          placeholder="用于验证请求来源"
        />
        <p className="text-xs text-zinc-500">
          飞书开放平台事件订阅配置中的 Verification Token
        </p>
      </div>

      {/* Allow From */}
      <div className="space-y-2">
        <Label htmlFor="allow_from">允许的用户</Label>
        <Textarea
          id="allow_from"
          value={data.allow_from?.join("\n") || ""}
          onChange={(e) => handleAllowFromChange(e.target.value)}
          placeholder="每行一个用户 Open ID&#10;例如:&#10;ou_xxxxxxxxxxxxxxxx&#10;ou_yyyyyyyyyyyyyyyy"
          rows={4}
        />
        <p className="text-xs text-zinc-500">
          仅这些用户可以向 Agent 发送消息
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
          placeholder={'{\n  "oc_xxxxxxxxxxxxxxxx": {\n    "requireMention": true,\n    "allowFrom": ["ou_xxxxxxxxxxxxxxxx"]\n  }\n}'}
          rows={6}
          className="font-mono text-sm"
        />
        <p className="text-xs text-zinc-500">
          高级配置：为特定群组设置 requireMention 和 allowFrom
        </p>
      </div>

      {/* Help Section */}
      <div className="p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 text-sm">
        <h4 className="font-semibold mb-2">📋 配置说明</h4>
        <ol className="list-decimal list-inside space-y-1 text-xs">
          <li>访问飞书开放平台 open.feishu.cn</li>
          <li>创建企业自建应用</li>
          <li>在应用详情页获取 App ID 和 App Secret</li>
          <li>配置事件订阅，设置请求网址</li>
          <li>开启消息卡片、接收消息等权限</li>
          <li>发布版本并应用到企业</li>
        </ol>
      </div>
    </div>
  );
}
