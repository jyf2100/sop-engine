"use client";

import { useState, useEffect } from "react";
import { apiClient, Agent } from "@/lib/api-client";
import { AgentList } from "@/components/agents/agent-list";
import { CreateAgentDialog } from "@/components/agents/create-agent-dialog";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createOpen, setCreateOpen] = useState(false);

  const loadAgents = async () => {
    setLoading(true);
    setError(null);
    try {
      const data: Agent[] = await apiClient.get("/api/agents");
      setAgents(data || []);
    } catch (err) {
      const message = err instanceof Error ? err.message : "加载 Agent 列表失败";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAgents();
  }, []);

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* 装饰性背景光晕 */}
      <div className="fixed inset-0 bg-zinc-50 dark:bg-zinc-950 pointer-events-none">
        <div className="absolute top-0 right-1/4 w-[500px] h-[500px] bg-gradient-to-br from-violet-500/20 via-purple-500/10 to-transparent rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-1/4 w-[500px] h-[500px] bg-gradient-to-tr from-fuchsia-500/15 via-pink-500/10 to-transparent rounded-full blur-3xl" />
      </div>

      <div className="container mx-auto px-4 py-8 relative">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-black tracking-tight
              bg-gradient-to-r from-violet-600 via-purple-500 to-fuchsia-500
              bg-clip-text text-transparent">
              Agent 管理
            </h1>
            <p className="text-zinc-500 mt-1">配置和管理 OpenClaw Agent 实例</p>
          </div>
          <Button
            onClick={() => setCreateOpen(true)}
            className={cn(
              "h-11 px-6 text-base font-bold rounded-xl",
              "bg-gradient-to-r from-violet-600 via-purple-500 to-fuchsia-500",
              "hover:from-violet-700 hover:via-purple-600 hover:to-fuchsia-600",
              "text-white shadow-[0_0_25px_rgba(139,92,246,0.4)]",
              "hover:shadow-[0_0_35px_rgba(139,92,246,0.6)]",
              "transition-all duration-300 hover:scale-[1.02]",
              "border-0"
            )}
          >
            <span className="mr-2">✨</span>
            创建 Agent
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          {[
            { label: "总 Agent", value: agents.length, icon: "🤖", color: "from-violet-500 to-purple-500" },
            { label: "活跃", value: agents.filter(a => a.is_active).length, icon: "✅", color: "from-emerald-500 to-teal-500" },
            { label: "默认", value: agents.filter(a => a.is_default).length, icon: "⭐", color: "from-amber-500 to-orange-500" },
            { label: "非活跃", value: agents.filter(a => !a.is_active).length, icon: "💤", color: "from-zinc-400 to-zinc-500" },
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
              <Button onClick={loadAgents} variant="outline">
                重试
              </Button>
            </div>
          ) : (
            <AgentList
              agents={agents}
              loading={loading}
              onRefresh={loadAgents}
            />
          )}
        </div>

        <CreateAgentDialog
          open={createOpen}
          onOpenChange={setCreateOpen}
          onSuccess={() => {
            setCreateOpen(false);
            loadAgents();
          }}
        />
      </div>
    </div>
  );
}
