"""Condition 节点执行器。

REQ-0001-013: Condition 节点执行器

评估条件并选择执行分支。
"""
import re
from typing import Any

from app.executors.base import BaseExecutor, NodeResult, NodeStatus


class ConditionExecutor(BaseExecutor):
    """Condition 节点执行器

    评估条件表达式并返回匹配的分支。
    """

    def execute(
        self,
        node: dict[str, Any],
        context: dict[str, Any],
    ) -> NodeResult:
        """评估条件并选择分支

        Args:
            node: 节点配置
            context: 执行上下文

        Returns:
            NodeResult: 包含匹配分支的结果
        """
        branches = node.get("branches", {})
        config = node.get("config", {})

        # 如果有表达式，评估表达式
        expression = config.get("expression")
        if expression:
            try:
                branch = self._evaluate_expression(expression, context)
                if branch and branch in branches:
                    return NodeResult(
                        status=NodeStatus.SUCCESS,
                        output={"branch": branch, "expression": expression},
                    )
            except Exception as e:
                return NodeResult(
                    status=NodeStatus.FAILED,
                    error=f"Expression evaluation failed: {e}",
                )

        # 如果有 status 字段，根据 status 匹配
        status = context.get("status")
        if status and status in branches:
            return NodeResult(
                status=NodeStatus.SUCCESS,
                output={"branch": status},
            )

        # 检查 default 分支
        if "default" in branches:
            return NodeResult(
                status=NodeStatus.SUCCESS,
                output={"branch": "default"},
            )

        # 无匹配分支
        return NodeResult(
            status=NodeStatus.FAILED,
            error=f"No matching branch found for status '{status}' and no default branch defined",
        )

    def _evaluate_expression(
        self,
        expression: str,
        context: dict[str, Any],
    ) -> str | None:
        """评估表达式

        支持简单的比较表达式，如:
        - {count} > 10
        - {status} == "success"
        - {enabled} == true

        Args:
            expression: 表达式字符串
            context: 变量上下文

        Returns:
            匹配的分支名，或不匹配返回 None
        """
        # 替换变量
        expr = self._substitute_variables(expression, context)

        # 简单的表达式解析
        # 支持格式: value operator value
        operators = [">=", "<=", "==", "!=", ">", "<"]

        for op in operators:
            if op in expr:
                parts = expr.split(op, 1)
                if len(parts) == 2:
                    left = parts[0].strip()
                    right = parts[1].strip()

                    # 尝试转换为数值
                    try:
                        left_val = self._parse_value(left)
                        right_val = self._parse_value(right)

                        # 比较
                        result = self._compare(left_val, right_val, op)
                        if result:
                            # 返回 "pass" 或 "true" 作为分支名
                            return "pass"
                    except (ValueError, TypeError):
                        # 字符串比较
                        result = self._compare(left, right, op)
                        if result:
                            return "pass"

        return None

    def _substitute_variables(
        self,
        text: str,
        context: dict[str, Any],
    ) -> str:
        """替换文本中的变量"""
        pattern = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")

        def replace(match: re.Match) -> str:
            var_name = match.group(1)
            if var_name not in context:
                return match.group(0)
            value = context[var_name]
            if isinstance(value, str):
                return f'"{value}"'
            return str(value)

        return pattern.sub(replace, text)

    def _parse_value(self, value: str) -> int | float | bool | str:
        """解析值为适当类型"""
        value = value.strip()

        # 布尔值
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False

        # 引号字符串
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return value[1:-1]

        # 数字
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            return value

    def _compare(
        self,
        left: Any,
        right: Any,
        operator: str,
    ) -> bool:
        """比较两个值"""
        if operator == "==":
            return left == right
        elif operator == "!=":
            return left != right
        elif operator == ">":
            return left > right
        elif operator == "<":
            return left < right
        elif operator == ">=":
            return left >= right
        elif operator == "<=":
            return left <= right
        return False
