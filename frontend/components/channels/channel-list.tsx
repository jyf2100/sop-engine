"use client";

import { useState } from "react";
import { ChannelConfig, apiClient } from "@/lib/api-client";
import { EditChannelDialog } from "./edit-channel-dialog";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Loader2 } from "lucide-react";

interface ChannelListProps {
  channels: ChannelConfig[];
  loading: boolean;
  onRefresh: () => void;
}

export function ChannelList({ channels, loading, onRefresh }: ChannelListProps) {
  const [editChannel, setEditChannel] = useState<ChannelConfig | null>(null);
  const [deleteChannel, setDeleteChannel] = useState<ChannelConfig | null>(null);
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async () => {
    if (!deleteChannel) return;

    setDeleting(true);
    try {
      await apiClient.delete(`/api/channels/${deleteChannel.id}`);
      setDeleteChannel(null);
      onRefresh();
    } catch (err) {
      console.error("Failed to delete channel:", err);
    } finally {
      setDeleting(false);
    }
  };

  const getChannelIcon = (type: string) => {
    const icons: Record<string, string> = {
      telegram: "📱",
      whatsapp: "💬",
      feishu: "🔶",
      discord: "🎮",
      slack: "💼",
    };
    return icons[type] || "📡";
  };

  const getChannelTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      telegram: "Telegram",
      whatsapp: "WhatsApp",
      feishu: "飞书",
      discord: "Discord",
      slack: "Slack",
    };
    return labels[type] || type;
  };

  // 检查是否配置了凭据
  const hasCredentials = (channel: ChannelConfig) => {
    if (channel.type === "telegram") return channel.has_bot_token;
    if (channel.type === "whatsapp") return channel.has_phone_id;
    if (channel.type === "feishu") return channel.has_app_id;
    return false;
  };

  if (loading) {
    return (
      <div className="p-8 text-center">
        <Loader2 className="h-8 w-8 animate-spin mx-auto text-zinc-400" />
        <p className="text-zinc-500 mt-2">加载中...</p>
      </div>
    );
  }

  if (channels.length === 0) {
    return (
      <div className="p-8 text-center">
        <span className="text-5xl mb-4 block">📡</span>
        <p className="text-zinc-500 mb-2">暂无 Channel 配置</p>
        <p className="text-zinc-400 text-sm">点击右上角按钮创建第一个 Channel</p>
      </div>
    );
  }

  return (
    <>
      <div className="divide-y divide-zinc-200/50 dark:divide-zinc-700/50">
        {channels.map((channel) => (
          <div
            key={channel.id}
            className={cn(
              "p-4 flex items-center justify-between",
              "hover:bg-zinc-50/50 dark:hover:bg-zinc-800/50",
              "transition-colors duration-200"
            )}
          >
            <div className="flex items-center gap-4">
              <div className={cn(
                "w-12 h-12 rounded-xl flex items-center justify-center text-2xl",
                channel.enabled
                  ? "bg-gradient-to-br from-cyan-500/20 to-blue-500/20"
                  : "bg-zinc-100 dark:bg-zinc-800"
              )}>
                {getChannelIcon(channel.type)}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-zinc-900 dark:text-white">
                    {channel.name}
                  </span>
                  <span className={cn(
                    "px-2 py-0.5 rounded-full text-xs font-medium",
                    channel.enabled
                      ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
                      : "bg-zinc-100 text-zinc-600 dark:bg-zinc-800 dark:text-zinc-400"
                  )}>
                    {channel.enabled ? "已启用" : "已禁用"}
                  </span>
                </div>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-sm text-zinc-500">
                    {getChannelTypeLabel(channel.type)}
                  </span>
                  <span className="text-zinc-300 dark:text-zinc-600">•</span>
                  <span className="text-sm text-zinc-500 font-mono">
                    {channel.id}
                  </span>
                  {hasCredentials(channel) && (
                    <>
                      <span className="text-zinc-300 dark:text-zinc-600">•</span>
                      <span className="text-sm text-emerald-600 dark:text-emerald-400">
                        已配置凭据
                      </span>
                    </>
                  )}
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setEditChannel(channel)}
                className="text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-white"
              >
                编辑
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setDeleteChannel(channel)}
                className="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
              >
                删除
              </Button>
            </div>
          </div>
        ))}
      </div>

      <EditChannelDialog
        channel={editChannel}
        open={!!editChannel}
        onOpenChange={(open) => !open && setEditChannel(null)}
        onSuccess={() => {
          setEditChannel(null);
          onRefresh();
        }}
      />

      <AlertDialog open={!!deleteChannel} onOpenChange={(open) => !open && setDeleteChannel(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>确认删除</AlertDialogTitle>
            <AlertDialogDescription>
              确定要删除 Channel &quot;{deleteChannel?.name}&quot; 吗？此操作无法撤销。
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleting}>取消</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDelete}
              disabled={deleting}
              className="bg-red-600 hover:bg-red-700"
            >
              {deleting ? "删除中..." : "删除"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
