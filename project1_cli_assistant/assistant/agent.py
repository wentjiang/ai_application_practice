"""
Tool Use 循环。

负责与模型通信，处理工具调用，直到模型给出最终回答。
"""

import json
import os

from openai import OpenAI

from .tools import TOOLS_SCHEMA, TOOL_HANDLERS

# ── 客户端初始化（从环境变量读取配置） ────────────────────────
_client = OpenAI(
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
    api_key="ollama",
)
_model = os.getenv("MODEL", "qwen3:8b")


def run(messages: list[dict]) -> str:
    """
    Tool Use 循环：
      1. 发消息给模型
      2. 模型返回 tool_call → 执行工具 → 结果追加到 messages
      3. 重复，直到模型返回最终回答
    """
    while True:
        response = _client.chat.completions.create(
            model=_model,
            messages=messages,
            tools=TOOLS_SCHEMA,
        )

        choice = response.choices[0]
        msg = choice.message

        if choice.finish_reason == "stop" or not msg.tool_calls:
            return msg.content or ""

        # 把模型的 tool_call 消息加入历史
        messages.append(msg)

        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            print(f"\n  [调用工具] {name}({args})")

            handler = TOOL_HANDLERS.get(name)
            result = handler(**args) if handler else f"[错误] 未知工具：{name}"

            print(f"  [工具结果] {result[:200]}{'...' if len(result) > 200 else ''}")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result,
            })
