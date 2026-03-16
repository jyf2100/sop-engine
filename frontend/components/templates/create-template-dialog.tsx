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

interface CreateTemplateDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function CreateTemplateDialog({
  open,
  onOpenChange,
  onSuccess,
}: CreateTemplateDialogProps) {
  const [name, setName] = useState("");
  const [version, setVersion] = useState("1.0.0");
  const [yamlContent, setYamlContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await apiClient.post("/api/templates", {
        name,
        version,
        yaml_content: yamlContent,
      });
      onSuccess();
      // Reset form
      setName("");
      setVersion("1.0.0");
      setYamlContent("");
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("创建模板失败");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>创建模板</DialogTitle>
          <DialogDescription>
            创建一个新的流程模板。请填写模板名称、版本和 YAML 内容。
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
              <Label htmlFor="version" className="text-right">
                版本
              </Label>
              <Input
                id="version"
                value={version}
                onChange={(e) => setVersion(e.target.value)}
                className="col-span-3"
                required
              />
            </div>
            <div className="grid grid-cols-4 items-start gap-4">
              <Label htmlFor="yaml" className="text-right pt-2">
                YAML 内容
              </Label>
              <textarea
                id="yaml"
                value={yamlContent}
                onChange={(e) => setYamlContent(e.target.value)}
                className="col-span-3 min-h-[200px] rounded-md border border-zinc-200 bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-zinc-500 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-zinc-950 disabled:cursor-not-allowed disabled:opacity-50 dark:border-zinc-800 dark:placeholder:text-zinc-400 dark:focus-visible:ring-zinc-300 font-mono"
                placeholder={`name: example-flow
version: "1.0"
nodes:
  - id: start
    type: start
    next: end
  - id: end
    type: end`}
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
