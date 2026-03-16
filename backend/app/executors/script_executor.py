"""Script 节点执行器。

REQ-0001-011: Script 节点执行器

执行 shell 命令作为流程节点。
"""
import asyncio
import subprocess
import re
from typing import Any

from app.executors.base import BaseExecutor, NodeResult, NodeStatus


class NodeExecutionError(Exception):
    """节点执行错误"""

    pass


class ScriptExecutor(BaseExecutor):
    """Script 节点执行器

    执行 shell 命令并捕获输出。
    """

    DEFAULT_TIMEOUT = 300  # 5 minutes

    def execute(
        self,
        node: dict[str, Any],
        context: dict[str, Any],
    ) -> NodeResult:
        """执行 shell 命令

        Args:
            node: 节点配置
            context: 执行上下文

        Returns:
            NodeResult: 执行结果
        """
        command = node.get("command")
        if not command:
            return NodeResult(
                status=NodeStatus.FAILED,
                error="Missing required field: 'command'",
            )

        # 变量替换
        try:
            command = self._substitute_variables(command, context)
        except Exception as e:
            return NodeResult(
                status=NodeStatus.FAILED,
                error=f"Variable substitution failed: {e}",
            )

        # 获取超时配置
        config = node.get("config", {})
        timeout = config.get("timeout_seconds", self.DEFAULT_TIMEOUT)

        # 执行命令
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            # 构建输出
            output = {
                "stdout": result.stdout.strip() if result.stdout else "",
                "stderr": result.stderr.strip() if result.stderr else "",
                "exit_code": result.returncode,
                "command": command,
            }

            if result.returncode == 0:
                return NodeResult(
                    status=NodeStatus.SUCCESS,
                    output=output,
                )
            else:
                return NodeResult(
                    status=NodeStatus.FAILED,
                    output=output,
                    error=f"Command exited with code {result.returncode}: {result.stderr}",
                )

        except subprocess.TimeoutExpired as e:
            raise NodeExecutionError(
                f"Command timed out after {timeout} seconds"
            )
        except Exception as e:
            return NodeResult(
                status=NodeStatus.FAILED,
                error=f"Command execution failed: {e}",
            )

    def _substitute_variables(
        self,
        text: str,
        context: dict[str, Any],
    ) -> str:
        """替换文本中的变量

        Args:
            text: 包含 {var} 格式变量的文本
            context: 变量上下文

        Returns:
            替换后的文本
        """
        pattern = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")

        def replace(match: re.Match) -> str:
            var_name = match.group(1)
            if var_name not in context:
                return match.group(0)  # 保留原变量
            value = context[var_name]
            return str(value)

        return pattern.sub(replace, text)
