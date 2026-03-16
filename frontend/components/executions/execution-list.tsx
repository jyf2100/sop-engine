"use client";

import { Execution, Template, NodeExecution, PaginatedResponse } from "@/lib/api-client";
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
import { useState, useEffect, useCallback } from "react";
import { apiClient } from "@/lib/api-client";
import { useToast } from "@/components/ui/toast";

interface ExecutionListProps {
  executions: Execution[];
  templates: Template[];
  loading: boolean;
  onRefresh: () => void;
}

const statusColors: Record<string, string> = {
  pending: "text-gray-500 bg-gray-100",
  running: "text-blue-500 bg-blue-100",
  paused: "text-yellow-500 bg-yellow-100",
  completed: "text-green-500 bg-green-100",
  failed: "text-red-500 bg-red-100",
  cancelled: "text-gray-400 bg-gray-100",
};

const statusLabels: Record<string, string> = {
  pending: "等待中",
  running: "运行中",
  paused: "已暂停",
  completed: "已完成",
  failed: "失败",
  cancelled: "已取消",
};

export function ExecutionList({
  executions,
  templates,
  loading,
  onRefresh,
}: ExecutionListProps) {
  const [detailOpen, setDetailOpen] = useState(false);
  const [cancelOpen, setCancelOpen] = useState(false);
  const [selectedExecution, setSelectedExecution] = useState<Execution | null>(
    null
  );
  const [nodeExecutions, setNodeExecutions] = useState<NodeExecution[]>([]);
  const [loadingNodes, setLoadingNodes] = useState(false);
  const { toast } = useToast();

  const handleCancel = async () => {
    if (!selectedExecution) return;
    try {
      await apiClient.post(`/api/executions/${selectedExecution.id}/cancel`);
      setCancelOpen(false);
      toast({ type: "success", message: "执行已取消" });
      onRefresh();
    } catch (error) {
      const message = error instanceof Error ? error.message : "取消执行失败";
      toast({ type: "error", message });
    }
  };

  const handleViewDetail = useCallback(async (execution: Execution) => {
    setSelectedExecution(execution);
    setDetailOpen(true);

    setLoadingNodes(true);
    try {
      const data: PaginatedResponse<NodeExecution> = await apiClient.get(
        `/api/executions/${execution.id}/nodes`
      );
      setNodeExecutions(data.items || []);
    } catch (error) {
      const message = error instanceof Error ? error.message : "加载节点执行失败";
      toast({ type: "error", message });
      setNodeExecutions([]);
    } finally {
      setLoadingNodes(false);
    }
  }, [toast]);

  const canCancel = (status: string) => {
    return status === "pending" || status === "running" || status === "paused";
  };

  const getTemplateName = (templateId: string) => {
    const template = templates.find((t) => t.id === templateId);
    return template ? `${template.name} (v${template.version})` : templateId;
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
            <TableHead>完成时间</TableHead>
            <TableHead className="text-right">操作</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {executions.map((execution) => (
            <TableRow key={execution.id}>
              <TableCell className="font-mono text-sm">
                {execution.id?.substring(0, 8)}...
              </TableCell>
              <TableCell>{getTemplateName(execution.template_id)}</TableCell>
              <TableCell>
                <span
                  className={`px-2 py-1 rounded-full text-xs font-medium ${
                    statusColors[execution.status] || ""
                  }`}
                >
                  {statusLabels[execution.status] || execution.status}
                </span>
              </TableCell>
              <TableCell>
                {execution.started_at
                  ? new Date(execution.started_at).toLocaleString()
                  : "-"}
              </TableCell>
              <TableCell>
                {execution.completed_at
                  ? new Date(execution.completed_at).toLocaleString()
                  : "-"}
              </TableCell>
              <TableCell className="text-right space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleViewDetail(execution)}
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
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>执行详情</DialogTitle>
            <DialogDescription>
              ID: {selectedExecution?.id}
              <br />
              状态: {statusLabels[selectedExecution?.status || ""] || selectedExecution?.status}
            </DialogDescription>
          </DialogHeader>
          <div className="mt-4 space-y-4">
            <div>
              <h4 className="font-medium mb-2">输入参数</h4>
              <pre className="bg-zinc-100 dark:bg-zinc-800 p-4 rounded-md overflow-auto text-sm">
                {JSON.stringify(selectedExecution?.params || {}, null, 2)}
              </pre>
            </div>

            <div>
              <h4 className="font-medium mb-2">节点执行</h4>
              {loadingNodes ? (
                <div className="text-center py-4">加载中...</div>
              ) : nodeExecutions.length === 0 ? (
                <div className="text-center py-4 text-zinc-500">暂无节点执行记录</div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>节点ID</TableHead>
                      <TableHead>状态</TableHead>
                      <TableHead>开始时间</TableHead>
                      <TableHead>完成时间</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {nodeExecutions.map((node) => (
                      <TableRow key={node.id}>
                        <TableCell>{node.node_id}</TableCell>
                        <TableCell>
                          <span
                            className={`px-2 py-1 rounded-full text-xs font-medium ${
                              statusColors[node.status] || ""
                            }`}
                          >
                            {statusLabels[node.status] || node.status}
                          </span>
                        </TableCell>
                        <TableCell>
                          {node.started_at
                            ? new Date(node.started_at).toLocaleString()
                            : "-"}
                        </TableCell>
                        <TableCell>
                          {node.completed_at
                            ? new Date(node.completed_at).toLocaleString()
                            : "-"}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
            </div>
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
