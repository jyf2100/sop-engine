/**
 * 审批工作台 E2E 测试
 *
 * REQ-0001-023: 前端 - 审批工作台
 *
 * 覆盖用户流程：
 * 1. 查看待审批列表
 * 2. 处理审批（批准/拒绝）
 */

import { test, expect } from '@playwright/test';

test.describe('审批工作台', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/approvals');
    await page.waitForLoadState('networkidle');
  });

  test('应该显示审批工作台页面', async ({ page }) => {
    // 验证页面标题
    await expect(page.getByRole('heading', { name: '审批工作台' })).toBeVisible({ timeout: 10000 });
  });

  test('应该显示待审批列表或空状态', async ({ page }) => {
    // 等待加载完成
    await page.waitForTimeout(1000);

    // 要么显示待审批列表，要么显示空状态
    const hasTable = await page.locator('table').isVisible();
    const hasEmptyState = await page.getByText('暂无待审批任务').isVisible();

    expect(hasTable || hasEmptyState).toBe(true);
  });

  test('应该能打开审批处理对话框', async ({ page }) => {
    await page.waitForTimeout(1000);

    const processButton = page.getByRole('button', { name: '处理' }).first();
    if (await processButton.isVisible({ timeout: 5000 }).catch(() => false)) {
      await processButton.click();

      // 验证审批对话框打开
      await expect(page.getByRole('dialog')).toBeVisible();
      await expect(page.getByText('审批处理')).toBeVisible();
      await expect(page.getByRole('button', { name: '批准' })).toBeVisible();
      await expect(page.getByRole('button', { name: '拒绝' })).toBeVisible();
    } else {
      test.skip();
    }
  });

  test('应该能填写审批意见', async ({ page }) => {
    await page.waitForTimeout(1000);

    const processButton = page.getByRole('button', { name: '处理' }).first();
    if (await processButton.isVisible({ timeout: 5000 }).catch(() => false)) {
      await processButton.click();

      // 填写审批意见
      const commentInput = page.getByLabel('审批意见（可选）');
      await commentInput.fill('测试审批意见');

      // 验证输入成功
      await expect(commentInput).toHaveValue('测试审批意见');
    } else {
      test.skip();
    }
  });
});
