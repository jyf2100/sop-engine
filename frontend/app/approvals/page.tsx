"use client";

import { useState, useEffect } from "react";
import { apiClient, PendingApproval, PendingApprovalListResponse } from "@/lib/api-client";
import { ApprovalList } from "@/components/approvals/approval-list";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function ApprovalsPage() {
  const [approvals, setApprovals] = useState<PendingApproval[]>([]);
  const [loading, setLoading] = useState(true);

  const loadApprovals = async () => {
    setLoading(true);
    try {
      const data: PendingApprovalListResponse = await apiClient.get("/api/approvals/pending");
      setApprovals(data.approvals || []);
    } catch (error) {
      console.error("Failed to load approvals:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadApprovals();

    // WebSocket for real-time updates
    const ws = apiClient.createWebSocket((data) => {
      const msg = data as { type: string };
      if (msg.type === "new_approval" || msg.type === "approval_update") {
        loadApprovals();
      }
    });

    return () => ws.close();
  }, []);

  return (
    <div className="container mx-auto px-4 py-8">
      <Card>
        <CardHeader>
          <CardTitle>审批工作台</CardTitle>
        </CardHeader>
        <CardContent>
          <ApprovalList
            approvals={approvals}
            loading={loading}
            onRefresh={loadApprovals}
          />
        </CardContent>
      </Card>
    </div>
  );
}
