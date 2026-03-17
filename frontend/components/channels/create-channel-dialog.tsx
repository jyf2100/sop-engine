"use client";

import { useState } from "react";
import { apiClient, CreateChannelRequest } from "@/lib/api-client";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { ChannelForm, ChannelFormData } from "./channel-form";
import { Loader2 } from "lucide-react";

interface CreateChannelDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function CreateChannelDialog({ open, onOpenChange, onSuccess }: CreateChannelDialogProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState<ChannelFormData>({
    id: "",
    name: "",
    type: "telegram",
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

  const handleSubmit = async () => {
    if (!formData.id || !formData.name) {
      setError("请填写 Channel ID 和名称");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Clean up empty values and convert to API type
      const payload: CreateChannelRequest = {
        id: formData.id,
        name: formData.name,
        type: formData.type as CreateChannelRequest["type"],
        enabled: formData.enabled,
        bot_token: formData.bot_token || undefined,
        dm_policy: formData.dm_policy as CreateChannelRequest["dm_policy"],
        allow_from: formData.allow_from?.filter(Boolean) || [],
        group_policy: formData.group_policy as CreateChannelRequest["group_policy"],
        group_allow_from: formData.group_allow_from?.filter(Boolean) || [],
        groups: formData.groups,
        streaming: formData.streaming as CreateChannelRequest["streaming"],
        media_max_mb: formData.media_max_mb,
        phone_id: formData.phone_id || undefined,
        // 飞书配置
        app_id: formData.app_id || undefined,
        app_secret: formData.app_secret || undefined,
        encrypt_key: formData.encrypt_key || undefined,
        verification_token: formData.verification_token || undefined,
      };

      await apiClient.post("/api/channels", payload);
      setFormData({
        id: "",
        name: "",
        type: "telegram",
        enabled: true,
        bot_token: "",
        dm_policy: "pairing",
        allow_from: [],
        group_policy: "allowlist",
        group_allow_from: [],
        groups: {},
        streaming: "partial",
        media_max_mb: 100,
        app_id: "",
        app_secret: "",
        encrypt_key: "",
        verification_token: "",
      });
      onSuccess();
    } catch (err) {
      const message = err instanceof Error ? err.message : "创建 Channel 失败";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold">
            创建 Channel
          </DialogTitle>
        </DialogHeader>

        <ChannelForm
          data={formData}
          onChange={setFormData}
          isNew
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
            创建
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
