"""Context 上下文管理。

REQ-0001-008: Context 上下文管理

管理执行过程中的变量和状态。
"""
import re
from typing import Any, Optional


class ContextVariableError(Exception):
    """上下文变量错误异常"""

    pass


class ContextManager:
    """上下文管理器

    管理执行过程中的变量和状态，支持模板变量解析。
    """

    # 匹配 {variable_name} 模板变量
    VARIABLE_PATTERN = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")

    def __init__(self):
        # execution_id -> {key: value}
        self._contexts: dict[str, dict[str, Any]] = {}

    def get(
        self,
        execution_id: str,
        key: str,
        default: Optional[Any] = None,
    ) -> Any:
        """获取变量值

        Args:
            execution_id: 执行 ID
            key: 变量名
            default: 默认值（变量不存在时返回）

        Returns:
            变量值

        Raises:
            ContextVariableError: 变量不存在且未提供默认值
        """
        ctx = self._contexts.get(execution_id, {})
        if key not in ctx:
            if default is not None:
                return default
            raise ContextVariableError(
                f"Variable '{key}' not found in execution '{execution_id}'"
            )
        return ctx[key]

    def set(
        self,
        execution_id: str,
        key: str,
        value: Any,
    ) -> None:
        """设置变量

        Args:
            execution_id: 执行 ID
            key: 变量名
            value: 变量值
        """
        if execution_id not in self._contexts:
            self._contexts[execution_id] = {}
        self._contexts[execution_id][key] = value

    def set_default(
        self,
        execution_id: str,
        key: str,
        value: Any,
    ) -> bool:
        """设置默认值（变量不存在时）

        Args:
            execution_id: 执行 ID
            key: 变量名
            value: 默认值

        Returns:
            是否设置了默认值（变量不存在时返回 True）
        """
        if execution_id not in self._contexts:
            self._contexts[execution_id] = {}

        if key not in self._contexts[execution_id]:
            self._contexts[execution_id][key] = value
            return True
        return False

    def delete(
        self,
        execution_id: str,
        key: str,
    ) -> bool:
        """删除变量

        Args:
            execution_id: 执行 ID
            key: 变量名

        Returns:
            是否删除成功
        """
        ctx = self._contexts.get(execution_id, {})
        if key in ctx:
            del ctx[key]
            return True
        return False

    def get_all(self, execution_id: str) -> dict[str, Any]:
        """获取完整上下文

        Args:
            execution_id: 执行 ID

        Returns:
            上下文字典（副本）
        """
        return dict(self._contexts.get(execution_id, {}))

    def clear(self, execution_id: str) -> None:
        """清空执行上下文

        Args:
            execution_id: 执行 ID
        """
        if execution_id in self._contexts:
            del self._contexts[execution_id]

    def resolve_variables(
        self,
        execution_id: str,
        text: str,
    ) -> str:
        """解析模板变量

        将文本中的 {var_name} 替换为实际值。

        Args:
            execution_id: 执行 ID
            text: 包含模板变量的文本

        Returns:
            替换后的文本

        Raises:
            ContextVariableError: 变量不存在
        """
        ctx = self._contexts.get(execution_id, {})

        def replace(match: re.Match) -> str:
            var_name = match.group(1)
            if var_name not in ctx:
                raise ContextVariableError(
                    f"Variable '{var_name}' not found in execution '{execution_id}'"
                )
            return str(ctx[var_name])

        return self.VARIABLE_PATTERN.sub(replace, text)

    def has(self, execution_id: str, key: str) -> bool:
        """检查变量是否存在

        Args:
            execution_id: 执行 ID
            key: 变量名

        Returns:
            变量是否存在
        """
        ctx = self._contexts.get(execution_id, {})
        return key in ctx

    def keys(self, execution_id: str) -> list[str]:
        """获取所有变量名

        Args:
            execution_id: 执行 ID

        Returns:
            变量名列表
        """
        return list(self._contexts.get(execution_id, {}).keys())
