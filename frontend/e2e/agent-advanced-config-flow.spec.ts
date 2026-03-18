/**
 * Agent 高级配置流程 E2E 测试
 *
 * REQ-0001-027: Agent 配置对齐
 * REQ-0001-029: 前端适配 - 高级配置
 *
 * 覆盖用户流程：
 * 1. 创建 Agent 时配置 Session 设置
 * 2. 编辑 Agent 时修改高级配置
 * 3. 验证 Session 配置保存
 */

import { test, expect } from '@playwright/test';

test.describe('Agent 高级配置流程', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/agents');
    await page.waitForLoadState('networkidle');
  });

  test('应该显示高级配置标签页', async ({ page }) => {
    // 打开创建对话框
    await page.getByRole('button', { name: '创建 Agent' }).click();
    await expect(page.getByRole('dialog')).toBeVisible();

    // 切换到高级配置
    await page.getByRole('tab', { name: '高级配置' }).click();

    // 验证心跳配置存在
    await expect(page.getByText('心跳配置')).toBeVisible();
  });

  test('应该能展开 Session 配置面板', async ({ page }) => {
    // 打开创建对话框
    await page.getByRole('button', { name: '创建 Agent' }).click();
    await expect(page.getByRole('dialog')).toBeVisible();

    // 切换到高级配置
    await page.getByRole('tab', { name: '高级配置' }).click();

    // 点击 Session 配置折叠面板
    await page.getByRole('button', { name: /Session 配置/ }).click();

    // 验证 Session 配置内容显示
    await expect(page.getByText('DM Scope')).toBeVisible();
    await expect(page.getByText('会话重置')).toBeVisible();
  });

  test('应该能配置 DM Scope', async ({ page }) => {
    // 打开创建对话框
    await page.getByRole('button', { name: '创建 Agent' }).click();
    await expect(page.getByRole('dialog')).toBeVisible();

    // 切换到高级配置并展开 Session
    await page.getByRole('tab', { name: '高级配置' }).click();
    await page.getByRole('button', { name: /Session 配置/ }).click();

    // 等待 Session 配置面板展开
    await expect(page.getByText('DM Scope')).toBeVisible();

    // 选择 DM Scope
    const dmScopeSelect = page.locator('text=DM Scope').locator('..').locator('button[type="button"]').first();
    await dmScopeSelect.click();

    // 选择 per-peer
    await page.getByRole('option', { name: 'Per-Peer' }).click();
  });

  test('应该能配置会话重置策略', async ({ page }) => {
    // 打开创建对话框
    await page.getByRole('button', { name: '创建 Agent' }).click();
    await expect(page.getByRole('dialog')).toBeVisible();

    // 切换到高级配置并展开 Session
    await page.getByRole('tab', { name: '高级配置' }).click();
    await page.getByRole('button', { name: /Session 配置/ }).click();

    // 等待配置面板展开
    await expect(page.getByText('会话重置')).toBeVisible();

    // 点击会话重置卡片
    await page.getByRole('button', { name: /会话重置/ }).click();

    // 选择重置模式
    const resetModeSelect = page.locator('text=重置模式').locator('..').locator('button[type="button"]').first();
    await resetModeSelect.click();
    await page.getByRole('option', { name: '每日重置' }).click();
  });

  test('应该能配置线程绑定', async ({ page }) => {
    // 打开创建对话框
    await page.getByRole('button', { name: '创建 Agent' }).click();
    await expect(page.getByRole('dialog')).toBeVisible();

    // 切换到高级配置并展开 Session
    await page.getByRole('tab', { name: '高级配置' }).click();
    await page.getByRole('button', { name: /Session 配置/ }).click();

    // 等待配置面板展开
    await expect(page.getByText('线程绑定')).toBeVisible();

    // 点击线程绑定卡片
    await page.getByRole('button', { name: /线程绑定/ }).click();

    // 验证启用线程绑定开关存在
    await expect(page.getByText('启用线程绑定')).toBeVisible();
  });

  test('完整创建 Agent 并配置 Session', async ({ page }) => {
    const agentName = 'E2E Session Agent ' + Date.now();

    // 打开创建对话框
    await page.getByRole('button', { name: '创建 Agent' }).click();
    await expect(page.getByRole('dialog')).toBeVisible();

    // 填写基本信息
    await page.getByLabel('名称').fill(agentName);

    // 切换到高级配置
    await page.getByRole('tab', { name: '高级配置' }).click();

    // 展开 Session 配置
    await page.getByRole('button', { name: /Session 配置/ }).click();
    await expect(page.getByText('DM Scope')).toBeVisible();

    // 配置 DM Scope
    const dmScopeSelect = page.locator('text=DM Scope').locator('..').locator('button[type="button"]').first();
    await dmScopeSelect.click();
    await page.getByRole('option', { name: 'Per-Peer' }).click();

    // 提交创建
    await page.getByRole('tab', { name: '基本信息' }).click();
    await page.getByRole('button', { name: '创建' }).click();

    // 验证创建成功
    await expect(page.locator('.bg-green-500')).toBeVisible({ timeout: 10000 });
  });

  test('编辑 Agent 时应该能修改高级配置', async ({ page }) => {
    // 等待 Agent 列表加载
    await page.waitForTimeout(1000);

    // 检查是否有 Agent 可以编辑
    const hasAgent = await page.locator('table tbody tr').first().isVisible().catch(() => false);

    if (hasAgent) {
      // 点击第一个 Agent 的编辑按钮
      await page.locator('table tbody tr').first().getByRole('button', { name: /编辑/ }).click();

      // 等待编辑对话框
      await expect(page.getByRole('dialog')).toBeVisible();

      // 切换到高级配置
      await page.getByRole('tab', { name: '高级配置' }).click();

      // 验证高级配置可编辑
      await expect(page.getByText('心跳配置')).toBeVisible();
    } else {
      // 没有 Agent 时跳过测试
      test.skip();
    }
  });

  test('应该能查看配置预览', async ({ page }) => {
    // 打开创建对话框
    await page.getByRole('button', { name: '创建 Agent' }).click();
    await expect(page.getByRole('dialog')).toBeVisible();

    // 切换到高级配置
    await page.getByRole('tab', { name: '高级配置' }).click();

    // 滚动到底部找到配置预览
    const configPreview = page.getByText('配置预览');
    await configPreview.scrollIntoViewIfNeeded();

    // 验证配置预览存在
    await expect(configPreview).toBeVisible();
  });
});
