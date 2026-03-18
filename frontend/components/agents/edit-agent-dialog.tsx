"use client";

import { useState, useEffect } from "react";
import { apiClient, Agent } from "@/lib/api-client";
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

interface EditAgentDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  agent: Agent | null;
  onSuccess: () => void;
}

export function EditAgentDialog({
  open,
  onOpenChange,
  agent,
  onSuccess,
}: EditAgentDialogProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formData, setFormData] = useState<AgentFormData>(createFormDataFromAgent());
  const { toast } = useToast();

  // 当对话框打开时，重新加载表单数据
  useEffect(() => {
    if (open && agent) {
      setFormData(createFormDataFromAgent(agent));
      setError(null);
    }
  }, [open, agent]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!agent) return;

    if (!formData.name.trim()) {
      setError("请输入 Agent 名称");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const payload = createApiPayloadFromFormData(formData, agent.id);
      await apiClient.patch(`/api/agents/${agent.id}`, payload);
      toast({ type: "success", message: "Agent 更新成功" });
      onSuccess();
    } catch (err) {
      const message = err instanceof Error ? err.message : "更新 Agent 失败";
      setError(message);
      toast({ type: "error", message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>编辑 Agent</DialogTitle>
          <DialogDescription>
            修改 Agent 配置。点击保存后生效。
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="py-4">
            <AgentForm
              mode="edit"
              agent={agent || undefined}
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
              onClick={() => onOpenChange(false)}
            >
              取消
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? "保存中..." : "保存"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
