"""流程模板模型。

REQ-0001-006: YAML 模板解析器

定义流程模板的内部结构。
"""
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class NodeType(str, Enum):
    """节点类型"""

    START = "start"
    END = "end"
    AGENT = "agent"
    SCRIPT = "script"
    CONDITION = "condition"
    PARALLEL = "parallel"
    LOOP = "loop"
    HUMAN = "human"
    WAIT = "wait"


class FlowNode(BaseModel):
    """流程节点"""

    id: str = Field(..., description="节点唯一标识")
    type: NodeType = Field(..., description="节点类型")
    name: Optional[str] = Field(default=None, description="节点名称")
    next: Optional[str] = Field(default=None, description="下一个节点 ID")
    config: dict[str, Any] = Field(default_factory=dict, description="节点配置")

    # 条件节点特有
    branches: Optional[dict[str, str]] = Field(default=None, description="条件分支")

    # 并行节点特有
    parallel_branches: Optional[list[str]] = Field(default=None, description="并行分支")

    # 循环节点特有
    loop_body: Optional[str] = Field(default=None, description="循环体节点")
    loop_condition: Optional[str] = Field(default=None, description="循环条件")

    # Agent 节点特有
    agent_id: Optional[str] = Field(default=None, description="Agent ID")
    prompt: Optional[str] = Field(default=None, description="提示词模板")
    output_var: Optional[str] = Field(default=None, description="输出变量名")

    # Script 节点特有
    command: Optional[str] = Field(default=None, description="命令模板")

    # Human 节点特有
    approval_message: Optional[str] = Field(default=None, description="审批提示")
    timeout_seconds: Optional[int] = Field(default=None, description="超时秒数")

    # Wait 节点特有
    wait_seconds: Optional[int] = Field(default=None, description="等待秒数")
    wait_until: Optional[str] = Field(default=None, description="等待到指定时间")


class FlowParameter(BaseModel):
    """流程参数定义"""

    name: str = Field(..., description="参数名")
    type: str = Field(default="string", description="参数类型")
    required: bool = Field(default=False, description="是否必需")
    default: Optional[Any] = Field(default=None, description="默认值")
    description: Optional[str] = Field(default=None, description="参数描述")


class FlowTemplate(BaseModel):
    """流程模板"""

    id: str = Field(..., description="模板唯一标识")
    name: str = Field(..., description="模板名称")
    version: str = Field(default="1.0.0", description="模板版本")
    description: Optional[str] = Field(default=None, description="模板描述")
    nodes: dict[str, FlowNode] = Field(default_factory=dict, description="节点映射")
    params: list[FlowParameter] = Field(default_factory=list, description="参数定义")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "hello-world",
                    "name": "Hello World",
                    "version": "1.0.0",
                    "nodes": {
                        "start": {"id": "start", "type": "start", "next": "greet"},
                        "greet": {
                            "id": "greet",
                            "type": "agent",
                            "agent_id": "default",
                            "prompt": "Say hello to {name}",
                            "output_var": "greeting",
                            "next": "end",
                        },
                        "end": {"id": "end", "type": "end"},
                    },
                    "params": [{"name": "name", "type": "string", "required": True}],
                }
            ]
        }
    }
