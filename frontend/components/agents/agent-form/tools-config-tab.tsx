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
import { X, Plus } from "lucide-react";
import { JsonEditor } from "./json-editor";

// 工具配置文件预设
const TOOL_PROFILES = [
  {
    value: "default",
    label: "默认配置",
    desc: "允许常用工具",
    allow: ["Bash", "Read", "Edit", "Glob", "Grep", "Write"],
    deny: [],
  },
  {
    value: "restricted",
    label: "受限配置",
    desc: "仅允许读取类工具",
    allow: ["Read", "Glob", "Grep"],
    deny: ["Bash", "Write", "Edit"],
  },
  {
    value: "full-access",
    label: "完全访问",
    desc: "允许所有工具",
    allow: [],
    deny: [],
  },
  {
    value: "custom",
    label: "自定义",
    desc: "手动配置",
    allow: [],
    deny: [],
  },
];

// 可用工具列表
const AVAILABLE_TOOLS = [
  { value: "Bash", label: "Bash", desc: "执行 Shell 命令" },
  { value: "Read", label: "Read", desc: "读取文件" },
  { value: "Edit", label: "Edit", desc: "编辑文件" },
  { value: "Write", label: "Write", desc: "写入文件" },
  { value: "Glob", label: "Glob", desc: "文件模式匹配" },
  { value: "Grep", label: "Grep", desc: "内容搜索" },
  { value: "WebFetch", label: "WebFetch", desc: "获取网页内容" },
  { value: "WebSearch", label: "WebSearch", desc: "网络搜索" },
  { value: "Agent", label: "Agent", desc: "启动子 Agent" },
  { value: "TaskOutput", label: "TaskOutput", desc: "获取任务输出" },
  { value: "NotebookEdit", label: "NotebookEdit", desc: "编辑 Jupyter Notebook" },
  { value: "CronCreate", label: "CronCreate", desc: "创建定时任务" },
  { value: "CronDelete", label: "CronDelete", desc: "删除定时任务" },
  { value: "CronList", label: "CronList", desc: "列出定时任务" },
  { value: "ExitPlanMode", label: "ExitPlanMode", desc: "退出计划模式" },
  { value: "EnterPlanMode", label: "EnterPlanMode", desc: "进入计划模式" },
  { value: "TaskCreate", label: "TaskCreate", desc: "创建任务" },
  { value: "TaskUpdate", label: "TaskUpdate", desc: "更新任务" },
  { value: "TaskList", label: "TaskList", desc: "列出任务" },
  { value: "TaskGet", label: "TaskGet", desc: "获取任务" },
  { value: "TaskStop", label: "TaskStop", desc: "停止任务" },
  { value: "EnterWorktree", label: "EnterWorktree", desc: "进入工作树" },
  { value: "ExitWorktree", label: "ExitWorktree", desc: "退出工作树" },
  { value: "AskUserQuestion", label: "AskUserQuestion", desc: "询问用户" },
];

interface ToolsConfig {
  profile: string;
  allow: string[];
  deny: string[];
  exec: string[];
}

interface ToolsConfigTabProps {
  config: ToolsConfig;
  onChange: (config: ToolsConfig) => void;
}

export function ToolsConfigTab({ config, onChange }: ToolsConfigTabProps) {
  const [newAllow, setNewAllow] = useState("");
  const [newDeny, setNewDeny] = useState("");
  const [newExec, setNewExec] = useState("");

  const isCustomProfile = config.profile === "custom" || !config.profile;

  // 处理预设变化
  const handleProfileChange = (profile: string) => {
    const preset = TOOL_PROFILES.find((p) => p.value === profile);
    if (preset && profile !== "custom") {
      onChange({
        profile,
        allow: preset.allow,
        deny: preset.deny,
        exec: [],
      });
    } else {
      onChange({ ...config, profile });
    }
  };

  // 添加允许的工具
  const addAllow = () => {
    if (newAllow && !(config.allow || []).includes(newAllow)) {
      onChange({ ...config, allow: [...(config.allow || []), newAllow] });
      setNewAllow("");
    }
  };

  // 移除允许的工具
  const removeAllow = (tool: string) => {
    onChange({
      ...config,
      allow: (config.allow || []).filter((t) => t !== tool),
    });
  };

  // 添加禁止的工具
  const addDeny = () => {
    if (newDeny && !(config.deny || []).includes(newDeny)) {
      onChange({ ...config, deny: [...(config.deny || []), newDeny] });
      setNewDeny("");
    }
  };

  // 移除禁止的工具
  const removeDeny = (tool: string) => {
    onChange({
      ...config,
      deny: (config.deny || []).filter((t) => t !== tool),
    });
  };

  // 添加执行命令
  const addExec = () => {
    if (newExec.trim() && !(config.exec || []).includes(newExec.trim())) {
      onChange({ ...config, exec: [...(config.exec || []), newExec.trim()] });
      setNewExec("");
    }
  };

  // 移除执行命令
  const removeExec = (cmd: string) => {
    onChange({
      ...config,
      exec: (config.exec || []).filter((c) => c !== cmd),
    });
  };

  return (
    <div className="space-y-6">
      {/* 工具配置文件 */}
      <div className="grid grid-cols-4 items-center gap-4">
        <Label className="text-right">配置文件</Label>
        <div className="col-span-3">
          <Select
            value={config.profile || "default"}
            onValueChange={handleProfileChange}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {TOOL_PROFILES.map((profile) => (
                <SelectItem key={profile.value} value={profile.value}>
                  <div>
                    <span>{profile.label}</span>
                    <span className="text-xs text-zinc-500 ml-2">
                      {profile.desc}
                    </span>
                  </div>
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* 允许的工具 */}
      <div className="grid grid-cols-4 items-start gap-4">
        <Label className="text-right pt-2">允许的工具</Label>
        <div className="col-span-3 space-y-2">
          <div className="flex flex-wrap gap-2">
            {(config.allow || []).map((tool) => (
              <span
                key={tool}
                className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100 rounded-md text-sm"
              >
                {tool}
                <button
                  type="button"
                  onClick={() => removeAllow(tool)}
                  className="hover:text-green-600"
                >
                  <X className="h-3 w-3" />
                </button>
              </span>
            ))}
          </div>
          <div className="flex gap-2">
            <Select value={newAllow} onValueChange={setNewAllow}>
              <SelectTrigger className="flex-1">
                <SelectValue placeholder="选择工具..." />
              </SelectTrigger>
              <SelectContent>
                {AVAILABLE_TOOLS.filter(
                  (t) => !(config.allow || []).includes(t.value)
                ).map((tool) => (
                  <SelectItem key={tool.value} value={tool.value}>
                    <div>
                      <span>{tool.label}</span>
                      <span className="text-xs text-zinc-500 ml-2">
                        {tool.desc}
                      </span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button type="button" variant="outline" onClick={addAllow}>
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* 禁止的工具 */}
      <div className="grid grid-cols-4 items-start gap-4">
        <Label className="text-right pt-2">禁止的工具</Label>
        <div className="col-span-3 space-y-2">
          <div className="flex flex-wrap gap-2">
            {(config.deny || []).map((tool) => (
              <span
                key={tool}
                className="inline-flex items-center gap-1 px-2 py-1 bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100 rounded-md text-sm"
              >
                {tool}
                <button
                  type="button"
                  onClick={() => removeDeny(tool)}
                  className="hover:text-red-600"
                >
                  <X className="h-3 w-3" />
                </button>
              </span>
            ))}
          </div>
          <div className="flex gap-2">
            <Select value={newDeny} onValueChange={setNewDeny}>
              <SelectTrigger className="flex-1">
                <SelectValue placeholder="选择工具..." />
              </SelectTrigger>
              <SelectContent>
                {AVAILABLE_TOOLS.filter(
                  (t) => !(config.deny || []).includes(t.value)
                ).map((tool) => (
                  <SelectItem key={tool.value} value={tool.value}>
                    <div>
                      <span>{tool.label}</span>
                      <span className="text-xs text-zinc-500 ml-2">
                        {tool.desc}
                      </span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button type="button" variant="outline" onClick={addDeny}>
              <Plus className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* 执行命令白名单 (仅自定义模式显示) */}
      {isCustomProfile && (
        <div className="grid grid-cols-4 items-start gap-4">
          <Label className="text-right pt-2">命令白名单</Label>
          <div className="col-span-3 space-y-2">
            <div className="flex flex-wrap gap-2">
              {(config.exec || []).map((cmd) => (
                <span
                  key={cmd}
                  className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100 rounded-md text-sm font-mono"
                >
                  {cmd}
                  <button
                    type="button"
                    onClick={() => removeExec(cmd)}
                    className="hover:text-blue-600"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </span>
              ))}
            </div>
            <div className="flex gap-2">
              <Input
                value={newExec}
                onChange={(e) => setNewExec(e.target.value)}
                placeholder="git, npm, pip..."
                className="flex-1"
                onKeyDown={(e) => e.key === "Enter" && addExec()}
              />
              <Button type="button" variant="outline" onClick={addExec}>
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            <p className="text-xs text-zinc-500">
              允许执行的命令列表，留空表示允许所有命令
            </p>
          </div>
        </div>
      )}

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
