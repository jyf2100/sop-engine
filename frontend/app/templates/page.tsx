"use client";

import { useState, useEffect, useRef } from "react";
import { apiClient, Template, PaginatedResponse } from "@/lib/api-client";
import { TemplateList } from "@/components/templates/template-list";
import { CreateTemplateDialog } from "@/components/templates/create-template-dialog";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";
import { cn } from "@/lib/utils";

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { toast } = useToast();

  const loadTemplates = async () => {
    setLoading(true);
    setError(null);
    try {
      const data: PaginatedResponse<Template> = await apiClient.get("/api/templates");
      setTemplates(data.items || []);
    } catch (err) {
      const message = err instanceof Error ? err.message : "加载模板列表失败";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTemplates();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const maxSize = 1 * 1024 * 1024;
    if (file.size > maxSize) {
      toast({ type: "error", message: "文件大小不能超过 1MB" });
      return;
    }

    setUploading(true);
    try {
      const content = await file.text();
      const template = await apiClient.post<Template>("/api/templates/upload", content);
      toast({ type: "success", message: `模板 "${template.name}" 上传成功` });
      loadTemplates();
    } catch (error) {
      console.error("Failed to upload template:", error);
      toast({ type: "error", message: "上传失败，请检查 YAML 格式" });
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* 装饰性背景光晕 */}
      <div className="fixed inset-0 bg-zinc-50 dark:bg-zinc-950 pointer-events-none">
        <div className="absolute top-0 left-1/3 w-[500px] h-[500px] bg-gradient-to-br from-blue-500/20 via-cyan-500/10 to-transparent rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/3 w-[500px] h-[500px] bg-gradient-to-tr from-teal-500/15 via-emerald-500/10 to-transparent rounded-full blur-3xl" />
      </div>

      <div className="container mx-auto px-4 py-8 relative">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-black tracking-tight
              bg-gradient-to-r from-blue-600 via-cyan-500 to-teal-400
              bg-clip-text text-transparent">
              流程模板
            </h1>
            <p className="text-zinc-500 mt-1">管理和编辑 YAML 流程模板</p>
          </div>
          <div className="flex gap-3">
            <input
              ref={fileInputRef}
              type="file"
              accept=".yaml,.yml"
              onChange={handleFileUpload}
              className="hidden"
              id="yaml-upload"
            />
            <Button
              variant="outline"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
              className={cn(
                "h-11 px-5 rounded-xl font-semibold",
                "border-2 border-cyan-200 dark:border-cyan-800/50",
                "hover:bg-cyan-50 dark:hover:bg-cyan-900/20",
                "text-cyan-700 dark:text-cyan-300"
              )}
            >
              {uploading ? (
                <span className="flex items-center gap-2">
                  <span className="animate-spin">⏳</span>
                  上传中...
                </span>
              ) : (
                <span>📤 上传 YAML</span>
              )}
            </Button>
            <Button
              onClick={() => setCreateOpen(true)}
              className={cn(
                "h-11 px-6 text-base font-bold rounded-xl",
                "bg-gradient-to-r from-blue-600 via-cyan-500 to-teal-400",
                "hover:from-blue-700 hover:via-cyan-600 hover:to-teal-500",
                "text-white shadow-[0_0_25px_rgba(6,182,212,0.4)]",
                "hover:shadow-[0_0_35px_rgba(6,182,212,0.6)]",
                "transition-all duration-300 hover:scale-[1.02]",
                "border-0"
              )}
            >
              <span className="mr-2">✨</span>
              创建模板
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 mb-8">
          {[
            { label: "总模板", value: templates.length, icon: "📋", color: "from-blue-500 to-cyan-500" },
            { label: "最新更新", value: templates.filter(t => t.updated_at && Date.now() - new Date(t.updated_at).getTime() < 7 * 24 * 60 * 60 * 1000).length, icon: "🕐", color: "from-violet-500 to-fuchsia-500" },
          ].map((stat) => (
            <div
              key={stat.label}
              className={cn(
                "relative overflow-hidden rounded-2xl p-4",
                "bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl",
                "border border-zinc-200/50 dark:border-zinc-700/50",
                "hover:shadow-lg transition-all duration-300"
              )}
            >
              <div className={cn(
                "absolute inset-0 opacity-10 bg-gradient-to-br",
                stat.color
              )} />
              <div className="relative flex items-center gap-3">
                <span className="text-2xl">{stat.icon}</span>
                <div>
                  <div className="text-2xl font-bold text-zinc-900 dark:text-white">{stat.value}</div>
                  <div className="text-xs text-zinc-500">{stat.label}</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Main Content */}
        <div className={cn(
          "rounded-2xl overflow-hidden",
          "bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl",
          "border border-zinc-200/50 dark:border-zinc-700/50",
          "shadow-xl"
        )}>
          {error ? (
            <div className="p-8 text-center">
              <span className="text-5xl mb-4 block">⚠️</span>
              <p className="text-red-500 mb-2">{error}</p>
              <p className="text-zinc-400 text-sm mb-4">请确保后端服务已启动</p>
              <Button onClick={loadTemplates} variant="outline">
                重试
              </Button>
            </div>
          ) : (
            <TemplateList
              templates={templates}
              loading={loading}
              onRefresh={loadTemplates}
            />
          )}
        </div>

        <CreateTemplateDialog
          open={createOpen}
          onOpenChange={setCreateOpen}
          onSuccess={() => {
            setCreateOpen(false);
            loadTemplates();
          }}
        />
      </div>
    </div>
  );
}
