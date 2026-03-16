"use client";

import { useState } from "react";
import { Agent } from "@/lib/api-client";
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
import { EditAgentDialog } from "./edit-agent-dialog";
import { apiClient } from "@/lib/api-client";
import { useToast } from "@/components/ui/toast";
import { Pencil, RefreshCw, Trash2, Eye } from "lucide-react";

interface AgentListProps {
  agents: Agent[];
  loading: boolean;
  onRefresh: () => void;
}

export function AgentList({ agents, loading, onRefresh }: AgentListProps) {
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [syncing, setSyncing] = useState<string | null>(null);
  const { toast } = useToast();

  const handleDelete = async () => {
    if (!selectedAgent) return;
    try {
      await apiClient.delete(`/api/agents/${selectedAgent.id}`);
      setDeleteOpen(false);
      toast({ type: "success", message: "Agent 已删除" });
      onRefresh();
    } catch (error) {
      const message = error instanceof Error ? error.message : "删除 Agent 失败";
      toast({ type: "error", message });
    }
  };

  const handleSync = async (agentId: string) => {
    setSyncing(agentId);
    try {
      await apiClient.post(`/api/agents/${agentId}/sync`);
      toast({ type: "success", message: "Agent 同步成功" });
      onRefresh();
    } catch (error) {
      const message = error instanceof Error ? error.message : "同步 Agent 失败";
      toast({ type: "error", message });
    } finally {
      setSyncing(null);
    }
  };

  if (loading) {
    return <div className="text-center py-8">加载中...</div>;
  }

  if (agents.length === 0) {
    return <div className="text-center py-8 text-zinc-500">暂无 Agent</div>;
  }

  return (
    <>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>名称</TableHead>
            <TableHead>工作目录</TableHead>
            <TableHead>状态</TableHead>
            <TableHead>主模型</TableHead>
            <TableHead>创建时间</TableHead>
            <TableHead className="text-right">操作</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {agents.map((agent) => (
            <TableRow key={agent.id}>
              <TableCell className="font-medium">
                {agent.name}
                {agent.is_default && (
                  <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                    默认
                  </span>
                )}
              </TableCell>
              <TableCell className="font-mono text-sm truncate max-w-[200px]">
                {agent.workspace_path}
              </TableCell>
              <TableCell>
                {agent.is_active ? (
                  <span className="text-green-600 bg-green-100 px-2 py-1 rounded-full text-xs">
                    活跃
                  </span>
                ) : (
                  <span className="text-gray-500 bg-gray-100 px-2 py-1 rounded-full text-xs">
                    停用
                  </span>
                )}
              </TableCell>
              <TableCell className="text-sm">
                {(agent.llm_config?.primary as string) || "-"}
              </TableCell>
              <TableCell className="text-sm">
                {agent.created_at
                  ? new Date(agent.created_at).toLocaleDateString()
                  : "-"}
              </TableCell>
              <TableCell className="text-right">
                <div className="flex justify-end gap-1">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setSelectedAgent(agent);
                      setDetailOpen(true);
                    }}
                    title="查看详情"
                  >
                    <Eye className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setSelectedAgent(agent);
                      setEditOpen(true);
                    }}
                    title="编辑"
                  >
                    <Pencil className="h-4 w-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleSync(agent.id)}
                    disabled={syncing === agent.id}
                    title="同步"
                  >
                    <RefreshCw className={`h-4 w-4 ${syncing === agent.id ? "animate-spin" : ""}`} />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-red-500 hover:text-red-700"
                    onClick={() => {
                      setSelectedAgent(agent);
                      setDeleteOpen(true);
                    }}
                    title="删除"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {/* 详情对话框 */}
      <Dialog open={detailOpen} onOpenChange={setDetailOpen}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{selectedAgent?.name}</DialogTitle>
            <DialogDescription>
              工作目录: {selectedAgent?.workspace_path}
            </DialogDescription>
          </DialogHeader>
          <div className="mt-4 space-y-4">
            <div>
              <h4 className="font-medium mb-2">LLM 配置</h4>
              <pre className="bg-zinc-100 dark:bg-zinc-800 p-4 rounded-md overflow-auto text-sm">
                {JSON.stringify(selectedAgent?.llm_config || {}, null, 2)}
              </pre>
            </div>
            <div>
              <h4 className="font-medium mb-2">沙箱配置</h4>
              <pre className="bg-zinc-100 dark:bg-zinc-800 p-4 rounded-md overflow-auto text-sm">
                {JSON.stringify(selectedAgent?.sandbox_config || {}, null, 2)}
              </pre>
            </div>
            <div>
              <h4 className="font-medium mb-2">工具配置</h4>
              <pre className="bg-zinc-100 dark:bg-zinc-800 p-4 rounded-md overflow-auto text-sm">
                {JSON.stringify(selectedAgent?.tools_config || {}, null, 2)}
              </pre>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* 编辑对话框 */}
      <EditAgentDialog
        open={editOpen}
        onOpenChange={setEditOpen}
        agent={selectedAgent}
        onSuccess={() => {
          setEditOpen(false);
          onRefresh();
        }}
      />

      {/* 删除确认对话框 */}
      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>确认删除</DialogTitle>
            <DialogDescription>
              确定要删除 Agent "{selectedAgent?.name}" 吗？此操作不可撤销。
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteOpen(false)}>
              取消
            </Button>
            <Button variant="destructive" onClick={handleDelete}>
              删除
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
