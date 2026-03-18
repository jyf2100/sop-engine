import { test, expect } from '@playwright/test';

test('完整创建 Agent 流程', async ({ page }) => {
  await page.goto('/agents');

  // 点击创建按钮
  await page.getByRole('button', { name: '创建 Agent' }).click();

  // 等待对话框打开
  await expect(page.getByRole('dialog')).toBeVisible();

  // 填写基本信息
  await page.getByLabel('名称').fill('E2E 测试 Agent ' + Date.now());

  // 验证各个标签页可以切换
  await page.getByRole('tab', { name: 'LLM 配置' }).click();
  await expect(page.getByText('选择模型')).toBeVisible();

  await page.getByRole('tab', { name: '沙箱配置' }).click();
  await expect(page.getByText('沙箱模式')).toBeVisible();

  await page.getByRole('tab', { name: '工具配置' }).click();
  await expect(page.getByText('配置文件')).toBeVisible();

  await page.getByRole('tab', { name: '高级配置' }).click();
  await expect(page.getByText('心跳配置')).toBeVisible();

  // 切回基本信息并提交
  await page.getByRole('tab', { name: '基本信息' }).click();
  await page.getByRole('button', { name: '创建' }).click();

  // 等待成功 toast
  await expect(page.locator('.bg-green-500')).toBeVisible({ timeout: 10000 });

  console.log('✅ 创建 Agent 流程完成');
});
