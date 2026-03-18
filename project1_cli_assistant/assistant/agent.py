"""
Tool Use 循环。

负责与模型通信，处理工具调用，直到模型给出最终回答。

支持两种后端（通过环境变量切换）：
  - Ollama（默认）：设置 OLLAMA_BASE_URL 和 MODEL
  - Anthropic Claude API：设置 ANTHROPIC_API_KEY，MODEL 可选（默认 claude-opus-4-6）
"""

import json
import os

from .tools import TOOLS_SCHEMA, TOOL_HANDLERS

_ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_PRACTICE_KEY")
_USE_ANTHROPIC = bool(_ANTHROPIC_API_KEY)

if _USE_ANTHROPIC:
    import anthropic

    _anthropic_client = anthropic.Anthropic(api_key=_ANTHROPIC_API_KEY)
    _model = os.getenv("MODEL", "claude-opus-4-6")

    # 将 OpenAI 格式的 tools schema 转换为 Anthropic 格式
    _ANTHROPIC_TOOLS = [
        {
            "name": t["function"]["name"],
            "description": t["function"]["description"],
            "input_schema": t["function"]["parameters"],
        }
        for t in TOOLS_SCHEMA
    ]
else:
    from openai import OpenAI

    _openai_client = OpenAI(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        api_key="ollama",
    )
    _model = os.getenv("MODEL", "qwen3:8b")


def _run_anthropic(messages: list[dict]) -> str:
    """使用 Anthropic Claude API 的 Tool Use 循环。"""
    # 分离 system 消息
    system = ""
    chat_messages = []
    for msg in messages:
        if msg["role"] == "system":
            system = msg["content"]
        else:
            chat_messages.append(msg)

    while True:
        kwargs = dict(
            model=_model,
            max_tokens=4096,
            tools=_ANTHROPIC_TOOLS,
            messages=chat_messages,
        )
        if system:
            kwargs["system"] = system

        response = _anthropic_client.messages.create(**kwargs)

        if response.stop_reason == "end_turn":
            text_block = next((b for b in response.content if b.type == "text"), None)
            return text_block.text if text_block else ""

        # 处理工具调用
        tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
        if not tool_use_blocks:
            text_block = next((b for b in response.content if b.type == "text"), None)
            return text_block.text if text_block else ""

        # 把 assistant 的完整响应加入历史
        chat_messages.append({"role": "assistant", "content": response.content})

        # 执行所有工具并收集结果
        tool_results = []
        for block in tool_use_blocks:
            name = block.name
            args = block.input

            print(f"\n  [调用工具] {name}({args})")

            handler = TOOL_HANDLERS.get(name)
            result = handler(**args) if handler else f"[错误] 未知工具：{name}"

            print(f"  [工具结果] {result[:200]}{'...' if len(result) > 200 else ''}")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })

        chat_messages.append({"role": "user", "content": tool_results})


def _run_ollama(messages: list[dict]) -> str:
    """使用 Ollama（OpenAI 兼容接口）的 Tool Use 循环。"""
    while True:
        response = _openai_client.chat.completions.create(
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


def run(messages: list[dict]) -> str:
    """
    Tool Use 循环：
      1. 发消息给模型
      2. 模型返回 tool_call → 执行工具 → 结果追加到 messages
      3. 重复，直到模型返回最终回答
    """
    if _USE_ANTHROPIC:
        return _run_anthropic(messages)
    return _run_ollama(messages)
