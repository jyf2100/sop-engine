"use client";

import { useState, useEffect } from "react";
import { apiClient, Agent, PaginatedResponse } from "@/lib/api-client";
import { AgentList } from "@/components/agents/agent-list";
import { CreateAgentDialog } from "@/components/agents/create-agent-dialog";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);

  const loadAgents = async () => {
    setLoading(true);
    try {
      const data: PaginatedResponse<Agent> = await apiClient.get("/api/agents");
      setAgents(data.items || []);
    } catch (error) {
      console.error("Failed to load agents:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAgents();
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Agent 管理</CardTitle>
          <Button onClick={() => setCreateOpen(true)}>创建 Agent</Button>
        </CardHeader>
        <CardContent>
          <AgentList
            agents={agents}
            loading={loading}
            onRefresh={loadAgents}
          />
        </CardContent>
      </Card>

      <CreateAgentDialog
        open={createOpen}
        onOpenChange={setCreateOpen}
        onSuccess={() => {
          setCreateOpen(false);
          loadAgents();
        }}
      />
    </div>
  );
}
