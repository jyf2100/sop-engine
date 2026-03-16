"use client";

import { useState, useEffect } from "react";
import { apiClient, Execution, PaginatedResponse, Template, StartExecutionRequest } from "@/lib/api-client";
import { ExecutionList } from "@/components/executions/execution-list";
import { StartExecutionDialog } from "@/components/executions/start-execution-dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";

export default function ExecutionsPage() {
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [startOpen, setStartOpen] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>("all");

  const loadExecutions = async () => {
    setLoading(true);
    try {
      let url = "/api/executions";
      if (statusFilter && statusFilter !== "all") {
        url += `?status=${statusFilter}`;
      }
      const data: PaginatedResponse<Execution> = await apiClient.get(url);
      setExecutions(data.items || []);
    } catch (error) {
      console.error("Failed to load executions:", error);
    } finally {
      setLoading(false);
    }
  };

  const loadTemplates = async () => {
    try {
      const data: PaginatedResponse<Template> = await apiClient.get("/api/templates");
      setTemplates(data.items || []);
    } catch (error) {
      console.error("Failed to load templates:", error);
    }
  };

  useEffect(() => {
    loadExecutions();
    loadTemplates();
  }, [statusFilter]);

  useEffect(() => {
    // WebSocket for real-time updates (connect once)
    const ws = apiClient.createWebSocket((data) => {
      if (data && typeof data === 'object' && 'type' in data) {
        const msg = data as { type: string };
        if (msg.type === "execution_update") {
          loadExecutions();
        }
      }
    });

    return () => ws.close();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div className="flex items-center gap-4">
            <CardTitle>执行监控</CardTitle>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="全部状态" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">全部状态</SelectItem>
                <SelectItem value="pending">等待中</SelectItem>
                <SelectItem value="running">运行中</SelectItem>
                <SelectItem value="completed">已完成</SelectItem>
                <SelectItem value="failed">失败</SelectItem>
                <SelectItem value="cancelled">已取消</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Button onClick={() => setStartOpen(true)}>启动执行</Button>
        </CardHeader>
        <CardContent>
          <ExecutionList
            executions={executions}
            templates={templates}
            loading={loading}
            onRefresh={loadExecutions}
          />
        </CardContent>
      </Card>

      <StartExecutionDialog
        open={startOpen}
        onOpenChange={setStartOpen}
        templates={templates}
        onSuccess={() => {
          setStartOpen(false);
          loadExecutions();
        }}
      />
    </div>
  );
}
