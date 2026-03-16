"use client";

import { useState } from "react";
import { apiClient, Template, StartExecutionRequest } from "@/lib/api-client";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface StartExecutionDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  templates: Template[];
  onSuccess: () => void;
}

export function StartExecutionDialog({
  open,
  onOpenChange,
  templates,
  onSuccess,
}: StartExecutionDialogProps) {
  const [templateId, setTemplateId] = useState("");
  const [paramsJson, setParamsJson] = useState("{}");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!templateId) {
      setError("请选择模板");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      let params = {};
      try {
        params = JSON.parse(paramsJson);
      } catch {
        setError("参数 JSON 格式无效");
        setLoading(false);
        return;
      }

      const request: StartExecutionRequest = {
        template_id: templateId,
        params,
      };

      await apiClient.post("/api/executions", request);
      setTemplateId("");
      setParamsJson("{}");
      onSuccess();
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("启动执行失败");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>启动执行</DialogTitle>
          <DialogDescription>
            选择模板并配置执行参数
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="template">选择模板</Label>
              <Select value={templateId} onValueChange={setTemplateId}>
                <SelectTrigger>
                  <SelectValue placeholder="请选择模板" />
                </SelectTrigger>
                <SelectContent>
                  {templates.map((t) => (
                    <SelectItem key={t.id} value={t.id}>
                      {t.name} (v{t.version})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label htmlFor="params">执行参数 (JSON)</Label>
              <textarea
                id="params"
                value={paramsJson}
                onChange={(e) => setParamsJson(e.target.value)}
                className="min-h-[100px] rounded-md border border-zinc-200 bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-zinc-500 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-950 font-mono"
                placeholder='{"key": "value"}'
              />
            </div>
            {error && (
              <div className="text-sm text-red-500">{error}</div>
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
            <Button type="submit" disabled={loading || templates.length === 0}>
              {loading ? "启动中..." : "启动"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
