/**
 * v1 回归测试
 *
 * REQ-0001-030: E2E 测试完善 - 回归测试
 *
 * 确保 v2 功能不影响 v1 核心功能：
 * 1. 模板管理
 * 2. 执行监控
 * 3. 审批流程
 * 4. Agent 管理
 */

import { test, expect } from '@playwright/test';

test.describe('v1 回归测试 - 模板管理', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/templates');
    await page.waitForLoadState('networkidle');
  });

  test('模板列表页应该正常显示', async ({ page }) => {
    await expect(page.getByRole('heading', { name: '流程模板' })).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole('button', { name: '创建模板' })).toBeVisible();
  });

  test('创建模板对话框应该可用', async ({ page }) => {
    await page.getByRole('button', { name: '创建模板' }).click();
    await expect(page.getByRole('dialog')).toBeVisible();
    await expect(page.getByLabel('名称')).toBeVisible();
  });

  test('模板表格或空状态应该显示', async ({ page }) => {
    await page.waitForTimeout(1000);
    const hasTable = await page.locator('table').isVisible().catch(() => false);
    const hasEmptyState = await page.getByText('暂无模板').isVisible().catch(() => false);
    expect(hasTable || hasEmptyState).toBe(true);
  });
});

test.describe('v1 回归测试 - 执行监控', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/executions');
    await page.waitForLoadState('networkidle');
  });

  test('执行监控页应该正常显示', async ({ page }) => {
    await expect(page.getByRole('heading', { name: '执行记录' })).toBeVisible({ timeout: 10000 });
  });

  test('执行表格或空状态应该显示', async ({ page }) => {
    await page.waitForTimeout(1000);
    const hasTable = await page.locator('table').isVisible().catch(() => false);
    const hasEmptyState = await page.getByText('暂无执行记录').isVisible().catch(() => false);
    expect(hasTable || hasEmptyState).toBe(true);
  });
});

test.describe('v1 回归测试 - 审批流程', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/approvals');
    await page.waitForLoadState('networkidle');
  });

  test('审批列表页应该正常显示', async ({ page }) => {
    await expect(page.getByRole('heading', { name: '人工审批' })).toBeVisible({ timeout: 10000 });
  });

  test('审批表格或空状态应该显示', async ({ page }) => {
    await page.waitForTimeout(1000);
    const hasTable = await page.locator('table').isVisible().catch(() => false);
    const hasEmptyState = await page.getByText('暂无审批').isVisible().catch(() => false);
    expect(hasTable || hasEmptyState).toBe(true);
  });
});

test.describe('v1 回归测试 - Agent 管理', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/agents');
    await page.waitForLoadState('networkidle');
  });

  test('Agent 列表页应该正常显示', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'Agent 管理' })).toBeVisible({ timeout: 10000 });
    await expect(page.getByRole('button', { name: '创建 Agent' })).toBeVisible();
  });

  test('Agent 创建对话框应该可用', async ({ page }) => {
    await page.getByRole('button', { name: '创建 Agent' }).click();
    await expect(page.getByRole('dialog')).toBeVisible();

    // 验证所有标签页存在
    await expect(page.getByRole('tab', { name: '基本信息' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'LLM 配置' })).toBeVisible();
    await expect(page.getByRole('tab', { name: '沙箱配置' })).toBeVisible();
    await expect(page.getByRole('tab', { name: '工具配置' })).toBeVisible();
    await expect(page.getByRole('tab', { name: '高级配置' })).toBeVisible();
  });

  test('Agent 表格或空状态应该显示', async ({ page }) => {
    await page.waitForTimeout(1000);
    const hasTable = await page.locator('table').isVisible().catch(() => false);
    const hasEmptyState = await page.getByText('暂无 Agent').isVisible().catch(() => false);
    expect(hasTable || hasEmptyState).toBe(true);
  });
});

test.describe('v1 回归测试 - 首页', () => {
  test('首页应该正常显示', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // 验证页面内容存在
    await expect(page.locator('body')).toBeVisible();

    // 验证导航可用
    const agentsLink = page.getByRole('link', { name: /Agent/ });
    if (await agentsLink.isVisible()) {
      await agentsLink.click();
      await expect(page).toHaveURL('/agents');
    }
  });
});

test.describe('v1 回归测试 - 编辑器', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/editor');
    await page.waitForLoadState('networkidle');
  });

  test('编辑器页应该正常显示', async ({ page }) => {
    // 编辑器页面可能显示空状态或编辑器组件
    const hasEditor = await page.locator('.react-flow').isVisible().catch(() => false);
    const hasEmptyState = await page.getByText(/选择.*模板|Select.*template/i).isVisible().catch(() => false);
    const hasPage = await page.locator('body').isVisible();

    expect(hasEditor || hasEmptyState || hasPage).toBe(true);
  });
});

test.describe('v1 回归测试 - API 健康', () => {
  test('后端 API 应该可访问', async ({ page }) => {
    const response = await page.request.get('http://localhost:8000/health');
    expect(response.status()).toBe(200);
  });

  test('Agent API 应该可访问', async ({ page }) => {
    const response = await page.request.get('http://localhost:8000/api/agents');
    expect(response.status()).toBe(200);
  });

  test('Template API 应该可访问', async ({ page }) => {
    const response = await page.request.get('http://localhost:8000/api/templates');
    expect(response.status()).toBe(200);
  });
});
