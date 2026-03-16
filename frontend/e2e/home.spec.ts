/**
 * 首页导航 E2E 测试
 *
 * 覆盖用户流程：
 * 1. 导航栏显示正确
 * 2. 导航到各个页面
 * 3. 首页卡片显示
 */

import { test, expect } from '@playwright/test';

test.describe('首页和导航', () => {
  test('应该显示导航栏', async ({ page }) => {
    await page.goto('/');

    // 验证品牌名称
    await expect(page.getByRole('link', { name: 'SOP Engine' })).toBeVisible();

    // 验证导航链接 (使用 exact: true 避免匹配首页卡片)
    await expect(page.getByRole('link', { name: '首页', exact: true })).toBeVisible();
    await expect(page.getByRole('link', { name: '模板', exact: true })).toBeVisible();
    await expect(page.getByRole('link', { name: '执行', exact: true })).toBeVisible();
    await expect(page.getByRole('link', { name: '审批', exact: true })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Agent', exact: true })).toBeVisible();
    await expect(page.getByRole('link', { name: '编辑器', exact: true })).toBeVisible();
  });

  test('应该能导航到模板页', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('link', { name: '模板', exact: true }).click();

    await expect(page).toHaveURL('/templates');
    await expect(page.getByRole('heading', { name: '流程模板' })).toBeVisible({ timeout: 10000 });
  });

  test('应该能导航到执行页', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('link', { name: '执行', exact: true }).click();

    await expect(page).toHaveURL('/executions');
    await expect(page.getByRole('heading', { name: '执行监控' })).toBeVisible({ timeout: 10000 });
  });

  test('应该能导航到审批页', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('link', { name: '审批', exact: true }).click();

    await expect(page).toHaveURL('/approvals');
    await expect(page.getByRole('heading', { name: '审批工作台' })).toBeVisible({ timeout: 10000 });
  });

  test('应该能导航到 Agent 页', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('link', { name: 'Agent', exact: true }).click();

    await expect(page).toHaveURL('/agents');
    await expect(page.getByRole('heading', { name: 'Agent 管理' })).toBeVisible({ timeout: 10000 });
  });

  test('应该能导航到编辑器页', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('link', { name: '编辑器', exact: true }).click();

    await expect(page).toHaveURL('/editor');
    await expect(page.getByRole('heading', { name: '流程画布' })).toBeVisible({ timeout: 10000 });
  });

  test('首页应该显示标题', async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // 验证 SOP Engine 标题
    await expect(page.getByRole('heading', { name: 'SOP Engine', level: 1 })).toBeVisible({ timeout: 10000 });
  });

  test('当前页面导航链接应该高亮', async ({ page }) => {
    await page.goto('/templates');

    // 模板链接应该有高亮样式
    const templatesLink = page.getByRole('link', { name: '模板', exact: true });
    await expect(templatesLink).toHaveClass(/bg-/);
  });

  test('首页卡片可以点击导航', async ({ page }) => {
    await page.goto('/');

    // 点击首页的流程模板卡片
    await page.getByRole('link', { name: /^流程模板/ }).click();
    await expect(page).toHaveURL('/templates');
    await expect(page.getByRole('heading', { name: '流程模板' })).toBeVisible();
  });
});
