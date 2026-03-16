"use client";

import { Template } from "@/lib/api-client";
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

interface TemplateListProps {
  templates: Template[];
  loading: boolean;
  onRefresh: () => void;
}

export function TemplateList({ templates, loading, onRefresh }: TemplateListProps) {
  const [detailOpen, setDetailOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<Template | null>(null);

  const handleDelete = async () => {
    if (!selectedTemplate) return;
    try {
      await apiClient.delete(`/api/templates/${selectedTemplate.id}`);
      setDeleteOpen(false);
      onRefresh();
    } catch (error) {
      console.error("Failed to delete template:", error);
    }
  };

  if (loading) {
    return <div className="text-center py-8">加载中...</div>;
  }

  if (templates.length === 0) {
    return <div className="text-center py-8 text-zinc-500">暂无模板</div>;
  }

  return (
    <>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>名称</TableHead>
            <TableHead>版本</TableHead>
            <TableHead>创建时间</TableHead>
            <TableHead className="text-right">操作</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {templates.map((template) => (
            <TableRow key={template.id}>
              <TableCell className="font-medium">{template.name}</TableCell>
              <TableCell>{template.version}</TableCell>
              <TableCell>
                {template.created_at
                  ? new Date(template.created_at).toLocaleString()
                  : "-"}
              </TableCell>
              <TableCell className="text-right space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setSelectedTemplate(template);
                    setDetailOpen(true);
                  }}
                >
                  查看
                </Button>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => {
                    setSelectedTemplate(template);
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
            <DialogTitle>{selectedTemplate?.name}</DialogTitle>
            <DialogDescription>
              版本: {selectedTemplate?.version}
            </DialogDescription>
          </DialogHeader>
          <div className="mt-4">
            <pre className="bg-zinc-100 dark:bg-zinc-800 p-4 rounded-md overflow-auto text-sm">
              {selectedTemplate?.yaml_content}
            </pre>
          </div>
        </DialogContent>
      </Dialog>

      {/* 删除确认对话框 */}
      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>确认删除</DialogTitle>
            <DialogDescription>
              确定要删除模板 "{selectedTemplate?.name}" 吗？此操作不可撤销。
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
