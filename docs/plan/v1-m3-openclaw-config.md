# v1-m3: OpenClaw 配置管理

## Goal

实现 OpenClaw 主配置和凭证的统一管理，SOP Engine 作为 OpenClaw 配置的唯一来源。

## PRD Trace

- REQ-0001-004: OpenClaw 主配置管理
- REQ-0001-005: OpenClaw 凭证管理

## Scope

**做**：
- OpenClawConfigService: openclaw.json CRUD
- CredentialService: 凭证加密存储和同步
- 配置验证（符合 OpenClaw schema）
- 凭证脱敏（API 响应、日志）
- 与 Agent 配置联动的自动更新
- 单元测试 + 集成测试

**不做**：
- REST API 端点（M7-M11）
- 前端页面（M12-M17）
- 实际调用 OpenClaw webhook

## Acceptance

| # | 验收标准 | 验证命令 |
|---|----------|----------|
| 1 | 读取 openclaw.json 并解析为结构化对象 | `pytest tests/unit/test_openclaw_config.py::test_load_config -v` |
| 2 | 更新配置后写入文件 | `pytest tests/unit/test_openclaw_config.py::test_update_config -v` |
| 3 | 配置验证失败时拒绝更新 | `pytest tests/unit/test_openclaw_config.py::test_validate_config_fails -v` |
| 4 | 凭证 AES-256 加密存储 | `pytest tests/unit/test_credential_service.py::test_encrypt_credential -v` |
| 5 | 凭证同步到 OpenClaw | `pytest tests/integration/test_credential_sync.py::test_sync_credentials -v` |
| 6 | API 响应中凭证值脱敏 | `pytest tests/unit/test_credential_service.py::test_mask_credential -v` |

## Files

```
backend/
├── app/
│   ├── services/
│   │   ├── openclaw_config_service.py   # openclaw.json 管理
│   │   └── credential_service.py        # 凭证管理
│   ├── models/
│   │   ├── openclaw_config.py           # openclaw.json 结构
│   │   └── credential.py                # 凭证模型
│   └── utils/
│       └── crypto.py                     # 加密工具
└── tests/
    ├── unit/
    │   ├── test_openclaw_config.py
    │   ├── test_credential_service.py
    │   └── test_crypto.py
    └── integration/
        └── test_credential_sync.py
```

## Steps

### Step 1: 创建加密工具 (TDD Red → Green)
### Step 2: 创建 OpenClawConfig 模型
### Step 3: 实现 OpenClawConfigService (TDD)
### Step 4: 创建 Credential 模型
### Step 5: 实现 CredentialService (TDD)
### Step 6: 集成测试
### Step 7: 代码质量检查

## Risks

| 风险 | 缓解措施 |
|------|----------|
| 加密密钥丢失导致数据无法恢复 | 密钥备份机制、密钥轮换支持 |
| 并发写入 openclaw.json | 文件锁或原子写入 |
| 凭证泄露 | 脱敏、审计日志、密钥轮换 |

## DoD 自检

- [x] 每条验收标准可二元判定
- [x] 每条验收绑定验证命令
- [x] Scope 明确不做什么
- [x] 测试覆盖正常/异常/边界场景
