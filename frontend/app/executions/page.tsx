"use client";

import { useState, useEffect } from "react";
import { apiClient, Execution, PaginatedResponse, Template } from "@/lib/api-client";
import { ExecutionList } from "@/components/executions/execution-list";
import { StartExecutionDialog } from "@/components/executions/start-execution-dialog";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

const statusConfig = [
  { value: "all", label: "全部状态", icon: "📊", color: "from-zinc-500" },
  { value: "pending", label: "等待中", icon: "⏳", color: "from-amber-500" },
  { value: "running", label: "运行中", icon: "🏃", color: "from-emerald-500" },
  { value: "completed", label: "已完成", icon: "✅", color: "from-blue-500" },
  { value: "failed", label: "失败", icon: "❌", color: "from-red-500" },
  { value: "cancelled", label: "已取消", icon: "🚫", color: "from-zinc-400" },
];

export default function ExecutionsPage() {
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [startOpen, setStartOpen] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>("all");

  const loadExecutions = async () => {
    setLoading(true);
    setError(null);
    try {
      let url = "/api/executions";
      if (statusFilter && statusFilter !== "all") {
        url += `?status=${statusFilter}`;
      }
      const data: PaginatedResponse<Execution> = await apiClient.get(url);
      setExecutions(data.items || []);
    } catch (err) {
      const message = err instanceof Error ? err.message : "加载执行列表失败";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const loadTemplates = async () => {
    try {
      const data: PaginatedResponse<Template> = await apiClient.get("/api/templates");
      setTemplates(data.items || []);
    } catch {
      // Templates are optional, don't show error
    }
  };

  useEffect(() => {
    loadExecutions();
    loadTemplates();
  }, [statusFilter]);

  useEffect(() => {
    const ws = apiClient.createWebSocket((data) => {
      if (data && typeof data === 'object' && 'type' in data) {
        const msg = data as { type: string };
        if (msg.type === "execution_update") {
          loadExecutions();
        }
      }
    });

    return () => ws.close();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* 装饰性背景光晕 */}
      <div className="fixed inset-0 bg-zinc-50 dark:bg-zinc-950 pointer-events-none">
        <div className="absolute top-0 right-1/4 w-[500px] h-[500px] bg-gradient-to-br from-emerald-500/20 via-teal-500/10 to-transparent rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-1/4 w-[500px] h-[500px] bg-gradient-to-tr from-cyan-500/15 via-blue-500/10 to-transparent rounded-full blur-3xl" />
      </div>

      <div className="container mx-auto px-4 py-8 relative">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-black tracking-tight
              bg-gradient-to-r from-emerald-600 via-teal-500 to-cyan-400
              bg-clip-text text-transparent drop-shadow-lg">
              执行监控
            </h1>
            <p className="text-zinc-500 mt-1">实时监控 SOP 流程执行状态</p>
          </div>

          <Button
            onClick={() => setStartOpen(true)}
            className={cn(
              "h-11 px-6 text-base font-bold rounded-xl",
              "bg-gradient-to-r from-emerald-500 to-teal-500",
              "hover:from-emerald-600 hover:to-teal-600",
              "text-white shadow-[0_0_25px_rgba(16,185,129,0.4)]",
              "hover:shadow-[0_0_35px_rgba(16,185,129,0.6)]",
              "transition-all duration-300 hover:scale-[1.02]"
            )}
          >
            <span className="mr-2">🚀</span>
            启动执行
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-5 gap-3 mb-8">
          {statusConfig.map((status) => {
            const count = status.value === "all"
              ? executions.length
              : executions.filter(e => e.status === status.value).length;

            return (
              <button
                key={status.value}
                onClick={() => setStatusFilter(status.value)}
                className={cn(
                  "relative overflow-hidden rounded-xl p-3 text-left",
                  "transition-all duration-300 hover:scale-[1.02]",
                  "bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl",
                  "border",
                  statusFilter === status.value
                    ? "border-emerald-300 dark:border-emerald-700 shadow-lg"
                    : "border-zinc-200/50 dark:border-zinc-700/50",
                  statusFilter === status.value && `shadow-[0_0_20px_rgba(16,185,129,0.3)]`
                )}
              >
                <div className={cn(
                  "absolute inset-0 opacity-10 bg-gradient-to-br",
                  status.color
                )} />
                <div className="relative flex items-center gap-2">
                  <span className="text-lg">{status.icon}</span>
                  <div>
                    <div className="text-xl font-bold text-zinc-900 dark:text-white">{count}</div>
                    <div className="text-xs text-zinc-500">{status.label}</div>
                  </div>
                </div>
              </button>
            );
          })}
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
              <Button onClick={loadExecutions} variant="outline">
                重试
              </Button>
            </div>
          ) : (
            <ExecutionList
              executions={executions}
              templates={templates}
              loading={loading}
              onRefresh={loadExecutions}
            />
          )}
        </div>

        <StartExecutionDialog
          open={startOpen}
          onOpenChange={setStartOpen}
          templates={templates}
          onSuccess={() => {
            setStartOpen(false);
            loadExecutions();
          }}
        />
      </div>
    </div>
  );
}
