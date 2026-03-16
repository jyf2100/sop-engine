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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

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
  const [name, setName] = useState("");
  const [workspacePath, setWorkspacePath] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await apiClient.post("/api/agents", {
        name,
        workspace_path: workspacePath,
        llm_config: {},
        sandbox_config: {},
        tools_config: {},
      });
      onSuccess();
      // Reset form
      setName("");
      setWorkspacePath("");
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("创建 Agent 失败");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>创建 Agent</DialogTitle>
          <DialogDescription>
            创建一个新的 OpenClaw Agent。
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="name" className="text-right">
                名称
              </Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="col-span-3"
                required
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="workspace" className="text-right">
                工作目录
              </Label>
              <Input
                id="workspace"
                value={workspacePath}
                onChange={(e) => setWorkspacePath(e.target.value)}
                className="col-span-3"
                placeholder="/path/to/workspace"
                required
              />
            </div>
            {error && (
              <div className="col-span-4 text-sm text-red-500 text-center">
                {error}
              </div>
            )}
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
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
