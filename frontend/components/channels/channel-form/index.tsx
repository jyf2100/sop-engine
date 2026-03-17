"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { BasicInfoTab } from "./basic-info-tab";
import { TelegramConfigTab } from "./telegram-config-tab";
import { WhatsAppConfigTab } from "./whatsapp-config-tab";
import { FeishuConfigTab } from "./feishu-config-tab";

// Export the form data type for use in other components
export interface ChannelFormData {
  id: string;
  type: string;
  name: string;
  enabled: boolean;
  bot_token?: string;
  dm_policy?: string;
  allow_from?: string[];
  group_policy?: string;
  group_allow_from?: string[];
  groups?: Record<string, { requireMention?: boolean; allowFrom?: string[] }>;
  streaming?: string;
  media_max_mb?: number;
  phone_id?: string;
  // 飞书配置
  app_id?: string;
  app_secret?: string;
  encrypt_key?: string;
  verification_token?: string;
  // 凭据状态标记
  has_app_id?: boolean;
}

interface ChannelFormProps {
  data: ChannelFormData;
  onChange: (data: ChannelFormData) => void;
  isNew: boolean;
  hasExistingToken?: boolean;
  hasExistingAppCredentials?: boolean;
}

export function ChannelForm({ data, onChange, isNew, hasExistingToken, hasExistingAppCredentials }: ChannelFormProps) {
  const [activeTab, setActiveTab] = useState("basic");

  const updateField = <K extends keyof ChannelFormData>(field: K, value: ChannelFormData[K]) => {
    onChange({ ...data, [field]: value });
  };

  // 根据类型决定显示哪些标签页
  const showTelegramTab = data.type === "telegram";
  const showWhatsAppTab = data.type === "whatsapp";
  const showFeishuTab = data.type === "feishu";

  return (
    <div className="py-4">
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-2 mb-6">
          <TabsTrigger value="basic">基本信息</TabsTrigger>
          {showTelegramTab && (
            <TabsTrigger value="telegram">Telegram 配置</TabsTrigger>
          )}
          {showWhatsAppTab && (
            <TabsTrigger value="whatsapp">WhatsApp 配置</TabsTrigger>
          )}
          {showFeishuTab && (
            <TabsTrigger value="feishu">飞书配置</TabsTrigger>
          )}
        </TabsList>

        <TabsContent value="basic">
          <BasicInfoTab
            data={data}
            updateField={updateField}
            isNew={isNew}
          />
        </TabsContent>

        {showTelegramTab && (
          <TabsContent value="telegram">
            <TelegramConfigTab
              data={data}
              updateField={updateField}
              hasExistingToken={hasExistingToken}
            />
          </TabsContent>
        )}

        {showWhatsAppTab && (
          <TabsContent value="whatsapp">
            <WhatsAppConfigTab
              data={data}
              updateField={updateField}
            />
          </TabsContent>
        )}

        {showFeishuTab && (
          <TabsContent value="feishu">
            <FeishuConfigTab
              data={data}
              updateField={updateField}
              hasExistingCredentials={hasExistingAppCredentials}
            />
          </TabsContent>
        )}
      </Tabs>
    </div>
  );
}
