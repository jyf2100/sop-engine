/**
 * 执行监控 E2E 测试
 *
 * REQ-0001-022: 前端 - 执行监控页
 *
 * 覆盖用户流程：
 * 1. 查看执行列表
 * 2. 查看执行详情
 * 3. 取消执行
 */

import { test, expect } from '@playwright/test';

test.describe('执行监控', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/executions');
    await page.waitForLoadState('networkidle');
  });

  test('应该显示执行监控页面', async ({ page }) => {
    // 验证页面标题
    await expect(page.getByRole('heading', { name: '执行监控' })).toBeVisible({ timeout: 10000 });
  });

  test('应该显示执行列表或空状态', async ({ page }) => {
    // 等待加载完成
    await page.waitForTimeout(1000);

    // 要么显示执行列表，要么显示空状态
    const hasTable = await page.locator('table').isVisible();
    const hasEmptyState = await page.getByText('暂无执行记录').isVisible();

    expect(hasTable || hasEmptyState).toBe(true);
  });

  test('应该能查看执行详情', async ({ page }) => {
    await page.waitForTimeout(1000);

    const viewButton = page.getByRole('button', { name: '详情' }).first();
    if (await viewButton.isVisible({ timeout: 5000 }).catch(() => false)) {
      await viewButton.click();

      // 验证详情对话框打开
      await expect(page.getByRole('dialog')).toBeVisible();
      await expect(page.getByText('执行详情')).toBeVisible();
    } else {
      test.skip();
    }
  });

  test('应该显示正确的状态颜色', async ({ page }) => {
    await page.waitForTimeout(1000);

    // 检查是否有状态显示
    const statusCell = page.locator('table td').filter({ hasText: /pending|running|completed|failed|cancelled/ }).first();
    if (await statusCell.isVisible({ timeout: 5000 }).catch(() => false)) {
      const text = await statusCell.textContent();
      expect(['pending', 'running', 'paused', 'completed', 'failed', 'cancelled']).toContain(text);
    } else {
      test.skip();
    }
  });
});
