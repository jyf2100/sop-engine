"use client";

import { useState, useEffect, useRef } from "react";
import { apiClient, Template, PaginatedResponse } from "@/lib/api-client";
import { TemplateList } from "@/components/templates/template-list";
import { CreateTemplateDialog } from "@/components/templates/create-template-dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadTemplates = async () => {
    setLoading(true);
    try {
      const data: PaginatedResponse<Template> = await apiClient.get("/api/templates");
      setTemplates(data.items || []);
    } catch (error) {
      console.error("Failed to load templates:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTemplates();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    try {
      const content = await file.text();
      const template = await apiClient.post("/api/templates/upload", content);
      console.log("Uploaded template:", template);
      loadTemplates();
    } catch (error) {
      console.error("Failed to upload template:", error);
      alert("上传失败，请检查 YAML 格式");
    } finally {
      setUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>流程模板</CardTitle>
          <div className="space-x-2">
            <input
              ref={fileInputRef}
              type="file"
              accept=".yaml,.yml"
              onChange={handleFileUpload}
              className="hidden"
              id="yaml-upload"
            />
            <Button
              variant="outline"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
            >
              {uploading ? "上传中..." : "上传 YAML"}
            </Button>
            <Button onClick={() => setCreateOpen(true)}>创建模板</Button>
          </div>
        </CardHeader>
        <CardContent>
          <TemplateList
            templates={templates}
            loading={loading}
            onRefresh={loadTemplates}
          />
        </CardContent>
      </Card>

      <CreateTemplateDialog
        open={createOpen}
        onOpenChange={setCreateOpen}
        onSuccess={() => {
          setCreateOpen(false);
          loadTemplates();
        }}
      />
    </div>
  );
}
