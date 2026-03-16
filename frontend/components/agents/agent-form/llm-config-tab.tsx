"use client";

import { useState } from "react";
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
import { X, Plus, Eye, EyeOff, TestTube } from "lucide-react";
import { JsonEditor } from "./json-editor";

// 可用模型列表
const AVAILABLE_MODELS = [
  { value: "claude-3-5-sonnet", label: "Claude 3.5 Sonnet (推荐)" },
  { value: "claude-3-opus", label: "Claude 3 Opus" },
  { value: "claude-3-sonnet", label: "Claude 3 Sonnet" },
  { value: "claude-3-haiku", label: "Claude 3 Haiku" },
  { value: "claude-sonnet-4-20250514", label: "Claude Sonnet 4" },
  { value: "claude-opus-4-20250514", label: "Claude Opus 4" },
];

// API 端点预设
const API_PRESETS = [
  { value: "anthropic", label: "Anthropic", url: "https://api.anthropic.com" },
  { value: "openai", label: "OpenAI", url: "https://api.openai.com/v1" },
  { value: "custom", label: "自定义", url: "" },
];

interface LlmConfig {
  base_url: string;
  api_key: string;
  primary: string;
  fallbacks: string[];
}

interface LlmConfigTabProps {
  config: LlmConfig;
  onChange: (config: LlmConfig) => void;
}

export function LlmConfigTab({ config, onChange }: LlmConfigTabProps) {
  const [showApiKey, setShowApiKey] = useState(false);
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<"success" | "error" | null>(null);

  // 确定当前预设
  const getCurrentPreset = () => {
    const preset = API_PRESETS.find((p) => p.url === config.base_url);
    return preset ? preset.value : "custom";
  };

  const handlePresetChange = (preset: string) => {
    const found = API_PRESETS.find((p) => p.value === preset);
    if (found) {
      onChange({ ...config, base_url: found.url });
    }
  };

  const handlePrimaryChange = (model: string) => {
    onChange({ ...config, primary: model });
  };

  const addFallback = () => {
    const fallbacks = config.fallbacks || [];
    const defaultModel = AVAILABLE_MODELS.find((m) => m.value !== config.primary)?.value;
    if (defaultModel) {
      onChange({ ...config, fallbacks: [...fallbacks, defaultModel] });
    }
  };

  const removeFallback = (index: number) => {
    const fallbacks = config.fallbacks || [];
    onChange({
      ...config,
      fallbacks: fallbacks.filter((_, i) => i !== index),
    });
  };

  const updateFallback = (index: number, model: string) => {
    const fallbacks = config.fallbacks || [];
    fallbacks[index] = model;
    onChange({ ...config, fallbacks: [...fallbacks] });
  };

  const testConnection = async () => {
    if (!config.base_url || !config.api_key) {
      setTestResult("error");
      return;
    }

    setTesting(true);
    setTestResult(null);

    try {
      // 简单的连接测试 - 发送一个最小请求
      const response = await fetch(`${config.base_url}/v1/messages`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-api-key": config.api_key,
          "anthropic-version": "2023-06-01",
        },
        body: JSON.stringify({
          model: config.primary,
          max_tokens: 1,
          messages: [{ role: "user", content: "Hi" }],
        }),
      });

      setTestResult(response.ok ? "success" : "error");
    } catch {
      setTestResult("error");
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* API 端点配置 */}
      <div className="space-y-4">
        <h4 className="font-medium">API 端点</h4>
        <div className="grid grid-cols-4 items-center gap-4">
          <Label className="text-right">预设</Label>
          <div className="col-span-3">
            <Select value={getCurrentPreset()} onValueChange={handlePresetChange}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {API_PRESETS.map((preset) => (
                  <SelectItem key={preset.value} value={preset.value}>
                    {preset.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="grid grid-cols-4 items-center gap-4">
          <Label htmlFor="base-url" className="text-right">
            Base URL
          </Label>
          <Input
            id="base-url"
            value={config.base_url || ""}
            onChange={(e) => onChange({ ...config, base_url: e.target.value })}
            className="col-span-2"
            placeholder="https://api.anthropic.com"
          />
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={testConnection}
            disabled={testing || !config.base_url || !config.api_key}
          >
            <TestTube className="h-3 w-3 mr-1" />
            {testing ? "测试中..." : "测试连接"}
          </Button>
        </div>

        {testResult && (
          <div
            className={`text-sm flex items-center gap-1 ${
              testResult === "success" ? "text-green-500" : "text-red-500"
            }`}
          >
            {testResult === "success" ? "✓ 连接成功" : "✕ 连接失败"}
          </div>
        )}

        <div className="grid grid-cols-4 items-center gap-4">
          <Label htmlFor="api-key" className="text-right">
            API Key
          </Label>
          <div className="col-span-3 relative">
            <Input
              id="api-key"
              type={showApiKey ? "text" : "password"}
              value={config.api_key || ""}
              onChange={(e) => onChange({ ...config, api_key: e.target.value })}
              placeholder="sk-ant-..."
              className="pr-10"
            />
            <button
              type="button"
              className="absolute right-2 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-zinc-600"
              onClick={() => setShowApiKey(!showApiKey)}
            >
              {showApiKey ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </button>
          </div>
        </div>
      </div>

      {/* 模型配置 */}
      <div className="space-y-4">
        <h4 className="font-medium">模型配置</h4>
        <div className="grid grid-cols-4 items-center gap-4">
          <Label htmlFor="primary" className="text-right">
            主模型
          </Label>
          <div className="col-span-3">
            <Select value={config.primary} onValueChange={handlePrimaryChange}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {AVAILABLE_MODELS.map((model) => (
                  <SelectItem key={model.value} value={model.value}>
                    {model.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* 备用模型 */}
        <div className="grid grid-cols-4 items-start gap-4">
          <Label className="text-right pt-2">备用模型</Label>
          <div className="col-span-3 space-y-2">
            {(config.fallbacks || []).map((model, index) => (
              <div key={index} className="flex gap-2">
                <Select value={model} onValueChange={(v) => updateFallback(index, v)}>
                  <SelectTrigger className="flex-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {AVAILABLE_MODELS.filter(
                      (m) => m.value !== config.primary
                    ).map((m) => (
                      <SelectItem key={m.value} value={m.value}>
                        {m.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
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
      </div>

      {/* 高级 JSON 配置 */}
      <details className="group">
        <summary className="cursor-pointer text-sm font-medium text-zinc-600 hover:text-zinc-900 flex items-center gap-1">
          <span className="transition-transform group-open:rotate-90">▶</span>
          高级配置 (JSON)
        </summary>
        <div className="mt-3">
          <JsonEditor
            value={config}
            onChange={onChange}
            height="150px"
          />
        </div>
      </details>
    </div>
  );
}
