# v2-m4: 前端适配 - 高级配置

## Goal

前端 UI 支持完整配置字段的编辑，包括高级配置 Tab、多账号管理、配置预设。

## PRD Trace

- **REQ-0001-029**: 前端适配 - 高级配置

## Scope

**包含**：
- Channel 高级配置 Tab：完整字段编辑
- Agent 高级配置 Tab：Session/Messages/Commands 配置
- 多账号管理 UI：账号列表、切换、配置
- 配置预设：常用配置快速应用
- JSON 编辑器：高级用户直接编辑 JSON

**不包含**：
- 所有高级字段的独立 UI（部分通过 JSON 编辑器）
- 配置版本对比 UI
- 配置导入/导出功能

## Acceptance

- [ ] `pnpm test` 全绿
- [ ] Channel 高级配置 Tab 可用
- [ ] Agent 高级配置 Tab 可用
- [ ] JSON 编辑器可用且验证通过
- [ ] 配置预设可一键应用
- [ ] E2E 测试覆盖配置流程

## Files

| 文件 | 操作 |
|------|------|
| `frontend/lib/api-client.ts` | 修改 - 新类型定义 |
| `frontend/components/channels/channel-form/advanced-tab.tsx` | 新增 |
| `frontend/components/channels/channel-form/accounts-tab.tsx` | 新增 |
| `frontend/components/agents/agent-form/session-tab.tsx` | 新增 |
| `frontend/components/agents/agent-form/messages-tab.tsx` | 新增 |
| `frontend/components/agents/agent-form/commands-tab.tsx` | 新增 |
| `frontend/components/ui/json-editor.tsx` | 新增 |
| `frontend/components/ui/config-preset.tsx` | 新增 |

## Steps

### Step 1: 更新类型定义

**实现**：
```typescript
// frontend/lib/api-client.ts

export interface SessionConfig {
  dm_scope: 'main' | 'per-peer' | 'per-channel-peer' | 'per-account-channel-peer';
  reset: {
    mode: 'daily' | 'idle';
    at_hour?: number;
    idle_minutes?: number;
  };
  maintenance?: {
    mode: 'warn' | 'enforce';
    prune_after?: string;
    max_entries?: number;
  };
}

export interface MessagesConfig {
  queue: {
    mode: 'steer' | 'followup' | 'collect' | 'interrupt';
  };
  inbound?: {
    debounce_ms?: number;
  };
}

export interface ChannelAccount {
  name?: string;
  enabled?: boolean;
  bot_token?: string;
  app_id?: string;
  app_secret?: string;
}

export interface ChannelConfig {
  // ... 现有字段
  accounts?: Record<string, ChannelAccount>;
  default_account?: string;
}
```

### Step 2: TDD Red - 测试高级配置 Tab

**写失败测试**：
```typescript
// frontend/components/channels/channel-form/__tests__/advanced-tab.test.tsx

describe('ChannelAdvancedTab', () => {
  it('should render all advanced fields', () => {
    render(<ChannelAdvancedTab channel={mockChannel} />);

    expect(screen.getByLabelText('Streaming Mode')).toBeInTheDocument();
    expect(screen.getByLabelText('Text Chunk Limit')).toBeInTheDocument();
    expect(screen.getByLabelText('Media Max MB')).toBeInTheDocument();
  });

  it('should save advanced config', async () => {
    const onSave = jest.fn();
    render(<ChannelAdvancedTab channel={mockChannel} onSave={onSave} />);

    fireEvent.change(screen.getByLabelText('Text Chunk Limit'), {
      target: { value: '4000' },
    });

    fireEvent.click(screen.getByText('Save'));

    await waitFor(() => {
      expect(onSave).toHaveBeenCalledWith(
        expect.objectContaining({ text_chunk_limit: 4000 })
      );
    });
  });
});
```

**运行到红**：
```bash
cd frontend && pnpm test components/channels/channel-form/__tests__/advanced-tab.test.tsx
# 预期：FAIL - 组件不存在
```

### Step 3: TDD Green - 实现高级配置 Tab

**实现**：
```tsx
// frontend/components/channels/channel-form/advanced-tab.tsx

export function ChannelAdvancedTab({ channel, onSave }: Props) {
  const [config, setConfig] = useState(channel);

  return (
    <div className="space-y-4">
      <div>
        <Label>Streaming Mode</Label>
        <Select
          value={config.streaming}
          onValueChange={(v) => setConfig({ ...config, streaming: v })}
        >
          <SelectItem value="off">Off</SelectItem>
          <SelectItem value="partial">Partial</SelectItem>
          <SelectItem value="block">Block</SelectItem>
        </Select>
      </div>

      <div>
        <Label>Text Chunk Limit</Label>
        <Input
          type="number"
          value={config.text_chunk_limit}
          onChange={(e) => setConfig({ ...config, text_chunk_limit: +e.target.value })}
        />
      </div>

      <Button onClick={() => onSave(config)}>Save</Button>
    </div>
  );
}
```

### Step 4: TDD Red - 测试多账号 Tab

**写失败测试**：
```typescript
describe('ChannelAccountsTab', () => {
  it('should list all accounts', () => {
    render(<ChannelAccountsTab accounts={mockAccounts} />);

    expect(screen.getByText('default')).toBeInTheDocument();
    expect(screen.getByText('alerts')).toBeInTheDocument();
  });

  it('should add new account', async () => {
    const onAdd = jest.fn();
    render(<ChannelAccountsTab accounts={mockAccounts} onAddAccount={onAdd} />);

    fireEvent.click(screen.getByText('Add Account'));

    await waitFor(() => {
      expect(onAdd).toHaveBeenCalled();
    });
  });
});
```

### Step 5: TDD Green - 实现多账号 Tab

### Step 6: TDD Red - 测试 JSON 编辑器

**写失败测试**：
```typescript
describe('JsonEditor', () => {
  it('should validate JSON', async () => {
    const onValidate = jest.fn();
    render(<JsonEditor value='{"valid": true}' onValidate={onValidate} />);

    fireEvent.change(screen.getByRole('textbox'), {
      target: { value: '{"invalid": }' },
    });

    await waitFor(() => {
      expect(onValidate).toHaveBeenCalledWith(false);
    });
  });
});
```

### Step 7: TDD Green - 实现 JSON 编辑器

### Step 8: 验证

```bash
cd frontend && pnpm test
cd frontend && pnpm build
```

## Risks

| 风险 | 缓解方式 |
|------|----------|
| UI 复杂度高 | 分 Tab 组织，职责清晰 |
| JSON 编辑体验 | 使用 Monaco Editor |
| 配置验证 | 后端严格验证 + 前端预验证 |

## DoD 硬度自检

| 检查项 | 结果 |
|--------|------|
| DoD 可二元判定 | ✅ 测试通过/失败 |
| 有验证命令 | ✅ pnpm test/build |
| 有反作弊条款 | ✅ JSON 验证 |
| Scope 明确 | ✅ 不包含版本对比 |
