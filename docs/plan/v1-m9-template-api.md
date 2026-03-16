# v1-m9: Template REST API

## Goal

实现模板管理的 REST API 端点，提供 CRUD 接口。

## PRD Trace

- REQ-0001-016: REST API - 模板管理

## Scope

**做**：
- GET /api/templates - 模板列表（分页）
- POST /api/templates - 创建模板
- GET /api/templates/{id} - 模板详情
- POST /api/templates/upload - 上传 YAML
- DELETE /api/templates/{id} - 删除模板
- 单元测试

**不做**：
- 模板版本管理
- 模板权限控制
- 数据库持久化（使用内存存储）

## Acceptance

| # | 验收标准 | 验证命令 |
|---|----------|----------|
| 1 | GET /api/templates 返回分页列表 | `pytest tests/unit/test_template_api.py::test_list_templates -v` |
| 2 | POST /api/templates 创建模板 | `pytest tests/unit/test_template_api.py::test_create_template -v` |
| 3 | GET /api/templates/{id} 返回详情 | `pytest tests/unit/test_template_api.py::test_get_template -v` |
| 4 | POST /api/templates/upload 上传 YAML | `pytest tests/unit/test_template_api.py::test_upload_yaml -v` |
| 5 | DELETE /api/templates/{id} 删除模板 | `pytest tests/unit/test_template_api.py::test_delete_template -v` |

## Files

```
backend/
├── app/api/
│   └── templates.py
├── app/services/
│   └── template_service.py
└── tests/
    └── unit/
        └── test_template_api.py
```

## Steps

### Step 1: 写测试 (TDD Red)
### Step 2: 实现 Service 和 API (TDD Green)
### Step 3: 代码质量检查

## Risks

| 风险 | 缓解措施 |
|------|----------|
| YAML 解析失败 | 使用 TemplateParser 验证 |

## DoD 自检

- [x] 每条验收标准可二元判定
- [x] 每条验收绑定验证命令
- [x] Scope 明确不做什么
- [x] 测试覆盖正常/异常/边界场景
