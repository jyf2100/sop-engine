"use client";

import { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";

interface FlowNode {
  id: string;
  type: string;
  name: string;
  x: number;
  y: number;
  next?: string;
}

interface FlowEdge {
  id: string;
  source: string;
  target: string;
}

const NODE_TYPES = [
  { type: "start", label: "开始", color: "bg-green-500" },
  { type: "end", label: "结束", color: "bg-red-500" },
  { type: "agent", label: "Agent", color: "bg-blue-500" },
  { type: "script", label: "脚本", color: "bg-yellow-500" },
  { type: "condition", label: "条件", color: "bg-purple-500" },
  { type: "parallel", label: "并行", color: "bg-orange-500" },
  { type: "loop", label: "循环", color: "bg-pink-500" },
  { type: "human", label: "审批", color: "bg-cyan-500" },
];

export default function EditorPage() {
  const [nodes, setNodes] = useState<FlowNode[]>([]);
  const [edges, setEdges] = useState<FlowEdge[]>([]);
  const [selectedNode, setSelectedNode] = useState<FlowNode | null>(null);
  const [connectingFrom, setConnectingFrom] = useState<string | null>(null);
  const [exportOpen, setExportOpen] = useState(false);
  const [yamlOutput, setYamlOutput] = useState("");

  const addNode = useCallback((type: string) => {
    const id = `${type}_${Date.now()}`;
    const label = NODE_TYPES.find((t) => t.type === type)?.label || type;
    const newNode: FlowNode = {
      id,
      type,
      name: `${label} ${nodes.length + 1}`,
      x: 100 + (nodes.length % 5) * 150,
      y: 100 + Math.floor(nodes.length / 5) * 100,
    };
    setNodes((prev) => [...prev, newNode]);
  }, [nodes.length]);

  const handleNodeClick = useCallback((node: FlowNode) => {
    if (connectingFrom) {
      // Create edge
      if (connectingFrom !== node.id) {
        const newEdge: FlowEdge = {
          id: `edge_${connectingFrom}_${node.id}`,
          source: connectingFrom,
          target: node.id,
        };
        setEdges((prev) => [...prev, newEdge]);
        // Update node's next property
        setNodes((prev) =>
          prev.map((n) =>
            n.id === connectingFrom ? { ...n, next: node.id } : n
          )
        );
      }
      setConnectingFrom(null);
    } else {
      setSelectedNode(node);
    }
  }, [connectingFrom]);

  const startConnecting = useCallback((nodeId: string) => {
    setConnectingFrom(nodeId);
    setSelectedNode(null);
  }, []);

  const deleteNode = useCallback((nodeId: string) => {
    setNodes((prev) => prev.filter((n) => n.id !== nodeId));
    setEdges((prev) =>
      prev.filter((e) => e.source !== nodeId && e.target !== nodeId)
    );
    setSelectedNode(null);
  }, []);

  const exportToYaml = useCallback(() => {
    const yamlLines = [
      "name: custom-flow",
      "version: \"1.0\"",
      "nodes:",
    ];

    nodes.forEach((node) => {
      yamlLines.push(`  - id: ${node.id}`);
      yamlLines.push(`    type: ${node.type}`);
      if (node.next) {
        yamlLines.push(`    next: ${node.next}`);
      }
    });

    setYamlOutput(yamlLines.join("\n"));
    setExportOpen(true);
  }, [nodes]);

  return (
    <div className="container mx-auto px-4 py-8 h-[calc(100vh-4rem)]">
      <div className="grid grid-cols-[250px_1fr] gap-4 h-full">
        {/* 左侧面板 - 节点类型 */}
        <Card className="h-fit">
          <CardHeader>
            <CardTitle className="text-sm">节点类型</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {NODE_TYPES.map((nodeType) => (
              <Button
                key={nodeType.type}
                variant="outline"
                className="w-full justify-start"
                onClick={() => addNode(nodeType.type)}
              >
                <span
                  className={`w-3 h-3 rounded-full ${nodeType.color} mr-2`}
                />
                {nodeType.label}
              </Button>
            ))}
            <div className="pt-4 border-t mt-4">
              <Button
                className="w-full"
                onClick={exportToYaml}
                disabled={nodes.length === 0}
              >
                导出 YAML
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* 右侧 - 画布 */}
        <Card className="relative overflow-hidden">
          <CardHeader className="absolute top-0 left-0 right-0 z-10 bg-white/80 dark:bg-zinc-900/80">
            <CardTitle>流程画布</CardTitle>
          </CardHeader>
          <CardContent className="p-0 h-full">
            <div className="w-full h-full bg-zinc-50 dark:bg-zinc-900 relative overflow-auto">
              {/* SVG for edges */}
              <svg className="absolute inset-0 w-full h-full pointer-events-none">
                {edges.map((edge) => {
                  const source = nodes.find((n) => n.id === edge.source);
                  const target = nodes.find((n) => n.id === edge.target);
                  if (!source || !target) return null;
                  return (
                    <line
                      key={edge.id}
                      x1={source.x + 60}
                      y1={source.y + 25}
                      x2={target.x + 60}
                      y2={target.y + 25}
                      stroke="#888"
                      strokeWidth={2}
                      markerEnd="url(#arrowhead)"
                    />
                  );
                })}
                <defs>
                  <marker
                    id="arrowhead"
                    markerWidth="10"
                    markerHeight="7"
                    refX="9"
                    refY="3.5"
                    orient="auto"
                  >
                    <polygon
                      points="0 0, 10 3.5, 0 7"
                      fill="#888"
                    />
                  </marker>
                </defs>
              </svg>

              {/* Nodes */}
              {nodes.map((node) => {
                const nodeType = NODE_TYPES.find((t) => t.type === node.type);
                return (
                  <div
                    key={node.id}
                    className={`absolute w-[120px] h-[50px] rounded-md border-2 shadow-sm cursor-pointer flex items-center justify-center text-white text-sm font-medium ${
                      nodeType?.color || "bg-gray-500"
                    } ${selectedNode?.id === node.id ? "ring-2 ring-blue-400" : ""} ${
                      connectingFrom === node.id ? "ring-2 ring-green-400" : ""
                    }`}
                    style={{ left: node.x, top: node.y }}
                    onClick={() => handleNodeClick(node)}
                  >
                    {node.name}
                  </div>
                );
              })}

              {nodes.length === 0 && (
                <div className="absolute inset-0 flex items-center justify-center text-zinc-400">
                  点击左侧按钮添加节点
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 节点操作对话框 */}
      <Dialog open={!!selectedNode} onOpenChange={() => setSelectedNode(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{selectedNode?.name}</DialogTitle>
            <DialogDescription>类型: {selectedNode?.type}</DialogDescription>
          </DialogHeader>
          <div className="py-4 space-y-4">
            <p className="text-sm text-zinc-500">
              ID: {selectedNode?.id}
            </p>
          </div>
          <DialogFooter className="space-x-2">
            <Button
              variant="outline"
              onClick={() => {
                if (selectedNode) startConnecting(selectedNode.id);
              }}
            >
              连接到...
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                if (selectedNode) deleteNode(selectedNode.id);
              }}
            >
              删除
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* YAML 导出对话框 */}
      <Dialog open={exportOpen} onOpenChange={setExportOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>导出 YAML</DialogTitle>
            <DialogDescription>
              复制以下 YAML 内容到模板文件
            </DialogDescription>
          </DialogHeader>
          <div className="mt-4">
            <pre className="bg-zinc-100 dark:bg-zinc-800 p-4 rounded-md overflow-auto text-sm font-mono">
              {yamlOutput}
            </pre>
          </div>
          <DialogFooter>
            <Button
              onClick={() => {
                navigator.clipboard.writeText(yamlOutput);
              }}
            >
              复制到剪贴板
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* 连接模式提示 */}
      {connectingFrom && (
        <div className="fixed bottom-4 left-1/2 transform -translate-x-1/2 bg-blue-500 text-white px-4 py-2 rounded-md shadow-lg">
          点击目标节点以创建连接，或点击空白处取消
        </div>
      )}
    </div>
  );
}
