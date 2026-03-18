/**
 * Agent 管理 E2E 测试
 *
 * REQ-0001-025: 前端 - Agent 管理页
 *
 * 覆盖用户流程：
 * 1. 查看 Agent 列表
 * 2. 打开创建 Agent 对话框
 * 3. 填写新表单
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

    // 验证表单标签页存在
    await expect(page.getByRole('tab', { name: '基本信息' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'LLM 配置' })).toBeVisible();
    await expect(page.getByRole('tab', { name: '沙箱配置' })).toBeVisible();
    await expect(page.getByRole('tab', { name: '工具配置' })).toBeVisible();
    await expect(page.getByRole('tab', { name: '高级配置' })).toBeVisible();

    // 验证基本信息表单字段
    await expect(page.getByLabel('名称')).toBeVisible();
    await expect(page.getByRole('button', { name: '创建' })).toBeVisible();
  });

  test('创建对话框应该能填写表单', async ({ page }) => {
    // 打开创建对话框
    await page.getByRole('button', { name: '创建 Agent' }).click();

    // 填写基本信息
    await page.getByLabel('名称').fill('测试 Agent');

    // 验证输入成功
    await expect(page.getByLabel('名称')).toHaveValue('测试 Agent');

    // 切换到 LLM 配置标签页
    await page.getByRole('tab', { name: 'LLM 配置' }).click();

    // 验证 LLM 配置表单字段存在 - 现在是模型选择
    await expect(page.getByText('选择模型')).toBeVisible();
  });

  test('应该显示表格或空状态', async ({ page }) => {
    await page.waitForTimeout(1000);

    // 要么显示表格，要么显示空状态
    const hasTable = await page.locator('table').isVisible().catch(() => false);
    const hasEmptyState = await page.getByText('暂无 Agent').isVisible().catch(() => false);

    expect(hasTable || hasEmptyState).toBe(true);
  });
});
