"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Agent } from "@/lib/api-client";

interface BasicInfoTabProps {
  name: string;
  onNameChange: (value: string) => void;
  workspacePath?: string;
  isActive?: boolean;
  onIsActiveChange?: (value: boolean) => void;
  isDefault?: boolean;
  mode: "create" | "edit";
}

export function BasicInfoTab({
  name,
  onNameChange,
  workspacePath,
  isActive = true,
  onIsActiveChange,
  isDefault = false,
  mode,
}: BasicInfoTabProps) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-4 items-center gap-4">
        <Label htmlFor="name" className="text-right">
          名称 <span className="text-red-500">*</span>
        </Label>
        <Input
          id="name"
          value={name}
          onChange={(e) => onNameChange(e.target.value)}
          className="col-span-3"
          placeholder="我的 Agent"
          required
        />
      </div>

      {mode === "edit" && workspacePath && (
        <div className="grid grid-cols-4 items-center gap-4">
          <Label className="text-right text-zinc-500">工作目录</Label>
          <div className="col-span-3 text-sm font-mono text-zinc-500 bg-zinc-100 dark:bg-zinc-800 px-3 py-2 rounded-md">
            {workspacePath}
          </div>
        </div>
      )}

      {mode === "edit" && onIsActiveChange && (
        <div className="grid grid-cols-4 items-center gap-4">
          <Label htmlFor="active" className="text-right">
            状态
          </Label>
          <div className="col-span-3 flex items-center gap-2">
            <Switch
              id="active"
              checked={isActive}
              onCheckedChange={onIsActiveChange}
            />
            <span className="text-sm text-zinc-600">
              {isActive ? "激活" : "停用"}
            </span>
          </div>
        </div>
      )}

      {isDefault && (
        <div className="grid grid-cols-4 items-center gap-4">
          <Label className="text-right text-zinc-500">默认 Agent</Label>
          <div className="col-span-3 text-sm text-zinc-500">
            是（此为系统默认 Agent）
          </div>
        </div>
      )}
    </div>
  );
}
