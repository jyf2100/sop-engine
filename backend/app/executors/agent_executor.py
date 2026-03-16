"""Agent 节点执行器。

REQ-0001-012: Agent 节点执行器

调用 OpenClaw Agent 执行任务。
"""
import re
from typing import Any, Optional

from app.executors.base import BaseExecutor, NodeResult, NodeStatus
from app.services.context_manager import ContextManager


class AgentExecutor(BaseExecutor):
    """Agent 节点执行器

    调用 OpenClaw Agent 执行任务。
    """

    def __init__(
        self,
        openclaw_url: Optional[str] = None,
        openclaw_token: Optional[str] = None,
        context_manager: Optional[ContextManager] = None,
    ):
        self.openclaw_url = openclaw_url
        self.openclaw_token = openclaw_token
        self.context_manager = context_manager

    def execute(
        self,
        node: dict[str, Any],
        context: dict[str, Any],
    ) -> NodeResult:
        """调用 Agent

        Args:
            node: 节点配置
            context: 执行上下文

        Returns:
            NodeResult: 执行结果
        """
        # 验证必需字段
        agent_id = node.get("agent_id")
        if not agent_id:
            return NodeResult(
                status=NodeStatus.FAILED,
                error="Missing required field: 'agent_id'",
            )

        prompt = node.get("prompt")
        if not prompt:
            return NodeResult(
                status=NodeStatus.FAILED,
                error="Missing required field: 'prompt'",
            )

        # 变量替换
        try:
            resolved_prompt = self._substitute_variables(prompt, context)
        except Exception as e:
            return NodeResult(
                status=NodeStatus.FAILED,
                error=f"Failed to substitute variables in prompt: {e}",
            )

        # 获取配置
        config = node.get("config", {})
        timeout_seconds = config.get("timeout_seconds", 300)
        model = config.get("model")
        thinking = config.get("thinking", "medium")

        # 构建请求
        request = {
            "message": resolved_prompt,
            "agentId": agent_id,
            "model": model,
            "thinking": thinking,
            "timeoutSeconds": timeout_seconds,
        }

        # 如果配置了 OpenClaw URL，调用真实 Agent
        if self.openclaw_url:
            return self._call_openclaw(request)
        else:
            # 没有配置 OpenClaw，返回模拟响应
            return NodeResult(
                status=NodeStatus.SUCCESS,
                output={
                    "agent_id": agent_id,
                    "prompt": resolved_prompt,
                    "response": "[MOCK] Agent response",
                    "model": model,
                },
            )

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
                return match.group(0)  # 保留原变量
            value = context[var_name]
            return str(value)

        return pattern.sub(replace, text)

    def _call_openclaw(self, request: dict[str, Any]) -> NodeResult:
        """调用 OpenClaw webhook

        Args:
            request: 请求体

        Returns:
            NodeResult: 执行结果
        """
        import httpx

        try:
            headers = {"Content-Type": "application/json"}
            if self.openclaw_token:
                headers["Authorization"] = f"Bearer {self.openclaw_token}"

            with httpx.Client(timeout=request.get("timeout_seconds", 300)) as client:
                response = client.post(
                    f"{self.openclaw_url}/hooks/agent",
                    json=request,
                    headers=headers,
                )

                if response.status_code == 200:
                    return NodeResult(
                        status=NodeStatus.SUCCESS,
                        output={
                            "agent_id": request.get("agentId"),
                            "prompt": request.get("message"),
                            "response": response.json(),
                        },
                    )
                elif response.status_code == 401:
                    return NodeResult(
                        status=NodeStatus.FAILED,
                        error="Authentication failed",
                    )
                elif response.status_code == 429:
                    return NodeResult(
                        status=NodeStatus.FAILED,
                        error="Rate limited",
                    )
                else:
                    return NodeResult(
                        status=NodeStatus.FAILED,
                        error=f"OpenClaw returned {response.status_code}: {response.text}",
                    )

        except httpx.TimeoutException:
            return NodeResult(
                status=NodeStatus.FAILED,
                error="Request timed out",
            )
        except httpx.HTTPError as e:
            return NodeResult(
                status=NodeStatus.FAILED,
                error=f"HTTP error: {e}",
            )
