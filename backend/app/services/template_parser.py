"""YAML 模板解析器。

REQ-0001-006: YAML 模板解析器

将 YAML 格式的流程定义解析为 FlowTemplate 对象。
"""
import re
from typing import Any

import yaml

from app.models.flow_template import FlowNode, FlowParameter, FlowTemplate, NodeType


class TemplateValidationError(Exception):
    """模板验证失败异常"""

    pass


class TemplateParser:
    """YAML 模板解析器

    解析 YAML 格式的流程模板并验证其结构。
    """

    # 有效的节点类型
    VALID_NODE_TYPES = {t.value for t in NodeType}

    def parse(self, yaml_content: str) -> FlowTemplate:
        """解析 YAML 字符串

        Args:
            yaml_content: YAML 格式的模板内容

        Returns:
            FlowTemplate 对象

        Raises:
            TemplateValidationError: 解析或验证失败
        """
        try:
            data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise TemplateValidationError(f"Invalid YAML syntax: {e}") from e

        return self.parse_dict(data)

    def parse_dict(self, data: dict[str, Any]) -> FlowTemplate:
        """解析字典数据

        Args:
            data: 模板数据字典

        Returns:
            FlowTemplate 对象

        Raises:
            TemplateValidationError: 验证失败
        """
        if not isinstance(data, dict):
            raise TemplateValidationError("Template must be a dictionary")

        # 解析基本信息
        template_id = data.get("id")
        if not template_id:
            raise TemplateValidationError("Template must have an 'id' field")

        name = data.get("name")
        if not name:
            raise TemplateValidationError("Template must have a 'name' field")

        # 解析节点
        nodes_data = data.get("nodes", {})
        if not nodes_data:
            raise TemplateValidationError("Template must have at least one node")

        nodes = {}
        for node_id, node_data in nodes_data.items():
            if not isinstance(node_data, dict):
                raise TemplateValidationError(f"Node '{node_id}' must be a dictionary")
            nodes[node_id] = self._parse_node(node_id, node_data)

        # 验证必须有 start 和 end 节点
        self._validate_required_nodes(nodes)

        # 验证节点引用
        self._validate_node_references(nodes)

        # 解析参数
        params = []
        for param_data in data.get("params", []):
            params.append(self._parse_parameter(param_data))

        return FlowTemplate(
            id=template_id,
            name=name,
            version=data.get("version", "1.0.0"),
            description=data.get("description"),
            nodes=nodes,
            params=params,
        )

    def _parse_node(self, node_id: str, data: dict[str, Any]) -> FlowNode:
        """解析单个节点"""
        node_type = data.get("type")
        if not node_type:
            raise TemplateValidationError(f"Node '{node_id}' must have a 'type' field")

        if node_type not in self.VALID_NODE_TYPES:
            raise TemplateValidationError(
                f"Node '{node_id}' has invalid type '{node_type}'. "
                f"Valid types: {', '.join(sorted(self.VALID_NODE_TYPES))}"
            )

        return FlowNode(
            id=node_id,
            type=NodeType(node_type),
            name=data.get("name"),
            next=data.get("next"),
            config=data.get("config", {}),
            branches=data.get("branches"),
            parallel_branches=data.get("parallel_branches"),
            loop_body=data.get("loop_body"),
            loop_condition=data.get("loop_condition"),
            agent_id=data.get("agent_id"),
            prompt=data.get("prompt"),
            output_var=data.get("output_var"),
            command=data.get("command"),
            approval_message=data.get("approval_message"),
            timeout_seconds=data.get("timeout_seconds"),
            wait_seconds=data.get("wait_seconds"),
            wait_until=data.get("wait_until"),
        )

    def _parse_parameter(self, data: dict[str, Any]) -> FlowParameter:
        """解析参数定义"""
        name = data.get("name")
        if not name:
            raise TemplateValidationError("Parameter must have a 'name' field")

        return FlowParameter(
            name=name,
            type=data.get("type", "string"),
            required=data.get("required", False),
            default=data.get("default"),
            description=data.get("description"),
        )

    def _validate_required_nodes(self, nodes: dict[str, FlowNode]) -> None:
        """验证必须有 start 和 end 节点"""
        has_start = any(n.type == NodeType.START for n in nodes.values())
        has_end = any(n.type == NodeType.END for n in nodes.values())

        if not has_start:
            raise TemplateValidationError("Template must have a 'start' node")

        if not has_end:
            raise TemplateValidationError("Template must have an 'end' node")

    def _validate_node_references(self, nodes: dict[str, FlowNode]) -> None:
        """验证节点引用的完整性"""
        node_ids = set(nodes.keys())

        for node_id, node in nodes.items():
            # 验证 next 引用
            if node.next and node.next not in node_ids:
                raise TemplateValidationError(
                    f"Node '{node_id}' references non-existent node '{node.next}'"
                )

            # 验证条件分支引用
            if node.branches:
                for branch_name, target_id in node.branches.items():
                    if target_id not in node_ids:
                        raise TemplateValidationError(
                            f"Node '{node_id}' branch '{branch_name}' "
                            f"references non-existent node '{target_id}'"
                        )

            # 验证并行分支引用
            if node.parallel_branches:
                for target_id in node.parallel_branches:
                    if target_id not in node_ids:
                        raise TemplateValidationError(
                            f"Node '{node_id}' parallel branch "
                            f"references non-existent node '{target_id}'"
                        )

            # 验证循环体引用
            if node.loop_body and node.loop_body not in node_ids:
                raise TemplateValidationError(
                    f"Node '{node_id}' loop_body references "
                    f"non-existent node '{node.loop_body}'"
                )
