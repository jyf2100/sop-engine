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
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { X, Plus } from "lucide-react";
import { JsonEditor } from "./json-editor";

// 沙箱模式
const SANDBOX_MODES = [
  { value: "non-main", label: "Non-Main (推荐)", desc: "非主进程隔离，安全且高效" },
  { value: "full-access", label: "Full-Access", desc: "完全访问权限，仅限信任环境" },
  { value: "restricted", label: "Restricted", desc: "受限模式，仅允许白名单操作" },
  { value: "docker", label: "Docker", desc: "容器隔离，最安全但开销最大" },
];

// 工作区访问权限
const WORKSPACE_ACCESS_OPTIONS = [
  { value: "none", label: "None", desc: "无访问权限" },
  { value: "read-only", label: "Read-Only", desc: "只读" },
  { value: "read-write", label: "Read-Write", desc: "读写" },
  { value: "full", label: "Full", desc: "完全访问" },
];

// 网络模式
const NETWORK_MODES = [
  { value: "bridge", label: "Bridge" },
  { value: "host", label: "Host" },
  { value: "none", label: "None" },
];

interface DockerConfig {
  image?: string;
  memory?: string;
  cpu_count?: number;
  timeout?: string;
  network?: string;
  volumes?: string[];
  environment?: Record<string, string>;
}

interface SandboxConfig {
  mode: string;
  workspaceAccess: string;
  scope: string[];
  docker?: DockerConfig;
}

interface SandboxConfigTabProps {
  config: SandboxConfig;
  onChange: (config: SandboxConfig) => void;
}

export function SandboxConfigTab({ config, onChange }: SandboxConfigTabProps) {
  const [newScope, setNewScope] = useState("");
  const [newVolume, setNewVolume] = useState("");
  const [newEnvKey, setNewEnvKey] = useState("");
  const [newEnvValue, setNewEnvValue] = useState("");

  const isDockerMode = config.mode === "docker";

  const updateDockerConfig = (updates: Partial<DockerConfig>) => {
    onChange({
      ...config,
      docker: { ...config.docker, ...updates },
    });
  };

  // 添加作用域
  const addScope = () => {
    if (newScope.trim()) {
      const scope = config.scope || [];
      onChange({ ...config, scope: [...scope, newScope.trim()] });
      setNewScope("");
    }
  };

  // 移除作用域
  const removeScope = (index: number) => {
    const scope = config.scope || [];
    onChange({ ...config, scope: scope.filter((_, i) => i !== index) });
  };

  // 添加挂载卷
  const addVolume = () => {
    if (newVolume.trim()) {
      const volumes = config.docker?.volumes || [];
      updateDockerConfig({ volumes: [...volumes, newVolume.trim()] });
      setNewVolume("");
    }
  };

  // 移除挂载卷
  const removeVolume = (index: number) => {
    const volumes = config.docker?.volumes || [];
    updateDockerConfig({ volumes: volumes.filter((_, i) => i !== index) });
  };

  // 添加环境变量
  const addEnvironment = () => {
    if (newEnvKey.trim()) {
      const environment = config.docker?.environment || {};
      updateDockerConfig({ environment: { ...environment, [newEnvKey]: newEnvValue } });
      setNewEnvKey("");
      setNewEnvValue("");
    }
  };

  // 移除环境变量
  const removeEnvironment = (key: string) => {
    const environment = config.docker?.environment || {};
    const { [key]: _, ...rest } = environment;
    updateDockerConfig({ environment: rest });
  };

  return (
    <div className="space-y-6">
      {/* 基本配置 */}
      <div className="space-y-4">
        <h4 className="font-medium">基本配置</h4>

        <div className="grid grid-cols-4 items-center gap-4">
          <Label className="text-right">沙箱模式</Label>
          <div className="col-span-3">
            <Select
              value={config.mode}
              onValueChange={(v) => onChange({ ...config, mode: v })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {SANDBOX_MODES.map((mode) => (
                  <SelectItem key={mode.value} value={mode.value}>
                    <div>
                      <span>{mode.label}</span>
                      <span className="text-xs text-zinc-500 ml-2">
                        {mode.desc}
                      </span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="grid grid-cols-4 items-center gap-4">
          <Label className="text-right">工作区访问</Label>
          <div className="col-span-3">
            <Select
              value={config.workspaceAccess || "read-write"}
              onValueChange={(v) => onChange({ ...config, workspaceAccess: v })}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {WORKSPACE_ACCESS_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* 作用域 */}
        <div className="grid grid-cols-4 items-start gap-4">
          <Label className="text-right pt-2">作用域</Label>
          <div className="col-span-3 space-y-2">
            {(config.scope || []).map((path, index) => (
              <div key={index} className="flex gap-2">
                <Input
                  value={path}
                  readOnly
                  className="flex-1 font-mono text-sm"
                />
                <Button
                  type="button"
                  variant="outline"
                  size="icon"
                  aria-label="移除作用域"
                  onClick={() => removeScope(index)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ))}
            <div className="flex gap-2">
              <Input
                value={newScope}
                onChange={(e) => setNewScope(e.target.value)}
                placeholder="/path/to/workspace"
                className="flex-1"
                onKeyDown={(e) => e.key === "Enter" && addScope()}
              />
              <Button type="button" variant="outline" onClick={addScope}>
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Docker 高级配置 */}
      {isDockerMode && (
        <div className="space-y-4 border-t pt-4">
          <h4 className="font-medium">Docker 配置</h4>

          <div className="grid grid-cols-4 items-center gap-4">
            <Label className="text-right">镜像</Label>
            <Input
              value={config.docker?.image || "ubuntu:22.04"}
              onChange={(e) => updateDockerConfig({ image: e.target.value })}
              className="col-span-3"
              placeholder="ubuntu:22.04"
            />
          </div>

          <div className="grid grid-cols-4 items-center gap-4">
            <Label className="text-right">内存</Label>
            <Input
              value={config.docker?.memory || "2g"}
              onChange={(e) => updateDockerConfig({ memory: e.target.value })}
              className="col-span-1"
              placeholder="2g"
            />
            <Label className="text-right">CPU</Label>
            <Input
              type="number"
              value={config.docker?.cpu_count || 1}
              onChange={(e) =>
                updateDockerConfig({ cpu_count: parseInt(e.target.value) || 1 })
              }
              className="col-span-1"
              min={1}
              max={16}
            />
          </div>

          <div className="grid grid-cols-4 items-center gap-4">
            <Label className="text-right">超时</Label>
            <Input
              value={config.docker?.timeout || "30m"}
              onChange={(e) => updateDockerConfig({ timeout: e.target.value })}
              className="col-span-1"
              placeholder="30m"
            />
            <Label className="text-right">网络</Label>
            <div className="col-span-1">
              <Select
                value={config.docker?.network || "bridge"}
                onValueChange={(v) => updateDockerConfig({ network: v })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {NETWORK_MODES.map((mode) => (
                    <SelectItem key={mode.value} value={mode.value}>
                      {mode.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* 挂载卷 */}
          <div className="grid grid-cols-4 items-start gap-4">
            <Label className="text-right pt-2">挂载卷</Label>
            <div className="col-span-3 space-y-2">
              {(config.docker?.volumes || []).map((vol, index) => (
                <div key={index} className="flex gap-2">
                  <Input
                    value={vol}
                    readOnly
                    className="flex-1 font-mono text-sm"
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    aria-label="移除挂载卷"
                    onClick={() => removeVolume(index)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ))}
              <div className="flex gap-2">
                <Input
                  value={newVolume}
                  onChange={(e) => setNewVolume(e.target.value)}
                  placeholder="/host/path:/container/path"
                  className="flex-1"
                  onKeyDown={(e) => e.key === "Enter" && addVolume()}
                />
                <Button type="button" variant="outline" onClick={addVolume}>
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>

          {/* 环境变量 */}
          <div className="grid grid-cols-4 items-start gap-4">
            <Label className="text-right pt-2">环境变量</Label>
            <div className="col-span-3 space-y-2">
              {Object.entries(config.docker?.environment || {}).map(([key, value]) => (
                <div key={key} className="flex gap-2">
                  <Input value={key} readOnly className="flex-1" />
                  <Input value={value as string} readOnly className="flex-1" />
                  <Button
                    type="button"
                    variant="outline"
                    size="icon"
                    aria-label="移除环境变量"
                    onClick={() => removeEnvironment(key)}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              ))}
              <div className="flex gap-2">
                <Input
                  value={newEnvKey}
                  onChange={(e) => setNewEnvKey(e.target.value)}
                  placeholder="KEY"
                  className="flex-1"
                />
                <Input
                  value={newEnvValue}
                  onChange={(e) => setNewEnvValue(e.target.value)}
                  placeholder="value"
                  className="flex-1"
                />
                <Button type="button" variant="outline" onClick={addEnvironment}>
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
            </div>
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
            <JsonEditor
              value={config}
              onChange={onChange}
              height="150px"
            />
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}
