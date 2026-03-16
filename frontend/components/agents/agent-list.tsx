"use client";

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
import { useState } from "react";
import { apiClient } from "@/lib/api-client";

interface AgentListProps {
  agents: Agent[];
  loading: boolean;
  onRefresh: () => void;
}

export function AgentList({ agents, loading, onRefresh }: AgentListProps) {
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);

  const handleDelete = async () => {
    if (!selectedAgent) return;
    try {
      await apiClient.delete(`/api/agents/${selectedAgent.id}`);
      setDeleteOpen(false);
      onRefresh();
    } catch (error) {
      console.error("Failed to delete agent:", error);
    }
  };

  const handleSync = async (agentId: string) => {
    try {
      await apiClient.post(`/api/agents/${agentId}/sync`);
      onRefresh();
    } catch (error) {
      console.error("Failed to sync agent:", error);
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
            <TableHead>创建时间</TableHead>
            <TableHead className="text-right">操作</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {agents.map((agent) => (
            <TableRow key={agent.id}>
              <TableCell className="font-medium">{agent.name}</TableCell>
              <TableCell className="font-mono text-sm">
                {agent.workspace_path}
              </TableCell>
              <TableCell>
                {agent.is_active ? (
                  <span className="text-green-500">活跃</span>
                ) : (
                  <span className="text-gray-400">停用</span>
                )}
              </TableCell>
              <TableCell>
                {agent.created_at
                  ? new Date(agent.created_at).toLocaleString()
                  : "-"}
              </TableCell>
              <TableCell className="text-right space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setSelectedAgent(agent);
                    setDetailOpen(true);
                  }}
                >
                  详情
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleSync(agent.id)}
                >
                  同步
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => {
                    setSelectedAgent(agent);
                    setDeleteOpen(true);
                  }}
                >
                  删除
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {/* 详情对话框 */}
      <Dialog open={detailOpen} onOpenChange={setDetailOpen}>
        <DialogContent className="max-w-3xl">
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
