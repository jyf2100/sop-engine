"use client";

import { useState, useEffect } from "react";
import { ModelConfig, ModelType, ModelProvider, CreateModelRequest, UpdateModelRequest } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

interface ModelDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  model?: ModelConfig | null;
  modelType: ModelType;
  onSubmit: (data: CreateModelRequest | UpdateModelRequest) => void;
  isLoading?: boolean;
}

const PROVIDERS: { value: ModelProvider; label: string }[] = [
  { value: "anthropic", label: "Anthropic" },
  { value: "openai", label: "OpenAI" },
  { value: "google", label: "Google" },
  { value: "cohere", label: "Cohere" },
  { value: "stability", label: "Stability AI" },
  { value: "custom", label: "自定义" },
];

const LLM_MODELS: Record<string, string[]> = {
  anthropic: ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"],
  openai: ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
  google: ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
  cohere: ["command-r-plus", "command-r", "command"],
  custom: [],
};

const EMBEDDING_MODELS: Record<string, string[]> = {
  openai: ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"],
  cohere: ["embed-english-v3.0", "embed-multilingual-v3.0"],
  google: ["text-embedding-004", "embedding-001"],
  custom: [],
};

const IMAGE_MODELS: Record<string, string[]> = {
  openai: ["dall-e-3", "dall-e-2"],
  stability: ["stable-diffusion-xl-1024-v1-0", "stable-diffusion-v1-6"],
  custom: [],
};

const TYPE_LABELS: Record<ModelType, string> = {
  llm: "LLM",
  embedding: "Embedding",
  image: "图像",
};

export function ModelDialog({
  open,
  onOpenChange,
  model,
  modelType,
  onSubmit,
  isLoading,
}: ModelDialogProps) {
  const isEditing = !!model;
  const [formData, setFormData] = useState<CreateModelRequest>({
    id: "",
    name: "",
    type: modelType,
    provider: "openai",
    model_id: "",
    base_url: "",
    api_key: "",
    default_params: {},
    dimensions: undefined,
    default_size: "1024x1024",
    is_default: false,
  });

  const [showApiKey, setShowApiKey] = useState(false);

  // Get models for current provider and type
  const getModelOptions = () => {
    if (modelType === "llm") return LLM_MODELS[formData.provider] || [];
    if (modelType === "embedding") return EMBEDDING_MODELS[formData.provider] || [];
    if (modelType === "image") return IMAGE_MODELS[formData.provider] || [];
    return [];
  };

  // Get default base URL for provider
  const getDefaultBaseUrl = (provider: ModelProvider) => {
    const urls: Record<string, string> = {
      anthropic: "https://api.anthropic.com",
      openai: "https://api.openai.com/v1",
      google: "https://generativelanguage.googleapis.com/v1beta",
      cohere: "https://api.cohere.ai/v1",
      stability: "https://api.stability.ai",
    };
    return urls[provider] || "";
  };

  // Reset form when dialog opens/closes or model changes
  useEffect(() => {
    if (open) {
      if (model) {
        setFormData({
          id: model.id,
          name: model.name,
          type: model.type,
          provider: model.provider,
          model_id: model.model_id,
          base_url: model.base_url,
          api_key: "",
          default_params: { ...model.default_params },
          dimensions: model.dimensions,
          default_size: model.default_size,
          is_default: model.is_default,
        });
      } else {
        setFormData({
          id: "",
          name: "",
          type: modelType,
          provider: "openai",
          model_id: getModelOptions()[0] || "",
          base_url: getDefaultBaseUrl("openai"),
          api_key: "",
          default_params: modelType === "llm" ? { temperature: 0.7, max_tokens: 4096 } : {},
          dimensions: modelType === "embedding" ? 1536 : undefined,
          default_size: modelType === "image" ? "1024x1024" : undefined,
          is_default: false,
        });
      }
    }
  }, [open, model, modelType]);

  const handleProviderChange = (provider: ModelProvider) => {
    const models = getModelOptions();
    setFormData((prev) => ({
      ...prev,
      provider,
      model_id: models[0] || prev.model_id,
      base_url: getDefaultBaseUrl(provider),
    }));
  };

  const handleModelIdChange = (modelId: string) => {
    setFormData((prev) => ({ ...prev, model_id: modelId }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isEditing) {
      const updateData: UpdateModelRequest = {
        name: formData.name,
        provider: formData.provider,
        model_id: formData.model_id,
        base_url: formData.base_url,
        api_key: formData.api_key || undefined,
        default_params: formData.default_params,
        dimensions: formData.dimensions,
        default_size: formData.default_size,
        is_default: formData.is_default,
      };
      onSubmit(updateData);
    } else {
      onSubmit(formData);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg border-2 border-zinc-200 dark:border-zinc-700 rounded-2xl">
        <DialogHeader>
          <DialogTitle className="text-xl font-bold bg-gradient-to-r from-violet-600 to-fuchsia-500 bg-clip-text text-transparent">
            {isEditing ? `编辑 ${TYPE_LABELS[modelType]} 模型` : `添加 ${TYPE_LABELS[modelType]} 模型`}
          </DialogTitle>
          <DialogDescription className="text-zinc-500">
            配置模型参数以支持 OpenAI 兼容格式
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Name */}
          <div className="space-y-2">
            <Label htmlFor="name" className="font-semibold">名称 *</Label>
            <Input
              id="name"
              value={formData.name}
              onChange={(e) => setFormData((p) => ({ ...p, name: e.target.value }))}
              placeholder="例如: GPT-4o"
              className="rounded-xl h-11"
              required
            />
          </div>

          {/* Provider & Model ID - only show for new models */}
          {!isEditing && (
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label className="font-semibold">Provider *</Label>
                <Select value={formData.provider} onValueChange={handleProviderChange}>
                  <SelectTrigger className="rounded-xl h-11">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="rounded-xl">
                    {PROVIDERS.map((p) => (
                      <SelectItem key={p.value} value={p.value}>
                        {p.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label className="font-semibold">模型 ID *</Label>
                {formData.provider === "custom" ? (
                  <Input
                    value={formData.model_id}
                    onChange={(e) => setFormData((p) => ({ ...p, model_id: e.target.value }))}
                    placeholder="自定义模型 ID"
                    className="rounded-xl h-11"
                    required
                  />
                ) : (
                  <Select value={formData.model_id} onValueChange={handleModelIdChange}>
                    <SelectTrigger className="rounded-xl h-11">
                      <SelectValue placeholder="选择模型" />
                    </SelectTrigger>
                    <SelectContent className="rounded-xl">
                      {getModelOptions().map((m) => (
                        <SelectItem key={m} value={m}>
                          {m}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              </div>
            </div>
          )}

          {/* Base URL */}
          <div className="space-y-2">
            <Label htmlFor="baseUrl" className="font-semibold">Base URL</Label>
            <Input
              id="baseUrl"
              value={formData.base_url}
              onChange={(e) => setFormData((p) => ({ ...p, base_url: e.target.value }))}
              placeholder="https://api.openai.com/v1"
              className="rounded-xl h-11 font-mono text-sm"
            />
          </div>

          {/* API Key */}
          <div className="space-y-2">
            <Label htmlFor="apiKey" className="font-semibold">API Key</Label>
            <div className="relative">
              <Input
                id="apiKey"
                type={showApiKey ? "text" : "password"}
                value={formData.api_key}
                onChange={(e) => setFormData((p) => ({ ...p, api_key: e.target.value }))}
                placeholder={isEditing ? "留空保持不变" : "sk-..."}
                className="rounded-xl h-11 pr-20"
              />
              <button
                type="button"
                onClick={() => setShowApiKey(!showApiKey)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-medium text-zinc-400 hover:text-violet-500 transition-colors"
              >
                {showApiKey ? "隐藏" : "显示"}
              </button>
            </div>
          </div>

          {/* Embedding: Dimensions */}
          {modelType === "embedding" && (
            <div className="space-y-2">
              <Label htmlFor="dimensions" className="font-semibold">向量维度</Label>
              <Input
                id="dimensions"
                type="number"
                value={formData.dimensions || ""}
                onChange={(e) =>
                  setFormData((p) => ({
                    ...p,
                    dimensions: e.target.value ? parseInt(e.target.value) : undefined,
                  }))
                }
                placeholder="1536"
                className="rounded-xl h-11"
              />
            </div>
          )}

          {/* Image: Default Size */}
          {modelType === "image" && (
            <div className="space-y-2">
              <Label htmlFor="defaultSize" className="font-semibold">默认尺寸</Label>
              <Select
                value={formData.default_size || "1024x1024"}
                onValueChange={(v) => setFormData((p) => ({ ...p, default_size: v }))}
              >
                <SelectTrigger className="rounded-xl h-11">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="rounded-xl">
                  <SelectItem value="256x256">256 × 256</SelectItem>
                  <SelectItem value="512x512">512 × 512</SelectItem>
                  <SelectItem value="1024x1024">1024 × 1024</SelectItem>
                  <SelectItem value="1792x1024">1792 × 1024</SelectItem>
                  <SelectItem value="1024x1792">1024 × 1792</SelectItem>
                </SelectContent>
              </Select>
            </div>
          )}

          {/* LLM: Default Parameters */}
          {modelType === "llm" && (
            <div className="space-y-3 p-4 rounded-xl bg-gradient-to-r from-violet-500/5 via-fuchsia-500/5 to-pink-500/5 border border-violet-200/50 dark:border-violet-800/50">
              <Label className="text-sm font-bold text-violet-700 dark:text-violet-300">默认参数</Label>
              <div className="grid grid-cols-3 gap-3">
                <div className="space-y-1">
                  <Label htmlFor="temperature" className="text-xs text-zinc-500 font-medium">
                    Temperature
                  </Label>
                  <Input
                    id="temperature"
                    type="number"
                    step="0.1"
                    min="0"
                    max="2"
                    value={formData.default_params?.temperature ?? 0.7}
                    onChange={(e) =>
                      setFormData((p) => ({
                        ...p,
                        default_params: {
                          ...p.default_params,
                          temperature: parseFloat(e.target.value),
                        },
                      }))
                    }
                    className="rounded-lg h-10"
                  />
                </div>
                <div className="space-y-1">
                  <Label htmlFor="maxTokens" className="text-xs text-zinc-500 font-medium">
                    Max Tokens
                  </Label>
                  <Input
                    id="maxTokens"
                    type="number"
                    value={formData.default_params?.max_tokens ?? 4096}
                    onChange={(e) =>
                      setFormData((p) => ({
                        ...p,
                        default_params: {
                          ...p.default_params,
                          max_tokens: parseInt(e.target.value),
                        },
                      }))
                    }
                    className="rounded-lg h-10"
                  />
                </div>
                <div className="space-y-1">
                  <Label htmlFor="topP" className="text-xs text-zinc-500 font-medium">
                    Top P
                  </Label>
                  <Input
                    id="topP"
                    type="number"
                    step="0.1"
                    min="0"
                    max="1"
                    value={formData.default_params?.top_p ?? 1}
                    onChange={(e) =>
                      setFormData((p) => ({
                        ...p,
                        default_params: {
                          ...p.default_params,
                          top_p: parseFloat(e.target.value),
                        },
                      }))
                    }
                    className="rounded-lg h-10"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Is Default */}
          <div className="flex items-center justify-between p-3 rounded-xl bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/50">
            <Label htmlFor="isDefault" className="cursor-pointer font-semibold text-amber-700 dark:text-amber-300">
              ⭐ 设为默认模型
            </Label>
            <Switch
              id="isDefault"
              checked={formData.is_default}
              onCheckedChange={(v: boolean) => setFormData((p) => ({ ...p, is_default: v }))}
            />
          </div>

          <DialogFooter className="gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              className="rounded-xl h-11 px-6 font-semibold"
            >
              取消
            </Button>
            <Button
              type="submit"
              disabled={isLoading}
              className="rounded-xl h-11 px-6 font-semibold
                bg-gradient-to-r from-violet-600 to-fuchsia-500
                hover:from-violet-700 hover:to-fuchsia-600
                text-white shadow-[0_0_20px_rgba(168,85,247,0.3)]
                hover:shadow-[0_0_30px_rgba(168,85,247,0.5)]
                transition-all duration-300"
            >
              {isLoading ? "保存中..." : isEditing ? "保存" : "创建"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
