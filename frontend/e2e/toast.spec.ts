import { test, expect } from '@playwright/test';

test.describe('Toast 通知功能', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('上传无效 YAML 应该显示错误 toast', async ({ page }) => {
    await page.goto('/templates');

    // 等待页面加载
    await expect(page.getByRole('heading', { name: '流程模板' })).toBeVisible();

    // 创建一个无效的 YAML 文件
    const invalidYamlContent = 'invalid: yaml: content: [unclosed';

    // 监听文件选择
    const fileInput = page.locator('input[type="file"]');

    // 上传无效文件
    await fileInput.setInputFiles({
      name: 'invalid.yaml',
      mimeType: 'application/x-yaml',
      buffer: Buffer.from(invalidYamlContent)
    });

    // 等待 toast 出现 - 红色错误提示
    const toast = page.locator('.bg-red-500');
    await expect(toast).toBeVisible({ timeout: 5000 });

    // 验证错误消息
    await expect(toast).toContainText('上传失败');

    console.log('✅ 错误 toast 显示成功');
  });

  test('上传超大文件应该显示错误 toast', async ({ page }) => {
    await page.goto('/templates');

    await expect(page.getByRole('heading', { name: '流程模板' })).toBeVisible();

    // 创建一个超过 1MB 的文件
    const largeContent = 'x: ' + 'a'.repeat(2 * 1024 * 1024); // 2MB+
    const fileInput = page.locator('input[type="file"]');

    await fileInput.setInputFiles({
      name: 'large.yaml',
      mimeType: 'application/x-yaml',
      buffer: Buffer.from(largeContent)
    });

    // 等待 toast 出现
    const toast = page.locator('.bg-red-500');
    await expect(toast).toBeVisible({ timeout: 5000 });
    await expect(toast).toContainText('文件大小不能超过');

    console.log('✅ 文件大小限制 toast 显示成功');
  });

  test('toast 应该能手动关闭', async ({ page }) => {
    await page.goto('/templates');

    await expect(page.getByRole('heading', { name: '流程模板' })).toBeVisible();

    // 触发一个错误
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles({
      name: 'invalid.yaml',
      mimeType: 'application/x-yaml',
      buffer: Buffer.from('invalid:::yaml')
    });

    // 等待 toast 出现
    const toast = page.locator('.bg-red-500');
    await expect(toast).toBeVisible({ timeout: 5000 });

    // 点击关闭按钮
    const closeButton = toast.locator('button');
    await closeButton.click();

    // 验证 toast 消失
    await expect(toast).not.toBeVisible({ timeout: 2000 });

    console.log('✅ Toast 手动关闭成功');
  });
});
