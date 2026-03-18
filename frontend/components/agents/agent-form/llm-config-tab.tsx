"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { X, Plus, ExternalLink } from "lucide-react";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { apiClient, ModelConfig } from "@/lib/api-client";
import { cn } from "@/lib/utils";
import { JsonEditor } from "./json-editor";

interface LlmConfig {
  model_id?: string;
  base_url: string;
  api_key: string;
  primary: string;
  fallbacks: string[];
}

interface LlmConfigTabProps {
  config: LlmConfig;
  onChange: (config: LlmConfig) => void;
}

const PROVIDER_COLORS: Record<string, string> = {
  anthropic: "bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-300",
  openai: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300",
  google: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300",
  cohere: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300",
  custom: "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-300",
};

export function LlmConfigTab({ config, onChange }: LlmConfigTabProps) {
  const [models, setModels] = useState<ModelConfig[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const data = await apiClient.get<ModelConfig[]>("/api/models?type=llm");
        setModels(data);
      } catch (error) {
        console.error("Failed to fetch models:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchModels();
  }, []);

  const selectedModel = models.find((m) => m.id === config.model_id);

  const handleModelSelect = (modelId: string) => {
    const model = models.find((m) => m.id === modelId);
    if (model) {
      onChange({
        ...config,
        model_id: modelId,
        primary: model.model_id,
        base_url: model.base_url,
        api_key: config.api_key,
      });
    }
  };

  const addFallback = () => {
    const fallbacks = config.fallbacks || [];
    const otherModel = models.find((m) => m.model_id !== config.primary);
    if (otherModel) {
      onChange({ ...config, fallbacks: [...fallbacks, otherModel.model_id] });
    }
  };

  const removeFallback = (index: number) => {
    const fallbacks = config.fallbacks || [];
    onChange({
      ...config,
      fallbacks: fallbacks.filter((_, i) => i !== index),
    });
  };

  const updateFallback = (index: number, modelId: string) => {
    const fallbacks = [...(config.fallbacks || [])];
    fallbacks[index] = modelId;
    onChange({ ...config, fallbacks });
  };

  return (
    <div className="space-y-6">
      {/* 模型选择 */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="font-medium">选择模型</h4>
          <Link
            href="/models"
            className="text-xs text-indigo-500 hover:text-indigo-600 flex items-center gap-1"
          >
            <ExternalLink className="h-3 w-3" />
            管理模型配置
          </Link>
        </div>

        {loading ? (
          <div
            className="flex items-center justify-center py-8"
            role="status"
            aria-live="polite"
            aria-label="加载模型列表中"
          >
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-500" />
            <span className="sr-only">加载模型列表中...</span>
          </div>
        ) : models.length === 0 ? (
          <div className="text-center py-8 rounded-lg border-2 border-dashed border-zinc-200 dark:border-zinc-800">
            <p className="text-zinc-500 mb-2">暂无可用模型</p>
            <Link href="/models">
              <Button variant="outline" size="sm">
                添加第一个模型
              </Button>
            </Link>
          </div>
        ) : (
          <Select
            value={config.model_id || ""}
            onValueChange={handleModelSelect}
          >
            <SelectTrigger className="h-auto py-2">
              <SelectValue placeholder="选择一个 LLM 模型" />
            </SelectTrigger>
            <SelectContent>
              {models.map((model) => (
                <SelectItem key={model.id} value={model.id}>
                  <div className="flex items-center gap-2">
                    <span
                      className={cn(
                        "px-1.5 py-0.5 rounded text-[10px] font-bold uppercase",
                        PROVIDER_COLORS[model.provider]
                      )}
                    >
                      {model.provider}
                    </span>
                    <span className="font-medium">{model.name}</span>
                    {model.is_default && (
                      <span className="text-[10px] text-indigo-500">★</span>
                    )}
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      </div>

      {/* 选中模型的参数预览 */}
      {selectedModel && (
        <div className="p-4 rounded-lg bg-gradient-to-r from-zinc-50 to-zinc-100 dark:from-zinc-800/50 dark:to-zinc-900/50 border border-zinc-200 dark:border-zinc-700">
          <div className="flex items-start justify-between mb-3">
            <div>
              <div className="font-medium">{selectedModel.name}</div>
              <div className="text-xs text-zinc-500 font-mono">
                {selectedModel.model_id}
              </div>
            </div>
            <span
              className={cn(
                "px-2 py-0.5 rounded text-xs font-bold uppercase",
                PROVIDER_COLORS[selectedModel.provider]
              )}
            >
              {selectedModel.provider}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span className="text-zinc-400">Base URL:</span>
              <div className="font-mono text-xs truncate">{selectedModel.base_url}</div>
            </div>
            <div>
              <span className="text-zinc-400">参数:</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {selectedModel.default_params.temperature !== undefined && (
                  <span className="px-1.5 py-0.5 rounded bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 text-[10px] font-mono">
                    temp: {selectedModel.default_params.temperature}
                  </span>
                )}
                {selectedModel.default_params.max_tokens !== undefined && (
                  <span className="px-1.5 py-0.5 rounded bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-[10px] font-mono">
                    tokens: {selectedModel.default_params.max_tokens}
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* API Key 覆盖 */}
      {selectedModel && (
        <div className="space-y-2">
          <Label htmlFor="api-key">API Key（可选覆盖）</Label>
          <p className="text-xs text-zinc-500 -mt-1">
            留空则使用模型配置中保存的 API Key
          </p>
          <Input
            id="api-key"
            type="password"
            value={config.api_key || ""}
            onChange={(e) => onChange({ ...config, api_key: e.target.value })}
            placeholder="留空使用模型配置的 Key"
          />
        </div>
      )}

      {/* 备用模型 */}
      {selectedModel && (
        <div className="space-y-4">
          <h4 className="font-medium">备用模型</h4>
          <div className="space-y-2">
            {(config.fallbacks || []).map((modelId, index) => (
              <div key={index} className="flex gap-2">
                <Select value={modelId} onValueChange={(v) => updateFallback(index, v)}>
                  <SelectTrigger className="flex-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {models
                      .filter((m) => m.model_id !== config.primary)
                      .map((m) => (
                        <SelectItem key={m.id} value={m.model_id}>
                          {m.name}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  aria-label="移除备用模型"
                  onClick={() => removeFallback(index)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={addFallback}
              className="w-full"
            >
              <Plus className="h-3 w-3 mr-1" />
              添加备用模型
            </Button>
          </div>
        </div>
      )}

      {/* 高级 JSON 配置 */}
      <Accordion type="single" collapsible>
        <AccordionItem value="json-config">
          <AccordionTrigger className="cursor-pointer text-sm font-medium text-zinc-600 hover:text-zinc-900 px-2 py-1.5 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-800 w-full text-left">
            高级配置 (JSON)
          </AccordionTrigger>
          <AccordionContent className="mt-3">
            <JsonEditor value={config} onChange={onChange} height="150px" />
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}
