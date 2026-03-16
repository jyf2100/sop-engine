"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ChevronDown, ChevronRight, X, Plus } from "lucide-react";
import { JsonEditor } from "./json-editor";

// 心跳间隔预设
const HEARTBEAT_INTERVALS = [
  { value: "5m", label: "5 分钟" },
  { value: "10m", label: "10 分钟" },
  { value: "30m", label: "30 分钟" },
  { value: "1h", label: "1 小时" },
  { value: "2h", label: "2 小时" },
];

// 记忆搜索提供商
const MEMORY_PROVIDERS = [
  { value: "openai", label: "OpenAI" },
  { value: "pinecone", label: "Pinecone" },
  { value: "local", label: "本地" },
];

// 嵌入模型
const EMBEDDING_MODELS = [
  { value: "text-embedding-3-small", label: "text-embedding-3-small (推荐)" },
  { value: "text-embedding-3-large", label: "text-embedding-3-large" },
  { value: "text-embedding-ada-002", label: "text-embedding-ada-002" },
];

interface HeartbeatConfig {
  every: string;
  target: string;
}

interface MemorySearchConfig {
  enabled: boolean;
  provider: string;
  model: string;
}

interface GroupChatConfig {
  mentionPatterns: string[];
}

interface AdvancedConfig {
  heartbeat: HeartbeatConfig;
  memorySearch: MemorySearchConfig;
  groupChat: GroupChatConfig;
}

interface AdvancedConfigTabProps {
  config: AdvancedConfig;
  onChange: (config: AdvancedConfig) => void;
}

export function AdvancedConfigTab({ config, onChange }: AdvancedConfigTabProps) {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    heartbeat: true,
    memorySearch: true,
    groupChat: false,
  });

  const [newPattern, setNewPattern] = useState("");

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  const updateHeartbeat = (updates: Partial<HeartbeatConfig>) => {
    onChange({
      ...config,
      heartbeat: { ...config.heartbeat, ...updates },
    });
  };

  const updateMemorySearch = (updates: Partial<MemorySearchConfig>) => {
    onChange({
      ...config,
      memorySearch: { ...config.memorySearch, ...updates },
    });
  };

  const updateGroupChat = (updates: Partial<GroupChatConfig>) => {
    onChange({
      ...config,
      groupChat: { ...config.groupChat, ...updates },
    });
  };

  const addPattern = () => {
    if (newPattern.trim()) {
      const patterns = config.groupChat?.mentionPatterns || [];
      updateGroupChat({ mentionPatterns: [...patterns, newPattern.trim()] });
      setNewPattern("");
    }
  };

  const removePattern = (index: number) => {
    const patterns = config.groupChat?.mentionPatterns || [];
    updateGroupChat({
      mentionPatterns: patterns.filter((_, i) => i !== index),
    });
  };

  return (
    <div className="space-y-4">
      {/* 心跳配置 */}
      <div className="border rounded-lg">
        <button
          type="button"
          onClick={() => toggleSection("heartbeat")}
          className="w-full flex items-center justify-between p-4 hover:bg-zinc-50 dark:hover:bg-zinc-800"
        >
          <div className="flex items-center gap-2">
            {expandedSections.heartbeat ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
            <span className="font-medium">心跳配置</span>
          </div>
          <span className="text-xs text-zinc-500">
            {config.heartbeat?.every || "未配置"}
          </span>
        </button>
        {expandedSections.heartbeat && (
          <div className="p-4 pt-0 space-y-4 border-t">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label className="text-right">心跳间隔</Label>
              <Select
                value={config.heartbeat?.every || "30m"}
                onValueChange={(v) => updateHeartbeat({ every: v })}
              >
                <SelectTrigger className="col-span-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {HEARTBEAT_INTERVALS.map((interval) => (
                    <SelectItem key={interval.value} value={interval.value}>
                      {interval.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Label className="text-right">目标文件</Label>
              <Input
                value={config.heartbeat?.target || ""}
                onChange={(e) => updateHeartbeat({ target: e.target.value })}
                placeholder="heartbeat.md"
                className="col-span-1"
              />
            </div>
          </div>
        )}
      </div>

      {/* 记忆搜索配置 */}
      <div className="border rounded-lg">
        <button
          type="button"
          onClick={() => toggleSection("memorySearch")}
          className="w-full flex items-center justify-between p-4 hover:bg-zinc-50 dark:hover:bg-zinc-800"
        >
          <div className="flex items-center gap-2">
            {expandedSections.memorySearch ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
            <span className="font-medium">记忆搜索配置</span>
          </div>
          <span className="text-xs text-zinc-500">
            {config.memorySearch?.enabled ? "已启用" : "未启用"}
          </span>
        </button>
        {expandedSections.memorySearch && (
          <div className="p-4 pt-0 space-y-4 border-t">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label className="text-right">启用</Label>
              <div className="col-span-3 flex items-center gap-2">
                <Switch
                  checked={config.memorySearch?.enabled || false}
                  onCheckedChange={(v: boolean) => updateMemorySearch({ enabled: v })}
                />
                <span className="text-sm text-zinc-600">
                  {config.memorySearch?.enabled ? "已启用" : "未启用"}
                </span>
              </div>
            </div>

            {config.memorySearch?.enabled && (
              <>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label className="text-right">提供商</Label>
                  <Select
                    value={config.memorySearch?.provider || "openai"}
                    onValueChange={(v) => updateMemorySearch({ provider: v })}
                  >
                    <SelectTrigger className="col-span-3">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {MEMORY_PROVIDERS.map((provider) => (
                        <SelectItem key={provider.value} value={provider.value}>
                          {provider.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid grid-cols-4 items-center gap-4">
                  <Label className="text-right">嵌入模型</Label>
                  <Select
                    value={config.memorySearch?.model || "text-embedding-3-small"}
                    onValueChange={(v) => updateMemorySearch({ model: v })}
                  >
                    <SelectTrigger className="col-span-3">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {EMBEDDING_MODELS.map((model) => (
                        <SelectItem key={model.value} value={model.value}>
                          {model.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </>
            )}
          </div>
        )}
      </div>

      {/* 群聊配置 */}
      <div className="border rounded-lg">
        <button
          type="button"
          onClick={() => toggleSection("groupChat")}
          className="w-full flex items-center justify-between p-4 hover:bg-zinc-50 dark:hover:bg-zinc-800"
        >
          <div className="flex items-center gap-2">
            {expandedSections.groupChat ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
            <span className="font-medium">群聊配置</span>
          </div>
          <span className="text-xs text-zinc-500">
            {(config.groupChat?.mentionPatterns?.length || 0) > 0
              ? `${config.groupChat?.mentionPatterns?.length} 个模式`
              : "未配置"}
          </span>
        </button>
        {expandedSections.groupChat && (
          <div className="p-4 pt-0 space-y-4 border-t">
            <div className="grid grid-cols-4 items-start gap-4">
              <Label className="text-right pt-2">@ 提及模式</Label>
              <div className="col-span-3 space-y-2">
                <div className="flex flex-wrap gap-2">
                  {(config.groupChat?.mentionPatterns || []).map((pattern, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center gap-1 px-2 py-1 bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-100 rounded-md text-sm font-mono"
                    >
                      {pattern}
                      <button
                        type="button"
                        onClick={() => removePattern(index)}
                        className="hover:text-purple-600"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </span>
                  ))}
                </div>
                <div className="flex gap-2">
                  <Input
                    value={newPattern}
                    onChange={(e) => setNewPattern(e.target.value)}
                    placeholder="@\w+"
                    className="flex-1 font-mono"
                    onKeyDown={(e) => e.key === "Enter" && addPattern()}
                  />
                  <Button type="button" variant="outline" onClick={addPattern}>
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
                <p className="text-xs text-zinc-500">
                  正则表达式模式，用于匹配群聊中的 @ 提及
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 完整 JSON 配置 */}
      <details className="group border rounded-lg">
        <summary className="cursor-pointer text-sm font-medium p-4 hover:bg-zinc-50 dark:hover:bg-zinc-800 flex items-center gap-2">
          <span className="transition-transform group-open:rotate-90">▶</span>
          完整 JSON 配置
        </summary>
        <div className="p-4 pt-0 border-t">
          <JsonEditor
            value={config}
            onChange={onChange}
            height="200px"
          />
        </div>
      </details>
    </div>
  );
}
