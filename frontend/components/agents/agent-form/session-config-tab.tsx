"use client";

import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, Trash2 } from "lucide-react";
import {
  SessionConfig,
  DmScope,
  ResetMode,
  MaintenanceMode,
} from "@/lib/api-client";

interface SessionConfigTabProps {
  config: SessionConfig | null | undefined;
  onChange: (config: SessionConfig) => void;
}

const DM_SCOPE_OPTIONS: { value: DmScope; label: string; description: string }[] = [
  { value: "main", label: "Main", description: "单一主会话" },
  { value: "per-peer", label: "Per-Peer", description: "每个对等体一个会话" },
  { value: "per-channel-peer", label: "Per-Channel-Peer", description: "每个渠道+对等体一个会话" },
  { value: "per-account-channel-peer", label: "Per-Account-Channel-Peer", description: "完整隔离" },
];

const RESET_MODE_OPTIONS: { value: ResetMode; label: string }[] = [
  { value: "daily", label: "每日重置" },
  { value: "idle", label: "空闲重置" },
];

const MAINTENANCE_MODE_OPTIONS: { value: MaintenanceMode; label: string }[] = [
  { value: "warn", label: "警告模式" },
  { value: "enforce", label: "强制模式" },
];

export function SessionConfigTab({ config, onChange }: SessionConfigTabProps) {
  const sessionConfig: SessionConfig = config || {};

  const updateField = <K extends keyof SessionConfig>(field: K, value: SessionConfig[K]) => {
    onChange({ ...sessionConfig, [field]: value });
  };

  const updateReset = (field: keyof NonNullable<SessionConfig["reset"]>, value: unknown) => {
    onChange({
      ...sessionConfig,
      reset: {
        ...sessionConfig.reset,
        [field]: value,
      } as NonNullable<SessionConfig["reset"]>,
    });
  };

  const updateMaintenance = (field: keyof NonNullable<SessionConfig["maintenance"]>, value: unknown) => {
    onChange({
      ...sessionConfig,
      maintenance: {
        ...sessionConfig.maintenance,
        [field]: value,
      } as NonNullable<SessionConfig["maintenance"]>,
    });
  };

  const addResetTrigger = () => {
    const triggers = sessionConfig.reset_triggers || [];
    updateField("reset_triggers", [...triggers, "/new"]);
  };

  const updateResetTrigger = (index: number, value: string) => {
    const triggers = [...(sessionConfig.reset_triggers || [])];
    triggers[index] = value;
    updateField("reset_triggers", triggers);
  };

  const removeResetTrigger = (index: number) => {
    const triggers = [...(sessionConfig.reset_triggers || [])];
    triggers.splice(index, 1);
    updateField("reset_triggers", triggers);
  };

  return (
    <div className="space-y-6">
      {/* DM Scope */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">DM Scope</CardTitle>
          <CardDescription>控制 DM 会话隔离策略</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>隔离模式</Label>
            <Select
              value={sessionConfig.dm_scope || "main"}
              onValueChange={(v: DmScope) => updateField("dm_scope", v)}
            >
              <SelectTrigger>
                <SelectValue placeholder="选择隔离模式" />
              </SelectTrigger>
              <SelectContent>
                {DM_SCOPE_OPTIONS.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    <div className="flex flex-col">
                      <span>{opt.label}</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {sessionConfig.dm_scope && (
              <p className="text-sm text-muted-foreground">
                {DM_SCOPE_OPTIONS.find((o) => o.value === sessionConfig.dm_scope)?.description}
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Reset Config */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">会话重置</CardTitle>
          <CardDescription>控制会话何时重置</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>重置模式</Label>
              <Select
                value={sessionConfig.reset?.mode || "daily"}
                onValueChange={(v: ResetMode) => updateReset("mode", v)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="选择重置模式" />
                </SelectTrigger>
                <SelectContent>
                  {RESET_MODE_OPTIONS.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {sessionConfig.reset?.mode === "daily" && (
              <div className="space-y-2">
                <Label>重置时间 (0-23)</Label>
                <Input
                  type="number"
                  min={0}
                  max={23}
                  value={sessionConfig.reset?.at_hour ?? 4}
                  onChange={(e) => updateReset("at_hour", parseInt(e.target.value))}
                />
              </div>
            )}

            {sessionConfig.reset?.mode === "idle" && (
              <div className="space-y-2">
                <Label>空闲分钟数</Label>
                <Input
                  type="number"
                  min={1}
                  value={sessionConfig.reset?.idle_minutes ?? 120}
                  onChange={(e) => updateReset("idle_minutes", parseInt(e.target.value))}
                />
              </div>
            )}
          </div>

          {/* Reset Triggers */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label>重置触发器</Label>
              <Button variant="outline" size="sm" onClick={addResetTrigger}>
                <Plus className="h-4 w-4 mr-1" />
                添加触发器
              </Button>
            </div>
            <div className="space-y-2">
              {(sessionConfig.reset_triggers || []).map((trigger, index) => (
                <div key={index} className="flex items-center gap-2">
                  <Input
                    value={trigger}
                    onChange={(e) => updateResetTrigger(index, e.target.value)}
                    placeholder="/reset"
                  />
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => removeResetTrigger(index)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Maintenance Config */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">维护配置</CardTitle>
          <CardDescription>控制会话存储维护</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>维护模式</Label>
              <Select
                value={sessionConfig.maintenance?.mode || "warn"}
                onValueChange={(v: MaintenanceMode) => updateMaintenance("mode", v)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="选择维护模式" />
                </SelectTrigger>
                <SelectContent>
                  {MAINTENANCE_MODE_OPTIONS.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>清理周期</Label>
              <Input
                value={sessionConfig.maintenance?.prune_after || "30d"}
                onChange={(e) => updateMaintenance("prune_after", e.target.value)}
                placeholder="30d"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>最大条目数</Label>
              <Input
                type="number"
                min={1}
                value={sessionConfig.maintenance?.max_entries ?? 500}
                onChange={(e) => updateMaintenance("max_entries", parseInt(e.target.value))}
              />
            </div>

            <div className="space-y-2">
              <Label>轮转大小</Label>
              <Input
                value={sessionConfig.maintenance?.rotate_bytes || "10mb"}
                onChange={(e) => updateMaintenance("rotate_bytes", e.target.value)}
                placeholder="10mb"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Thread Bindings */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">线程绑定</CardTitle>
          <CardDescription>控制会话与消息线程的绑定</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <Label htmlFor="thread-bindings-enabled">启用线程绑定</Label>
            <Switch
              id="thread-bindings-enabled"
              checked={sessionConfig.thread_bindings?.enabled ?? true}
              onCheckedChange={(checked: boolean) =>
                updateField("thread_bindings", {
                  ...sessionConfig.thread_bindings,
                  enabled: checked,
                })
              }
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>空闲自动解绑 (小时)</Label>
              <Input
                type="number"
                min={0}
                value={sessionConfig.thread_bindings?.idle_hours ?? 24}
                onChange={(e) =>
                  updateField("thread_bindings", {
                    ...sessionConfig.thread_bindings,
                    idle_hours: parseInt(e.target.value),
                  })
                }
              />
            </div>

            <div className="space-y-2">
              <Label>最大存活 (小时, 0=禁用)</Label>
              <Input
                type="number"
                min={0}
                value={sessionConfig.thread_bindings?.max_age_hours ?? 0}
                onChange={(e) =>
                  updateField("thread_bindings", {
                    ...sessionConfig.thread_bindings,
                    max_age_hours: parseInt(e.target.value),
                  })
                }
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 当前配置预览 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">配置预览</CardTitle>
          <CardDescription>当前 Session 配置的 JSON 预览</CardDescription>
        </CardHeader>
        <CardContent>
          <pre className="bg-muted p-4 rounded-md text-xs overflow-auto">
            {JSON.stringify(sessionConfig, null, 2)}
          </pre>
        </CardContent>
      </Card>
    </div>
  );
}
