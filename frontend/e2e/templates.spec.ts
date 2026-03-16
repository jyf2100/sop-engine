/**
 * 模板管理 E2E 测试
 *
 * REQ-0001-021: 前端 - 模板列表页
 *
 * 覆盖用户流程：
 * 1. 查看模板列表
 * 2. 打开创建模板对话框
 */

import { test, expect } from '@playwright/test';

test.describe('模板管理', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/templates');
    await page.waitForLoadState('networkidle');
  });

  test('应该显示模板列表页面', async ({ page }) => {
    // 验证页面标题
    await expect(page.getByRole('heading', { name: '流程模板' })).toBeVisible({ timeout: 10000 });

    // 验证创建按钮存在
    await expect(page.getByRole('button', { name: '创建模板' })).toBeVisible();
  });

  test('应该能打开创建模板对话框', async ({ page }) => {
    // 点击创建按钮
    await page.getByRole('button', { name: '创建模板' }).click();

    // 验证对话框打开
    await expect(page.getByRole('dialog')).toBeVisible();
    await expect(page.getByLabel('名称')).toBeVisible();
    await expect(page.getByLabel('版本')).toBeVisible();
    await expect(page.getByRole('button', { name: '创建' })).toBeVisible();
  });

  test('创建对话框应该能填写表单', async ({ page }) => {
    // 打开创建对话框
    await page.getByRole('button', { name: '创建模板' }).click();

    // 填写表单
    await page.getByLabel('名称').fill('测试模板');
    await page.getByLabel('版本').fill('1.0.0');
    await page.locator('#yaml').fill('name: test\nversion: "1.0"');

    // 验证输入成功
    await expect(page.getByLabel('名称')).toHaveValue('测试模板');
    await expect(page.getByLabel('版本')).toHaveValue('1.0.0');
  });

  test('应该显示表格或空状态', async ({ page }) => {
    await page.waitForTimeout(1000);

    // 要么显示表格，要么显示空状态
    const hasTable = await page.locator('table').isVisible().catch(() => false);
    const hasEmptyState = await page.getByText('暂无模板').isVisible().catch(() => false);

    expect(hasTable || hasEmptyState).toBe(true);
  });
});
