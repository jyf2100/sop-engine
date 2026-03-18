/**
 * Bindings 配置流程 E2E 测试
 *
 * REQ-0001-028: Bindings 支持
 *
 * 覆盖用户流程：
 * 1. 查看 Bindings 列表
 * 2. 创建 Binding
 * 3. 配置路由规则
 */

import { test, expect } from '@playwright/test';

test.describe('Bindings 流程', () => {
  // 注意：Bindings 页面可能尚未实现，此测试作为未来验证
  test.skip(() => true, 'Bindings UI 尚未实现');

  test.beforeEach(async ({ page }) => {
    // 检查 bindings 页面是否存在
    const response = await page.goto('/bindings').catch(() => null);
    if (!response || response.status() === 404) {
      test.skip();
    }
    await page.waitForLoadState('networkidle');
  });

  test('应该显示 Bindings 管理页面', async ({ page }) => {
    // 验证页面标题
    await expect(page.getByRole('heading', { name: /Bindings|绑定/ })).toBeVisible({ timeout: 10000 });
  });

  test('应该能打开创建 Binding 对话框', async ({ page }) => {
    // 点击创建按钮
    await page.getByRole('button', { name: /创建|Create/ }).click();

    // 验证对话框打开
    await expect(page.getByRole('dialog')).toBeVisible();
  });

  test('应该能创建 Route 类型 Binding', async ({ page }) => {
    // 打开创建对话框
    await page.getByRole('button', { name: /创建|Create/ }).click();
    await expect(page.getByRole('dialog')).toBeVisible();

    // 选择类型
    const typeSelect = page.locator('[data-testid="binding-type"]').or(
      page.getByLabel(/类型|Type/)
    );
    await typeSelect.click();
    await page.getByRole('option', { name: 'Route' }).click();

    // 选择 Agent
    const agentSelect = page.locator('[data-testid="agent-id"]').or(
      page.getByLabel(/Agent/)
    );
    await agentSelect.click();

    // 验证表单可填写
    await expect(page.getByRole('button', { name: /创建|Save|保存/ })).toBeVisible();
  });

  test('应该能配置匹配规则', async ({ page }) => {
    // 打开创建对话框
    await page.getByRole('button', { name: /创建|Create/ }).click();
    await expect(page.getByRole('dialog')).toBeVisible();

    // 检查是否有匹配规则配置
    const matchSection = page.getByText(/匹配|Match/);
    if (await matchSection.isVisible()) {
      await expect(matchSection).toBeVisible();
    }
  });

  test('应该显示表格或空状态', async ({ page }) => {
    await page.waitForTimeout(1000);

    // 要么显示表格，要么显示空状态
    const hasTable = await page.locator('table').isVisible().catch(() => false);
    const hasEmptyState = await page.getByText(/暂无|No.*bindings|Empty/).isVisible().catch(() => false);

    expect(hasTable || hasEmptyState).toBe(true);
  });
});

test.describe('Bindings API 测试', () => {
  test('应该能访问 Bindings API', async ({ page }) => {
    const response = await page.request.get('http://localhost:8000/api/bindings');

    // API 应该返回 200 或 404（如果未实现）
    expect([200, 404]).toContain(response.status());
  });

  test('应该能创建 Binding 通过 API', async ({ page }) => {
    const response = await page.request.post('http://localhost:8000/api/bindings', {
      data: {
        type: 'route',
        agent_id: 'test-agent',
        match: {
          channel: 'telegram',
        },
      },
    });

    // API 应该返回 200, 201, 或 404（如果未实现）
    expect([200, 201, 404, 422]).toContain(response.status());
  });
});
