"use client";

import { useState } from "react";
import { apiClient } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { useToast } from "@/components/ui/toast";
import { AgentForm, createFormDataFromAgent, createApiPayloadFromFormData, AgentFormData } from "./agent-form";

interface CreateAgentDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function CreateAgentDialog({
  open,
  onOpenChange,
  onSuccess,
}: CreateAgentDialogProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<AgentFormData>(createFormDataFromAgent());
  const { toast } = useToast();

  const handleClose = () => {
    // 重置表单
    setFormData(createFormDataFromAgent());
    setError(null);
    onOpenChange(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim()) {
      setError("请输入 Agent 名称");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const payload = createApiPayloadFromFormData(formData);
      // 生成 ID（使用名称的 slug 形式）
      const slugId = formData.name
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-|-$/g, "");

      await apiClient.post("/api/agents", {
        ...payload,
        id: slugId || `agent-${Date.now()}`,
      });
      toast({ type: "success", message: "Agent 创建成功" });
      handleClose();
      onSuccess();
    } catch (err) {
      const message = err instanceof Error ? err.message : "创建 Agent 失败";
      setError(message);
      toast({ type: "error", message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>创建 Agent</DialogTitle>
          <DialogDescription>
            创建一个新的 OpenClaw Agent。配置各个选项后点击创建。
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="py-4">
            <AgentForm
              mode="create"
              data={formData}
              onChange={setFormData}
            />
          </div>

          {error && (
            <div className="text-sm text-red-500 text-center mb-4">
              {error}
            </div>
          )}

          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={handleClose}
            >
              取消
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "创建中..." : "创建"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
