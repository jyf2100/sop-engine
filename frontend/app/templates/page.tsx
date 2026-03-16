"use client";

import { useState, useEffect } from "react";
import { apiClient, Template, PaginatedResponse } from "@/lib/api-client";
import { TemplateList } from "@/components/templates/template-list";
import { CreateTemplateDialog } from "@/components/templates/create-template-dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);

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

  return (
    <div className="container mx-auto px-4 py-8">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>流程模板</CardTitle>
          <Button onClick={() => setCreateOpen(true)}>创建模板</Button>
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
