"use client";

import { PendingApproval } from "@/lib/api-client";
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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useState } from "react";
import { apiClient } from "@/lib/api-client";

interface ApprovalListProps {
  approvals: PendingApproval[];
  loading: boolean;
  onRefresh: () => void;
}

export function ApprovalList({
  approvals,
  loading,
  onRefresh,
}: ApprovalListProps) {
  const [detailOpen, setDetailOpen] = useState(false);
  const [selectedApproval, setSelectedApproval] = useState<PendingApproval | null>(null);
  const [comment, setComment] = useState("");
  const [processing, setProcessing] = useState(false);

  const handleApprove = async () => {
    if (!selectedApproval) return;
    setProcessing(true);
    try {
      await apiClient.post(
        `/api/approvals/${selectedApproval.execution_id}/${selectedApproval.node_id}`,
        { action: "approve", comment }
      );
      setDetailOpen(false);
      setComment("");
      onRefresh();
    } catch (error) {
      console.error("Failed to approve:", error);
    } finally {
      setProcessing(false);
    }
  };

  const handleReject = async () => {
    if (!selectedApproval) return;
    setProcessing(true);
    try {
      await apiClient.post(
        `/api/approvals/${selectedApproval.execution_id}/${selectedApproval.node_id}`,
        { action: "reject", comment }
      );
      setDetailOpen(false);
      setComment("");
      onRefresh();
    } catch (error) {
      console.error("Failed to reject:", error);
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8">加载中...</div>;
  }

  if (approvals.length === 0) {
    return <div className="text-center py-8 text-zinc-500">暂无待审批任务</div>;
  }

  return (
    <>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>执行ID</TableHead>
            <TableHead>节点ID</TableHead>
            <TableHead>创建时间</TableHead>
            <TableHead className="text-right">操作</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {approvals.map((approval) => (
            <TableRow key={`${approval.execution_id}-${approval.node_id}`}>
              <TableCell className="font-mono text-sm">
                {approval.execution_id?.substring(0, 8)}...
              </TableCell>
              <TableCell>{approval.node_id}</TableCell>
              <TableCell>
                {approval.created_at
                  ? new Date(approval.created_at).toLocaleString()
                  : "-"}
              </TableCell>
              <TableCell className="text-right">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setSelectedApproval(approval);
                    setDetailOpen(true);
                  }}
                >
                  处理
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {/* 审批对话框 */}
      <Dialog open={detailOpen} onOpenChange={setDetailOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>审批处理</DialogTitle>
            <DialogDescription>
              执行: {selectedApproval?.execution_id?.substring(0, 8)}...
              <br />
              节点: {selectedApproval?.node_id}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Label htmlFor="comment">审批意见（可选）</Label>
            <Input
              id="comment"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              placeholder="请输入审批意见"
              className="mt-2"
            />
          </div>
          <DialogFooter className="space-x-2">
            <Button variant="outline" onClick={() => setDetailOpen(false)}>
              取消
            </Button>
            <Button
              variant="destructive"
              onClick={handleReject}
              disabled={processing}
            >
              拒绝
            </Button>
            <Button onClick={handleApprove} disabled={processing}>
              批准
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
