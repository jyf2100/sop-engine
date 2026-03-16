/**
 * Agent 管理 E2E 测试
 *
 * REQ-0001-025: 前端 - Agent 管理页
 *
 * 覆盖用户流程：
 * 1. 查看 Agent 列表
 * 2. 打开创建 Agent 对话框
 */

import { test, expect } from '@playwright/test';

test.describe('Agent 管理', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/agents');
    await page.waitForLoadState('networkidle');
  });

  test('应该显示 Agent 管理页面', async ({ page }) => {
    // 验证页面标题
    await expect(page.getByRole('heading', { name: 'Agent 管理' })).toBeVisible({ timeout: 10000 });

    // 验证创建按钮存在
    await expect(page.getByRole('button', { name: '创建 Agent' })).toBeVisible();
  });

  test('应该能打开创建 Agent 对话框', async ({ page }) => {
    // 点击创建按钮
    await page.getByRole('button', { name: '创建 Agent' }).click();

    // 验证对话框打开
    await expect(page.getByRole('dialog')).toBeVisible();
    await expect(page.getByLabel('名称')).toBeVisible();
    await expect(page.getByLabel('工作目录')).toBeVisible();
    await expect(page.getByRole('button', { name: '创建' })).toBeVisible();
  });

  test('创建对话框应该能填写表单', async ({ page }) => {
    // 打开创建对话框
    await page.getByRole('button', { name: '创建 Agent' }).click();

    // 填写表单
    await page.getByLabel('名称').fill('测试 Agent');
    await page.getByLabel('工作目录').fill('/tmp/test-workspace');

    // 验证输入成功
    await expect(page.getByLabel('名称')).toHaveValue('测试 Agent');
    await expect(page.getByLabel('工作目录')).toHaveValue('/tmp/test-workspace');
  });

  test('应该显示表格或空状态', async ({ page }) => {
    await page.waitForTimeout(1000);

    // 要么显示表格，要么显示空状态
    const hasTable = await page.locator('table').isVisible().catch(() => false);
    const hasEmptyState = await page.getByText('暂无 Agent').isVisible().catch(() => false);

    expect(hasTable || hasEmptyState).toBe(true);
  });
});
