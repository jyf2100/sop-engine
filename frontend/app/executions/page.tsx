"use client";

import { useState, useEffect } from "react";
import { apiClient, Execution, PaginatedResponse } from "@/lib/api-client";
import { ExecutionList } from "@/components/executions/execution-list";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function ExecutionsPage() {
  const [executions, setExecutions] = useState<Execution[]>([]);
  const [loading, setLoading] = useState(true);

  const loadExecutions = async () => {
    setLoading(true);
    try {
      const data: PaginatedResponse<Execution> = await apiClient.get("/api/executions");
      setExecutions(data.items || []);
    } catch (error) {
      console.error("Failed to load executions:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadExecutions();

    // WebSocket for real-time updates
    const ws = apiClient.createWebSocket((data) => {
      const msg = data as { type: string };
      if (msg.type === "execution_update") {
        loadExecutions();
      }
    });

    return () => ws.close();
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <Card>
        <CardHeader>
          <CardTitle>执行监控</CardTitle>
        </CardHeader>
        <CardContent>
          <ExecutionList
            executions={executions}
            loading={loading}
            onRefresh={loadExecutions}
          />
        </CardContent>
      </Card>
    </div>
  );
}
