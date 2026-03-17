"use client";

import { useState, useEffect } from "react";
import { apiClient, ChannelConfig, UpdateChannelRequest } from "@/lib/api-client";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ChannelForm, ChannelFormData } from "./channel-form";
import { Loader2 } from "lucide-react";

interface EditChannelDialogProps {
  channel: ChannelConfig | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function EditChannelDialog({ channel, open, onOpenChange, onSuccess }: EditChannelDialogProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<ChannelFormData>({
    id: "",
    type: "",
    name: "",
    enabled: true,
    bot_token: "",
    dm_policy: "pairing",
    allow_from: [],
    group_policy: "allowlist",
    group_allow_from: [],
    groups: {},
    streaming: "partial",
    media_max_mb: 100,
    // 飞书配置
    app_id: "",
    app_secret: "",
    encrypt_key: "",
    verification_token: "",
  });

  useEffect(() => {
    if (channel) {
      setFormData({
        id: channel.id,
        type: channel.type,
        name: channel.name,
        enabled: channel.enabled,
        bot_token: "", // Don't show existing token
        dm_policy: channel.dm_policy,
        allow_from: channel.allow_from || [],
        group_policy: channel.group_policy,
        group_allow_from: channel.group_allow_from || [],
        groups: channel.groups || {},
        streaming: channel.streaming,
        media_max_mb: channel.media_max_mb,
        // 飞书配置 - 不显示现有凭据
        app_id: "",
        app_secret: "",
        encrypt_key: "",
        verification_token: "",
      });
    }
  }, [channel]);

  const handleSubmit = async () => {
    if (!channel) return;

    setLoading(true);
    setError(null);

    try {
      // Only send non-empty values
      const payload: UpdateChannelRequest = {};
      if (formData.name !== channel.name) payload.name = formData.name;
      if (formData.enabled !== channel.enabled) payload.enabled = formData.enabled;
      if (formData.bot_token) payload.bot_token = formData.bot_token; // Only send if changed
      if (formData.dm_policy !== channel.dm_policy) payload.dm_policy = formData.dm_policy as UpdateChannelRequest["dm_policy"];
      if (JSON.stringify(formData.allow_from) !== JSON.stringify(channel.allow_from)) {
        payload.allow_from = formData.allow_from?.filter(Boolean) || [];
      }
      if (formData.group_policy !== channel.group_policy) payload.group_policy = formData.group_policy as UpdateChannelRequest["group_policy"];
      if (JSON.stringify(formData.group_allow_from) !== JSON.stringify(channel.group_allow_from)) {
        payload.group_allow_from = formData.group_allow_from?.filter(Boolean) || [];
      }
      if (JSON.stringify(formData.groups) !== JSON.stringify(channel.groups)) {
        payload.groups = formData.groups;
      }
      if (formData.streaming !== channel.streaming) payload.streaming = formData.streaming as UpdateChannelRequest["streaming"];
      if (formData.media_max_mb !== channel.media_max_mb) payload.media_max_mb = formData.media_max_mb;
      // 飞书配置 - 只发送有值的字段
      if (formData.app_id) payload.app_id = formData.app_id;
      if (formData.app_secret) payload.app_secret = formData.app_secret;
      if (formData.encrypt_key) payload.encrypt_key = formData.encrypt_key;
      if (formData.verification_token) payload.verification_token = formData.verification_token;

      await apiClient.patch(`/api/channels/${channel.id}`, payload);
      onSuccess();
    } catch (err) {
      const message = err instanceof Error ? err.message : "更新 Channel 失败";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  if (!channel) return null;

  // 判断是否有飞书凭据
  const hasFeishuCredentials = channel.has_app_id || channel.has_app_secret;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold">
            编辑 Channel
          </DialogTitle>
        </DialogHeader>

        <ChannelForm
          data={formData}
          onChange={setFormData}
          isNew={false}
          hasExistingToken={channel.has_bot_token}
          hasExistingAppCredentials={hasFeishuCredentials}
        />

        {error && (
          <div className="p-3 rounded-lg bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 text-sm">
            {error}
          </div>
        )}

        <div className="flex justify-end gap-3 pt-4 border-t border-zinc-200 dark:border-zinc-700">
          <Button
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={loading}
          >
            取消
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={loading}
            className="bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700"
          >
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            保存
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
