"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Agent } from "@/lib/api-client";
import { BasicInfoTab } from "./basic-info-tab";
import { LlmConfigTab } from "./llm-config-tab";
import { SandboxConfigTab } from "./sandbox-config-tab";
import { ToolsConfigTab } from "./tools-config-tab";
import { AdvancedConfigTab } from "./advanced-config-tab";

// 默认 LLM 配置
const defaultLlmConfig = {
  base_url: "https://api.anthropic.com",
  api_key: "",
  primary: "claude-3-5-sonnet",
  fallbacks: [] as string[],
};

// 默认沙箱配置
const defaultSandboxConfig: {
  mode: string;
  workspaceAccess: string;
  scope: string[];
  docker?: {
    image?: string;
    memory?: string;
    cpu_count?: number;
    timeout?: string;
    network?: string;
    volumes?: string[];
    environment?: Record<string, string>;
  };
} = {
  mode: "non-main",
  workspaceAccess: "read-write",
  scope: [],
};

// 默认工具配置
const defaultToolsConfig = {
  profile: "default",
  allow: ["Bash", "Read", "Edit", "Glob", "Grep", "Write"],
  deny: [] as string[],
  exec: [] as string[],
};

// 默认高级配置
const defaultAdvancedConfig = {
  heartbeat: {
    every: "30m",
    target: "heartbeat.md",
  },
  memorySearch: {
    enabled: false,
    provider: "openai",
    model: "text-embedding-3-small",
  },
  groupChat: {
    mentionPatterns: [] as string[],
  },
};

export interface AgentFormData {
  name: string;
  isActive: boolean;
  llmConfig: typeof defaultLlmConfig;
  sandboxConfig: typeof defaultSandboxConfig;
  toolsConfig: typeof defaultToolsConfig;
  advancedConfig: typeof defaultAdvancedConfig;
}

interface AgentFormProps {
  mode: "create" | "edit";
  agent?: Agent;
  data: AgentFormData;
  onChange: (data: AgentFormData) => void;
}

export function AgentForm({ mode, agent, data, onChange }: AgentFormProps) {
  const [activeTab, setActiveTab] = useState("basic");

  const updateLlmConfig = (llmConfig: typeof defaultLlmConfig) => {
    onChange({ ...data, llmConfig });
  };

  const updateSandboxConfig = (sandboxConfig: typeof defaultSandboxConfig) => {
    onChange({ ...data, sandboxConfig });
  };

  const updateToolsConfig = (toolsConfig: typeof defaultToolsConfig) => {
    onChange({ ...data, toolsConfig });
  };

  const updateAdvancedConfig = (advancedConfig: typeof defaultAdvancedConfig) => {
    onChange({ ...data, advancedConfig });
  };

  return (
    <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
      <TabsList className="grid grid-cols-5 mb-4">
        <TabsTrigger value="basic">基本信息</TabsTrigger>
        <TabsTrigger value="llm">LLM 配置</TabsTrigger>
        <TabsTrigger value="sandbox">沙箱配置</TabsTrigger>
        <TabsTrigger value="tools">工具配置</TabsTrigger>
        <TabsTrigger value="advanced">高级配置</TabsTrigger>
      </TabsList>

      <TabsContent value="basic" className="mt-4">
        <BasicInfoTab
          name={data.name}
          onNameChange={(name) => onChange({ ...data, name })}
          workspacePath={agent?.workspace_path}
          isActive={data.isActive}
          onIsActiveChange={(isActive) => onChange({ ...data, isActive })}
          isDefault={agent?.is_default}
          mode={mode}
        />
      </TabsContent>

      <TabsContent value="llm" className="mt-4">
        <LlmConfigTab
          config={data.llmConfig}
          onChange={updateLlmConfig}
        />
      </TabsContent>

      <TabsContent value="sandbox" className="mt-4">
        <SandboxConfigTab
          config={data.sandboxConfig}
          onChange={updateSandboxConfig}
        />
      </TabsContent>

      <TabsContent value="tools" className="mt-4">
        <ToolsConfigTab
          config={data.toolsConfig}
          onChange={updateToolsConfig}
        />
      </TabsContent>

      <TabsContent value="advanced" className="mt-4">
        <AdvancedConfigTab
          config={data.advancedConfig}
          onChange={updateAdvancedConfig}
        />
      </TabsContent>
    </Tabs>
  );
}

// 辅助函数：从 Agent 创建表单数据
export function createFormDataFromAgent(agent?: Agent): AgentFormData {
  if (!agent) {
    return {
      name: "",
      isActive: true,
      llmConfig: { ...defaultLlmConfig },
      sandboxConfig: { ...defaultSandboxConfig },
      toolsConfig: { ...defaultToolsConfig },
      advancedConfig: { ...defaultAdvancedConfig },
    };
  }

  return {
    name: agent.name,
    isActive: agent.is_active,
    llmConfig: {
      base_url: (agent.llm_config?.base_url as string) || defaultLlmConfig.base_url,
      api_key: (agent.llm_config?.api_key as string) || "",
      primary: (agent.llm_config?.primary as string) || defaultLlmConfig.primary,
      fallbacks: (agent.llm_config?.fallbacks as string[]) || [],
    },
    sandboxConfig: {
      mode: (agent.sandbox_config?.mode as string) || defaultSandboxConfig.mode,
      workspaceAccess: (agent.sandbox_config?.workspaceAccess as string) || defaultSandboxConfig.workspaceAccess,
      scope: (agent.sandbox_config?.scope as string[]) || [],
      docker: agent.sandbox_config?.docker as typeof defaultSandboxConfig.docker,
    },
    toolsConfig: {
      profile: (agent.tools_config?.profile as string) || defaultToolsConfig.profile,
      allow: (agent.tools_config?.allow as string[]) || defaultToolsConfig.allow,
      deny: (agent.tools_config?.deny as string[]) || [],
      exec: (agent.tools_config?.exec as string[]) || [],
    },
    advancedConfig: {
      heartbeat: (agent.heartbeat_config as typeof defaultAdvancedConfig.heartbeat) || defaultAdvancedConfig.heartbeat,
      memorySearch: (agent.memory_search_config as typeof defaultAdvancedConfig.memorySearch) || defaultAdvancedConfig.memorySearch,
      groupChat: (agent.group_chat_config as typeof defaultAdvancedConfig.groupChat) || defaultAdvancedConfig.groupChat,
    },
  };
}

// 辅助函数：将表单数据转换为 API 请求格式
export function createApiPayloadFromFormData(data: AgentFormData, agentId?: string) {
  return {
    id: agentId,
    name: data.name,
    llm_config: {
      base_url: data.llmConfig.base_url,
      api_key: data.llmConfig.api_key || undefined,
      primary: data.llmConfig.primary,
      fallbacks: data.llmConfig.fallbacks,
    },
    sandbox_config: {
      mode: data.sandboxConfig.mode,
      workspaceAccess: data.sandboxConfig.workspaceAccess,
      scope: data.sandboxConfig.scope,
      docker: data.sandboxConfig.docker,
    },
    tools_config: {
      profile: data.toolsConfig.profile,
      allow: data.toolsConfig.allow,
      deny: data.toolsConfig.deny,
      exec: data.toolsConfig.exec,
    },
    heartbeat_config: data.advancedConfig.heartbeat,
    memory_search_config: data.advancedConfig.memorySearch,
    group_chat_config: data.advancedConfig.groupChat,
    is_active: data.isActive,
  };
}
