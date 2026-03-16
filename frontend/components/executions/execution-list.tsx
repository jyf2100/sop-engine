"use client";

import { Execution } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useState } from "react";
import { apiClient } from "@/lib/api-client";

interface ExecutionListProps {
  executions: Execution[];
  loading: boolean;
  onRefresh: () => void;
}

const statusColors: Record<string, string> = {
  pending: "text-gray-500",
  running: "text-blue-500",
  paused: "text-yellow-500",
  completed: "text-green-500",
  failed: "text-red-500",
  cancelled: "text-gray-400",
};

export function ExecutionList({
  executions,
  loading,
  onRefresh,
}: ExecutionListProps) {
  const [detailOpen, setDetailOpen] = useState(false);
  const [cancelOpen, setCancelOpen] = useState(false);
  const [selectedExecution, setSelectedExecution] = useState<Execution | null>(
    null
  );

  const handleCancel = async () => {
    if (!selectedExecution) return;
    try {
      await apiClient.post(`/api/executions/${selectedExecution.id}/cancel`);
      setCancelOpen(false);
      onRefresh();
    } catch (error) {
      console.error("Failed to cancel execution:", error);
    }
  };

  const canCancel = (status: string) => {
    return status === "pending" || status === "running" || status === "paused";
  };

  if (loading) {
    return <div className="text-center py-8">加载中...</div>;
  }

  if (executions.length === 0) {
    return <div className="text-center py-8 text-zinc-500">暂无执行记录</div>;
  }

  return (
    <>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>ID</TableHead>
            <TableHead>模板</TableHead>
            <TableHead>状态</TableHead>
            <TableHead>开始时间</TableHead>
            <TableHead className="text-right">操作</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {executions.map((execution) => (
            <TableRow key={execution.id}>
              <TableCell className="font-mono text-sm">
                {execution.id?.substring(0, 8)}...
              </TableCell>
              <TableCell>{execution.template_id || "-"}</TableCell>
              <TableCell>
                <span className={statusColors[execution.status] || ""}>
                  {execution.status}
                </span>
              </TableCell>
              <TableCell>
                {execution.started_at
                  ? new Date(execution.started_at).toLocaleString()
                  : "-"}
              </TableCell>
              <TableCell className="text-right space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setSelectedExecution(execution);
                    setDetailOpen(true);
                  }}
                >
                  详情
                </Button>
                {canCancel(execution.status) && (
                  <Button
                    variant="destructive"
                    size="sm"
                    onClick={() => {
                      setSelectedExecution(execution);
                      setCancelOpen(true);
                    }}
                  >
                    取消
                  </Button>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {/* 详情对话框 */}
      <Dialog open={detailOpen} onOpenChange={setDetailOpen}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>执行详情</DialogTitle>
            <DialogDescription>
              ID: {selectedExecution?.id}
              <br />
              状态: {selectedExecution?.status}
            </DialogDescription>
          </DialogHeader>
          <div className="mt-4 space-y-4">
            <div>
              <h4 className="font-medium mb-2">输入参数</h4>
              <pre className="bg-zinc-100 dark:bg-zinc-800 p-4 rounded-md overflow-auto text-sm">
                {JSON.stringify(selectedExecution?.input_params || {}, null, 2)}
              </pre>
            </div>
            <div>
              <h4 className="font-medium mb-2">输出结果</h4>
              <pre className="bg-zinc-100 dark:bg-zinc-800 p-4 rounded-md overflow-auto text-sm">
                {JSON.stringify(selectedExecution?.output || {}, null, 2)}
              </pre>
            </div>
            {selectedExecution?.error && (
              <div>
                <h4 className="font-medium mb-2 text-red-500">错误信息</h4>
                <pre className="bg-red-50 dark:bg-red-900/20 p-4 rounded-md overflow-auto text-sm text-red-600">
                  {selectedExecution.error}
                </pre>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>

      {/* 取消确认对话框 */}
      <Dialog open={cancelOpen} onOpenChange={setCancelOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>确认取消</DialogTitle>
            <DialogDescription>
              确定要取消此执行吗？此操作不可撤销。
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCancelOpen(false)}>
              返回
            </Button>
            <Button variant="destructive" onClick={handleCancel}>
              取消执行
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
