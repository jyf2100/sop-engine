"use client";

import { useState, useEffect } from "react";
import { apiClient, PendingApproval, PendingApprovalListResponse } from "@/lib/api-client";
import { ApprovalList } from "@/components/approvals/approval-list";
import { cn } from "@/lib/utils";

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<PendingApproval[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadApprovals = async () => {
    setLoading(true);
    setError(null);
    try {
      const data: PendingApprovalListResponse = await apiClient.get("/api/approvals/pending");
      setApprovals(data.items || []);
    } catch (err) {
      const message = err instanceof Error ? err.message : "加载审批列表失败";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadApprovals();

    // WebSocket for real-time updates
    const ws = apiClient.createWebSocket((data) => {
      if (data && typeof data === 'object' && 'type' in data) {
        const msg = data as { type: string };
        if (msg.type === "approval_update") {
          loadApprovals();
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
        <div className="absolute top-0 right-1/4 w-[500px] h-[500px] bg-gradient-to-br from-amber-500/20 via-orange-500/10 to-transparent rounded-full blur-3xl" />
        <div className="absolute bottom-0 left-1/4 w-[500px] h-[500px] bg-gradient-to-tr from-cyan-500/15 via-blue-500/10 to-transparent rounded-full blur-3xl" />
      </div>

      <div className="container mx-auto px-4 py-8 relative">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-black tracking-tight bg-gradient-to-r from-amber-600 via-orange-500 to-cyan-400 bg-clip-text text-transparent">
              定用审批工作台
            </h1>
            <p className="text-zinc-500 mt-1">
              处理待审批的人工节点
            </p>
          </div>

          <div className="flex items-center gap-4">
            <span className="px-3 py-1.5 text-xs font-bold rounded-full bg-zinc-900/5 dark:bg-white/5 backdrop-blur-sm border border-zinc-200/50 dark:border-zinc-700/50">
              {approvals.length}
            </span>
          </div>
        </div>

        {/* Main Content */}
        <div
          className={cn(
            "rounded-2xl overflow-hidden",
            "bg-white/80 dark:bg-zinc-900/80 backdrop-blur-xl",
            "border border-zinc-200/50 dark:border-zinc-700/50",
            "shadow-xl"
          )}
        >
          {error ? (
            <div className="p-8 text-center">
              <p className="text-red-500 mb-4">{error}</p>
              <p className="text-zinc-400 text-sm mb-4">请确保后端服务已启动</p>
              <button
                onClick={loadApprovals}
                className="px-4 py-2 bg-amber-500 text-white rounded-lg hover:bg-amber-600 transition-colors"
              >
                重试
              </button>
            </div>
          ) : (
            <ApprovalList
              approvals={approvals}
              loading={loading}
              onRefresh={loadApprovals}
            />
          )}
        </div>
      </div>
    </div>
  );
}
