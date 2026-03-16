/**
 * 流程编辑器 E2E 测试
 *
 * REQ-0001-024: 前端 - 流程编辑器
 *
 * 覆盖用户流程：
 * 1. 查看流程画布
 * 2. 添加节点
 * 3. 导出 YAML
 */

import { test, expect } from '@playwright/test';

test.describe('流程编辑器', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/editor');
    await page.waitForLoadState('networkidle');
  });

  test('应该显示流程编辑器页面', async ({ page }) => {
    // 验证页面标题
    await expect(page.getByRole('heading', { name: '流程画布' })).toBeVisible({ timeout: 10000 });

    // 验证节点类型面板存在
    await expect(page.getByRole('heading', { name: '节点类型' })).toBeVisible();
  });

  test('应该显示所有节点类型按钮', async ({ page }) => {
    // 验证所有节点类型按钮存在
    const expectedTypes = ['开始', '结束', 'Agent', '脚本', '条件', '并行', '循环', '审批'];

    for (const type of expectedTypes) {
      await expect(page.getByRole('button', { name: type, exact: true })).toBeVisible();
    }
  });

  test('应该能添加节点到画布', async ({ page }) => {
    // 添加开始节点
    await page.getByRole('button', { name: '开始', exact: true }).click();

    // 验证节点出现在画布上
    await expect(page.locator('div.absolute').filter({ hasText: /^开始/ }).first()).toBeVisible({ timeout: 5000 });
  });

  test('应该能添加多个节点', async ({ page }) => {
    // 添加开始和结束节点
    await page.getByRole('button', { name: '开始', exact: true }).click();
    await page.getByRole('button', { name: '结束', exact: true }).click();

    // 验证两个节点都出现
    await expect(page.locator('div.absolute').filter({ hasText: /^开始/ }).first()).toBeVisible();
    await expect(page.locator('div.absolute').filter({ hasText: /^结束/ }).first()).toBeVisible();
  });

  test('应该显示导出 YAML 按钮', async ({ page }) => {
    const exportButton = page.getByRole('button', { name: '导出 YAML' });
    await expect(exportButton).toBeVisible();

    // 初始状态应该是禁用的
    await expect(exportButton).toBeDisabled();
  });

  test('添加节点后导出按钮应该可用', async ({ page }) => {
    // 添加节点
    await page.getByRole('button', { name: '开始', exact: true }).click();
    await page.getByRole('button', { name: '结束', exact: true }).click();

    // 等待节点出现
    await page.waitForTimeout(500);

    // 导出按钮应该可用
    const exportButton = page.getByRole('button', { name: '导出 YAML' });
    await expect(exportButton).toBeEnabled({ timeout: 5000 });
  });

  test('应该能选择节点查看详情', async ({ page }) => {
    // 添加节点
    await page.getByRole('button', { name: 'Agent', exact: true }).click();

    // 等待节点出现
    await page.waitForTimeout(500);

    // 点击画布上的节点
    const canvasNode = page.locator('div.absolute.w-\\[120px\\]').filter({ hasText: /Agent/ }).first();
    await canvasNode.click();

    // 验证节点详情对话框打开
    await expect(page.getByRole('dialog')).toBeVisible({ timeout: 5000 });
  });

  test('应该能删除节点', async ({ page }) => {
    // 添加节点
    await page.getByRole('button', { name: 'Agent', exact: true }).click();

    // 等待节点出现
    await page.waitForTimeout(500);

    // 点击画布上的节点
    const canvasNode = page.locator('div.absolute.w-\\[120px\\]').filter({ hasText: /Agent/ }).first();
    await canvasNode.click();

    // 点击删除
    await expect(page.getByRole('dialog')).toBeVisible({ timeout: 5000 });
    await page.getByRole('dialog').getByRole('button', { name: '删除' }).click();

    // 验证节点已删除
    await expect(page.locator('div.absolute.w-\\[120px\\]').filter({ hasText: /Agent/ })).not.toBeVisible({ timeout: 5000 });
  });
});
