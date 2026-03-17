"use client";

import { useState, useEffect } from "react";
import { apiClient, ModelConfig, ModelType, CreateModelRequest, UpdateModelRequest } from "@/lib/api-client";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/toast";
import { ModelCard } from "@/components/models/model-card";
import { ModelDialog } from "@/components/models/model-dialog";
import { cn } from "@/lib/utils";

export default function ModelsPage() {
  const [models, setModels] = useState<ModelConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<ModelType>("llm");
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingModel, setEditingModel] = useState<ModelConfig | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const { toast } = useToast();

  const fetchModels = async () => {
    setError(null);
    try {
      const data = await apiClient.get<ModelConfig[]>("/api/models");
      setModels(data);
    } catch (err) {
      const message = err instanceof Error ? err.message : "加载模型列表失败";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  const filteredModels = models.filter((m) => m.type === activeTab);

  const handleAddModel = () => {
    setEditingModel(null);
    setDialogOpen(true);
  };

  const handleEditModel = (model: ModelConfig) => {
    setEditingModel(model);
    setDialogOpen(true);
  };

  const handleDeleteModel = async (model: ModelConfig) => {
    if (!confirm(`确定要删除模型 "${model.name}" 吗？`)) return;

    try {
      await apiClient.delete(`/api/models/${model.id}`);
      toast({ type: "success", message: "模型已删除" });
      fetchModels();
    } catch (error) {
      console.error("Failed to delete model:", error);
      toast({ type: "error", message: "删除模型失败" });
    }
  };

  const handleSetDefault = async (model: ModelConfig) => {
    try {
      await apiClient.patch(`/api/models/${model.id}`, { is_default: true });
      toast({ type: "success", message: "已设为默认模型" });
      fetchModels();
    } catch (error) {
      console.error("Failed to set default:", error);
      toast({ type: "error", message: "设置默认模型失败" });
    }
  };

  const handleSubmit = async (data: CreateModelRequest | UpdateModelRequest) => {
    setSubmitting(true);
    try {
      if (editingModel) {
        await apiClient.patch(`/api/models/${editingModel.id}`, data);
        toast({ type: "success", message: "模型已更新" });
      } else {
        await apiClient.post("/api/models", data);
        toast({ type: "success", message: "模型已创建" });
      }
      setDialogOpen(false);
      fetchModels();
    } catch (error) {
      console.error("Failed to save model:", error);
      toast({ type: "error", message: editingModel ? "更新模型失败" : "创建模型失败" });
    } finally {
      setSubmitting(false);
    }
  };

  const tabConfig: { type: ModelType; label: string; icon: string; gradient: string; glowColor: string }[] = [
    {
      type: "llm",
      label: "LLM 模型",
      icon: "🧠",
      gradient: "from-violet-600 via-purple-500 to-fuchsia-500",
      glowColor: "rgba(139, 92, 246, 0.5)",
    },
    {
      type: "embedding",
      label: "Embedding",
      icon: "🔢",
      gradient: "from-cyan-500 via-teal-500 to-emerald-500",
      glowColor: "rgba(6, 182, 212, 0.5)",
    },
    {
      type: "image",
      label: "图像模型",
      icon: "🎨",
      gradient: "from-pink-500 via-rose-500 to-orange-500",
      glowColor: "rgba(236, 72, 153, 0.5)",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-50 via-zinc-100 to-zinc-50 dark:from-zinc-950 dark:via-zinc-900 dark:to-zinc-950">
      {/* 装饰性背景光晕 */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-gradient-to-br from-violet-500/20 via-purple-500/20 to-fuchsia-500/20 rounded-full blur-3xl" />
        <div className="absolute top-1/2 -left-40 w-96 h-96 bg-gradient-to-br from-cyan-500/20 via-teal-500/20 to-emerald-500/20 rounded-full blur-3xl" />
        <div className="absolute -bottom-40 right-1/3 w-96 h-96 bg-gradient-to-br from-pink-500/20 via-rose-500/20 to-orange-500/20 rounded-full blur-3xl" />
      </div>

      <div className="container mx-auto py-8 px-4 relative">
        {/* Header */}
        <div className="mb-10 text-center">
          <div className="inline-flex items-center justify-center mb-4">
            <h1 className="text-5xl font-black tracking-tight
              bg-gradient-to-r from-violet-600 via-fuchsia-500 to-cyan-400
              bg-clip-text text-transparent
              drop-shadow-2xl">
              模型配置中心
            </h1>
          </div>
          <p className="text-lg text-zinc-500 dark:text-zinc-400 max-w-xl mx-auto">
            管理系统的 AI 模型配置，支持主流提供商和自定义模型
          </p>
          <div className="mt-4 flex items-center justify-center gap-3">
            {["Anthropic", "OpenAI", "Google", "Cohere", "Stability"].map((provider, i) => (
              <span
                key={provider}
                className="px-3 py-1 text-xs font-bold rounded-full
                  bg-zinc-900/5 dark:bg-white/5 backdrop-blur-sm
                  border border-zinc-200/50 dark:border-zinc-700/50
                  text-zinc-600 dark:text-zinc-400"
              >
                {provider}
              </span>
            ))}
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={(v: string) => setActiveTab(v as ModelType)}>
          <div className="flex items-center justify-between mb-8">
            <TabsList className="grid grid-cols-3 w-[420px] h-14 p-1.5
              bg-zinc-900/5 dark:bg-white/5 backdrop-blur-xl
              border border-zinc-200/50 dark:border-zinc-700/50
              rounded-2xl shadow-xl">
              {tabConfig.map(({ type, label, icon, gradient, glowColor }) => (
                <TabsTrigger
                  key={type}
                  value={type}
                  className={cn(
                    "relative h-11 rounded-xl text-sm font-bold transition-all duration-300",
                    "data-[state=active]:text-white data-[state=active]:shadow-2xl",
                    activeTab === type && `bg-gradient-to-r ${gradient}`,
                    activeTab === type && `shadow-[0_0_30px_${glowColor}]`,
                    activeTab !== type && "text-zinc-500 hover:text-zinc-700 dark:hover:text-zinc-300"
                  )}
                >
                  <span className="mr-2 text-lg">{icon}</span>
                  {label}
                </TabsTrigger>
              ))}
            </TabsList>

            <Button
              onClick={handleAddModel}
              className={cn(
                "h-12 px-6 text-base font-bold rounded-2xl",
                "bg-gradient-to-r from-violet-600 via-fuchsia-500 to-pink-500",
                "hover:from-violet-700 hover:via-fuchsia-600 hover:to-pink-600",
                "text-white shadow-[0_0_30px_rgba(168,85,247,0.4)]",
                "hover:shadow-[0_0_40px_rgba(168,85,247,0.6)]",
                "transition-all duration-300 hover:scale-[1.02]",
                "border-0"
              )}
            >
              <span className="mr-2 text-xl">✨</span>
              添加模型
            </Button>
          </div>

          {/* Content */}
          {tabConfig.map(({ type, gradient }) => (
            <TabsContent key={type} value={type} className="mt-0">
              {error ? (
                <div className="flex flex-col items-center justify-center py-24">
                  <span className="text-5xl mb-4">⚠️</span>
                  <p className="text-red-500 mb-2">{error}</p>
                  <p className="text-zinc-400 text-sm mb-4">请确保后端服务已启动</p>
                  <Button onClick={fetchModels} variant="outline">
                    重试
                  </Button>
                </div>
              ) : loading ? (
                <div className="flex flex-col items-center justify-center py-24">
                  <div className={cn(
                    "w-12 h-12 rounded-full border-4 border-t-transparent animate-spin",
                    `border-gradient-to-r ${gradient}`
                  )} />
                  <p className="mt-4 text-zinc-500">加载中...</p>
                </div>
              ) : filteredModels.length === 0 ? (
                <div className="text-center py-24">
                  <div className={cn(
                    "inline-flex items-center justify-center w-24 h-24 rounded-3xl mb-6",
                    "bg-gradient-to-br shadow-2xl",
                    type === "llm" && "from-violet-500/20 to-purple-500/20 shadow-violet-500/20",
                    type === "embedding" && "from-cyan-500/20 to-teal-500/20 shadow-cyan-500/20",
                    type === "image" && "from-pink-500/20 to-rose-500/20 shadow-pink-500/20"
                  )}>
                    <span className="text-5xl">📭</span>
                  </div>
                  <p className="text-xl font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                    暂无{type === "llm" ? "LLM" : type === "embedding" ? "Embedding" : "图像"}模型
                  </p>
                  <p className="text-zinc-500 mb-6">
                    添加你的第一个模型开始使用
                  </p>
                  <Button
                    onClick={handleAddModel}
                    variant="outline"
                    className={cn(
                      "h-11 px-6 rounded-xl font-semibold",
                      "border-2 hover:scale-[1.02] transition-all duration-300",
                      type === "llm" && "border-violet-300 hover:border-violet-400 hover:bg-violet-50 dark:hover:bg-violet-900/20",
                      type === "embedding" && "border-cyan-300 hover:border-cyan-400 hover:bg-cyan-50 dark:hover:bg-cyan-900/20",
                      type === "image" && "border-pink-300 hover:border-pink-400 hover:bg-pink-50 dark:hover:bg-pink-900/20"
                    )}
                  >
                    <span className="mr-2">➕</span>
                    添加第一个模型
                  </Button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {filteredModels.map((model) => (
                    <ModelCard
                      key={model.id}
                      model={model}
                      onEdit={handleEditModel}
                      onDelete={handleDeleteModel}
                      onSetDefault={handleSetDefault}
                    />
                  ))}
                </div>
              )}
            </TabsContent>
          ))}
        </Tabs>

        {/* Add/Edit Dialog */}
        <ModelDialog
          open={dialogOpen}
          onOpenChange={setDialogOpen}
          model={editingModel}
          modelType={activeTab}
          onSubmit={handleSubmit}
          isLoading={submitting}
        />
      </div>
    </div>
  );
}
