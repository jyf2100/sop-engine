# v2-m5: E2E 测试完善

## Goal

确保完整用户流程可自动化验证，覆盖 v2 所有新功能。

## PRD Trace

- **REQ-0001-030**: E2E 测试完善

## Scope

**包含**：
- Channel 配置流程 E2E：创建 → 配置 → 同步 → 验证
- Agent 配置流程 E2E：创建 → 高级配置 → 同步 → 验证
- Bindings 流程 E2E：创建 → 配置 → 路由验证
- 回归测试：v1 功能不受影响

**不包含**：
- 所有边界场景（单元测试覆盖）
- 性能测试
- 压力测试

## Acceptance

- [ ] 所有 E2E 测试通过
- [ ] 覆盖核心用户流程
- [ ] 测试可重复运行
- [ ] CI 集成成功

## Files

| 文件 | 操作 |
|------|------|
| `frontend/e2e/channel-config-flow.spec.ts` | 新增 |
| `frontend/e2e/agent-advanced-config-flow.spec.ts` | 新增 |
| `frontend/e2e/bindings-flow.spec.ts` | 新增 |
| `frontend/e2e/regression-v1.spec.ts` | 新增 |
| `frontend/playwright.config.ts` | 修改 - 新配置 |

## Steps

### Step 1: Channel 配置流程 E2E

**实现**：
```typescript
// frontend/e2e/channel-config-flow.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Channel Configuration Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/channels');
  });

  test('should create Telegram channel with multi-account', async ({ page }) => {
    // 1. 点击创建
    await page.click('text=Create Channel');

    // 2. 选择类型
    await page.selectOption('[data-testid="channel-type"]', 'telegram');

    // 3. 填写基础信息
    await page.fill('[data-testid="channel-name"]', 'Test Telegram');

    // 4. 切换到多账号 Tab
    await page.click('text=Accounts');

    // 5. 添加账号
    await page.click('text=Add Account');
    await page.fill('[data-testid="account-name"]', 'alerts');
    await page.fill('[data-testid="account-bot-token"]', 'test-token-yyy');

    // 6. 保存
    await page.click('text=Save');

    // 7. 验证成功
    await expect(page.locator('text=Channel created')).toBeVisible();

    // 8. 验证列表显示
    await expect(page.locator('text=Test Telegram')).toBeVisible();
  });

  test('should preserve non-managed fields on sync', async ({ page }) => {
    // 1. 打开已有 Channel
    await page.click('text=Test Telegram');

    // 2. 切换到高级配置
    await page.click('text=Advanced');

    // 3. 修改字段
    await page.fill('[data-testid="text-chunk-limit"]', '4000');

    // 4. 保存
    await page.click('text=Save');

    // 5. 验证同步成功
    await expect(page.locator('text=Synced')).toBeVisible();

    // 6. 验证非管理字段保留（通过 API）
    const response = await page.request.get('/api/channels/test-telegram/openclaw-config');
    const config = await response.json();
    expect(config.customField).toBe('preserved');
  });
});
```

### Step 2: Agent 高级配置流程 E2E

**实现**：
```typescript
// frontend/e2e/agent-advanced-config-flow.spec.ts

test.describe('Agent Advanced Configuration Flow', () => {
  test('should configure session settings', async ({ page }) => {
    await page.goto('/agents');

    // 1. 创建 Agent
    await page.click('text=Create Agent');
    await page.fill('[data-testid="agent-name"]', 'Test Agent');
    await page.click('text=Save');

    // 2. 打开详情
    await page.click('text=Test Agent');

    // 3. 切换到 Session 配置
    await page.click('text=Session');

    // 4. 配置 DM Scope
    await page.selectOption('[data-testid="dm-scope"]', 'per-peer');

    // 5. 配置重置策略
    await page.selectOption('[data-testid="reset-mode"]', 'idle');
    await page.fill('[data-testid="idle-minutes"]', '120');

    // 6. 保存
    await page.click('text=Save');

    // 7. 验证
    await expect(page.locator('text=Session config saved')).toBeVisible();
  });

  test('should configure messages queue', async ({ page }) => {
    await page.goto('/agents');

    // 1. 打开 Agent
    await page.click('text=Test Agent');

    // 2. 切换到 Messages 配置
    await page.click('text=Messages');

    // 3. 配置队列模式
    await page.selectOption('[data-testid="queue-mode"]', 'steer');

    // 4. 配置防抖
    await page.fill('[data-testid="debounce-ms"]', '500');

    // 5. 保存
    await page.click('text=Save');

    // 6. 验证
    await expect(page.locator('text=Messages config saved')).toBeVisible();
  });
});
```

### Step 3: Bindings 流程 E2E

**实现**：
```typescript
// frontend/e2e/bindings-flow.spec.ts

test.describe('Bindings Flow', () => {
  test('should create route binding', async ({ page }) => {
    await page.goto('/bindings');

    // 1. 创建绑定
    await page.click('text=Create Binding');

    // 2. 选择类型
    await page.selectOption('[data-testid="binding-type"]', 'route');

    // 3. 选择 Agent
    await page.selectOption('[data-testid="agent-id"]', 'test-agent');

    // 4. 配置匹配规则
    await page.selectOption('[data-testid="match-channel"]', 'telegram');
    await page.fill('[data-testid="match-guild-id"]', '12345');

    // 5. 保存
    await page.click('text=Save');

    // 6. 验证
    await expect(page.locator('text=Binding created')).toBeVisible();
  });
});
```

### Step 4: 回归测试

**实现**：
```typescript
// frontend/e2e/regression-v1.spec.ts

test.describe('v1 Regression Tests', () => {
  test('should still work: template management', async ({ page }) => {
    await page.goto('/templates');

    // 验证 v1 模板功能正常
    await expect(page.locator('table')).toBeVisible();
  });

  test('should still work: execution monitoring', async ({ page }) => {
    await page.goto('/executions');

    // 验证 v1 执行监控功能正常
    await expect(page.locator('table')).toBeVisible();
  });

  test('should still work: approval workflow', async ({ page }) => {
    await page.goto('/approvals');

    // 验证 v1 审批功能正常
    await expect(page.locator('table')).toBeVisible();
  });
});
```

### Step 5: CI 集成

**更新**：
```yaml
# .github/workflows/e2e.yml

name: E2E Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  e2e:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s

      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'pnpm'

      - name: Install dependencies
        run: cd frontend && pnpm install

      - name: Install Playwright
        run: cd frontend && npx playwright install --with-deps

      - name: Run E2E tests
        run: cd frontend && pnpm test:e2e

      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report
          path: frontend/playwright-report/
          retention-days: 30
```

### Step 6: 运行验证

```bash
# 本地运行 E2E
cd frontend && pnpm test:e2e

# 验证所有测试通过
npx playwright test --reporter=list
```

## Risks

| 风险 | 缓解方式 |
|------|----------|
| E2E 测试不稳定 | 添加重试和等待 |
| CI 超时 | 分片运行测试 |
| 测试数据管理 | 使用独立的测试数据库 |

## DoD 硬度自检

| 检查项 | 结果 |
|--------|------|
| DoD 可二元判定 | ✅ 测试通过/失败 |
| 有验证命令 | ✅ pnpm test:e2e |
| 有反作弊条款 | ✅ 回归测试验证 |
| Scope 明确 | ✅ 不包含性能测试 |
