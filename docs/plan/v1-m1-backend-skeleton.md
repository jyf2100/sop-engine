# v1-m1: 后端骨架搭建

## Goal

建立可运行的后端项目结构，配置开发工具，定义数据库模型，为后续开发提供基础。

## PRD Trace

- REQ-0001-001: 项目骨架搭建
- REQ-0001-002: 数据库模型定义

## Scope

**做**：
- 创建 backend/ 目录结构
- 配置 pyproject.toml 依赖
- 配置 ruff, pyright
- 定义 Template, Execution, NodeExecution 模型
- 定义 Agent, AgentConfigFile 模型（支持 OpenClaw 配置管理）
- 配置 PostgreSQL 异步连接
- 创建 FastAPI 入口

**不做**：
- 不实现业务逻辑
- 不创建数据库迁移
- 不配置 Redis
- 不实现 API 端点

## Acceptance

| # | 验收标准 | 验证命令 |
|---|----------|----------|
| 1 | uvicorn 启动成功 | `cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000` → 访问 http://localhost:8000 返回 200 |
| 2 | ruff 检查通过 | `cd backend && ruff check .` → exit code 0 |
| 3 | pyright 检查通过 | `cd backend && pyright` → 0 errors |
| 4 | pytest 可运行 | `cd backend && pytest` → exit code 0 |
| 5 | 模型可导入 | `python -c "from app.models import Template, Execution, NodeExecution, Agent, AgentConfigFile"` → 无错误 |

## Files

```
backend/
├── pyproject.toml
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置加载
│   └── models/
│       ├── __init__.py
│       ├── base.py          # 基础模型类
│       ├── template.py      # Template 模型
│       ├── execution.py     # Execution 模型
│       ├── node_execution.py # NodeExecution 模型
│       ├── agent.py         # Agent 模型
│       └── agent_config_file.py # AgentConfigFile 模型
└── tests/
    ├── __init__.py
    └── unit/
        ├── __init__.py
        └── test_models.py
```

## Steps

### Step 1: 创建目录结构

**命令**：
```bash
mkdir -p backend/app/models backend/tests/unit
touch backend/app/__init__.py
touch backend/app/models/__init__.py
touch backend/tests/__init__.py
touch backend/tests/unit/__init__.py
```

**验证**：目录结构存在

### Step 2: 创建 pyproject.toml（红）

**测试**：
```python
# tests/unit/test_setup.py
def test_dependencies_installed():
    """验证依赖已安装"""
    import fastapi
    import sqlalchemy
    import pydantic
    import asyncpg
    assert fastapi is not None
    assert sqlalchemy is not None
```

**命令**：
```bash
cd backend && pytest tests/unit/test_setup.py -v
```

**预期**：FAIL - pyproject.toml 不存在，依赖未安装

### Step 3: 创建 pyproject.toml（绿）

**实现**：
```toml
# backend/pyproject.toml
[project]
name = "sop-engine-backend"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "sqlalchemy>=2.0.0",
    "asyncpg>=0.29.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.0.0",
    "pyyaml>=6.0",
    "redis>=5.0.0",
    "httpx>=0.26.0",
    "structlog>=24.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.23.0",
    "ruff>=0.2.0",
    "pyright>=1.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP", "B"]

[tool.pyright]
pythonVersion = "3.11"
typeCheckingMode = "strict"

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

**命令**：
```bash
cd backend && pip install -e ".[dev]"
```

**验证**：
```bash
cd backend && pytest tests/unit/test_setup.py -v
```

**预期**：PASS

### Step 4: 创建 config.py（红）

**测试**：
```python
# tests/unit/test_config.py
def test_config_has_database_url():
    """验证配置包含 DATABASE_URL"""
    from app.config import settings
    assert hasattr(settings, "database_url")
    assert settings.database_url is not None


def test_config_has_openclaw_settings():
    """验证配置包含 OpenClaw 设置"""
    from app.config import settings
    assert hasattr(settings, "openclaw_url")
    assert hasattr(settings, "openclaw_token")
    assert hasattr(settings, "openclaw_timeout")
    assert hasattr(settings, "openclaw_workspace_root")
```

**命令**：
```bash
cd backend && pytest tests/unit/test_config.py -v
```

**预期**：FAIL - config.py 不存在

### Step 5: 创建 config.py（绿）

**实现**：
```python
# backend/app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/sop_engine"
    redis_url: str = "redis://localhost:6379/0"

    # OpenClaw 配置
    openclaw_url: str = "http://localhost:18789"
    openclaw_token: str = ""
    openclaw_timeout: int = 30
    openclaw_workspace_root: str = "~/.openclaw"  # OpenClaw workspace 根目录


settings = Settings()
```

**验证**：
```bash
cd backend && pytest tests/unit/test_config.py -v
```

**预期**：PASS

### Step 6: 创建模型（红）

**测试**：
```python
# tests/unit/test_models.py
import pytest


def test_template_model_exists():
    """REQ-0001-002: Template 模型存在"""
    from app.models import Template
    assert Template is not None


def test_execution_model_exists():
    """REQ-0001-002: Execution 模型存在"""
    from app.models import Execution
    assert Execution is not None


def test_node_execution_model_exists():
    """REQ-0001-002: NodeExecution 模型存在"""
    from app.models import NodeExecution
    assert NodeExecution is not None


def test_template_fields():
    """REQ-0001-002: Template 模型字段"""
    from app.models import Template
    template = Template(
        id="test-flow",
        name="Test Flow",
        version="1.0.0",
        yaml_content="nodes: {}",
    )
    assert template.id == "test-flow"
    assert template.name == "Test Flow"
    assert template.version == "1.0.0"
    assert template.yaml_content == "nodes: {}"


def test_execution_fields():
    """REQ-0001-002: Execution 模型字段"""
    from app.models import Execution
    import uuid
    exec_id = str(uuid.uuid4())
    execution = Execution(
        id=exec_id,
        template_id="test-flow",
        status="pending",
        params={"key": "value"},
    )
    assert execution.id == exec_id
    assert execution.template_id == "test-flow"
    assert execution.status == "pending"
    assert execution.params == {"key": "value"}


def test_agent_model_exists():
    """REQ-0001-002: Agent 模型存在"""
    from app.models import Agent
    assert Agent is not None


def test_agent_config_file_model_exists():
    """REQ-0001-002: AgentConfigFile 模型存在"""
    from app.models import AgentConfigFile
    assert AgentConfigFile is not None


def test_agent_fields():
    """REQ-0001-002: Agent 模型字段"""
    from app.models import Agent
    agent = Agent(
        id="security-scanner",
        name="Security Scanner",
        workspace_path="/workspace/security-scanner",
        model_config={"primary": "claude-3-5-sonnet"},
        sandbox_config={"mode": "non-main"},
        tools_config={"allow": ["read", "write"]},
    )
    assert agent.id == "security-scanner"
    assert agent.name == "Security Scanner"
    assert agent.workspace_path == "/workspace/security-scanner"


def test_agent_config_file_fields():
    """REQ-0001-002: AgentConfigFile 模型字段"""
    from app.models import AgentConfigFile
    config_file = AgentConfigFile(
        id="cfg-001",
        agent_id="security-scanner",
        file_type="AGENTS.md",
        content="# Agent Instructions\n...",
    )
    assert config_file.id == "cfg-001"
    assert config_file.agent_id == "security-scanner"
    assert config_file.file_type == "AGENTS.md"
```

**命令**：
```bash
cd backend && pytest tests/unit/test_models.py -v
```

**预期**：FAIL - 模型不存在

### Step 7: 创建模型（绿）

**实现**：

```python
# backend/app/models/base.py
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class Base(BaseModel):
    """所有模型的基类"""
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
```

```python
# backend/app/models/template.py
from datetime import datetime

from pydantic import BaseModel

from .base import Base


class Template(Base):
    """流程模板模型"""
    id: str
    name: str
    version: str
    yaml_content: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
```

```python
# backend/app/models/execution.py
from datetime import datetime
from typing import Any

from .base import Base


class Execution(Base):
    """执行实例模型"""
    id: str
    template_id: str
    status: str = "pending"
    params: dict[str, Any]
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime | None = None
```

```python
# backend/app/models/node_execution.py
from datetime import datetime
from typing import Any

from .base import Base


class NodeExecution(Base):
    """节点执行记录模型"""
    id: str
    execution_id: str
    node_id: str
    status: str = "pending"
    input: dict[str, Any] | None = None
    output: dict[str, Any] | None = None
    error: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
```

```python
# backend/app/models/agent.py
from datetime import datetime
from typing import Any

from .base import Base


class Agent(Base):
    """Agent 配置模型 - 对应 OpenClaw agents.list[]"""
    id: str
    name: str
    workspace_path: str
    model_config: dict[str, Any]  # primary, fallbacks
    sandbox_config: dict[str, Any]  # mode, workspaceAccess, scope, docker
    tools_config: dict[str, Any]  # profile, allow, deny, exec
    heartbeat_config: dict[str, Any] | None = None  # every, target
    memory_search_config: dict[str, Any] | None = None  # enabled, provider, model
    group_chat_config: dict[str, Any] | None = None  # mentionPatterns
    is_default: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
```

```python
# backend/app/models/agent_config_file.py
from datetime import datetime

from .base import Base


class AgentConfigFile(Base):
    """Agent 配置文件模型 - AGENTS.md, SOUL.md, USER.md 等"""
    id: str
    agent_id: str
    file_type: str  # AGENTS.md, SOUL.md, USER.md, IDENTITY.md, TOOLS.md, etc.
    content: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
```

```python
# backend/app/models/__init__.py
from .agent import Agent
from .agent_config_file import AgentConfigFile
from .base import Base
from .execution import Execution
from .node_execution import NodeExecution
from .template import Template

__all__ = ["Base", "Template", "Execution", "NodeExecution", "Agent", "AgentConfigFile"]
```

**验证**：
```bash
cd backend && pytest tests/unit/test_models.py -v
```

**预期**：PASS

### Step 8: 创建 FastAPI 入口（红）

**测试**：
```python
# tests/unit/test_main.py
import pytest
from fastapi.testclient import TestClient


def test_main_app_exists():
    """验证 FastAPI 应用存在"""
    from app.main import app
    assert app is not None


def test_health_check():
    """验证健康检查端点"""
    from app.main import app
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

**命令**：
```bash
cd backend && pytest tests/unit/test_main.py -v
```

**预期**：FAIL - main.py 不存在

### Step 9: 创建 FastAPI 入口（绿）

**实现**：
```python
# backend/app/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    yield
    # 关闭时清理


app = FastAPI(
    title="SOP Engine",
    description="SOP 编排引擎 API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok"}
```

**验证**：
```bash
cd backend && pytest tests/unit/test_main.py -v
```

**预期**：PASS

### Step 10: 代码质量检查

**命令**：
```bash
cd backend && ruff check . && ruff format . --check && pyright
```

**预期**：全部通过

### Step 11: 完整测试运行

**命令**：
```bash
cd backend && pytest --cov=app --cov-report=term-missing
```

**预期**：覆盖率 ≥ 90%

## Risks

| 风险 | 缓解措施 |
|------|----------|
| PostgreSQL 连接失败 | 使用环境变量配置，提供默认值 |
| 依赖版本冲突 | 锁定版本，使用 uv 锁文件 |

## DoD 自检

- [x] 每条验收标准可二元判定
- [x] 每条验收绑定验证命令
- [x] Scope 明确不做什么
- [x] 测试覆盖正常/异常场景
