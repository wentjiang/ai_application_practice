"""通用 Tool Use 循环，支持 Ollama(OpenAI 兼容) 与 Anthropic。"""

import json
import os
from importlib import import_module
from collections.abc import Callable


def _to_anthropic_tools(openai_tools: list[dict]) -> list[dict]:
    """把 OpenAI function tool schema 转成 Anthropic tools 格式。"""
    converted = []
    for tool in openai_tools:
        if tool.get("type") != "function":
            continue
        function = tool.get("function", {})
        converted.append(
            {
                "name": function.get("name", ""),
                "description": function.get("description", ""),
                "input_schema": function.get("parameters", {"type": "object", "properties": {}}),
            }
        )
    return converted


def _call_tool(tool_handlers: dict[str, Callable], tool_name: str, arguments: dict) -> str:
    handler = tool_handlers.get(tool_name)
    if not handler:
        return f"[错误] 未知工具: {tool_name}"

    try:
        result = handler(**arguments)
        return str(result)
    except TypeError as e:
        return f"[错误] 工具参数错误: {e}"
    except Exception as e:
        return f"[错误] 工具执行失败: {e}"


def _run_ollama(messages: list[dict], tools_schema: list[dict], tool_handlers: dict[str, Callable]) -> str:
    OpenAI = import_module("openai").OpenAI
    client = OpenAI(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
        api_key=os.getenv("OPENAI_API_KEY", "ollama"),
    )

    local_messages = [*messages]

    while True:
        response = client.chat.completions.create(
            model=os.getenv("MODEL", "qwen3:8b"),
            messages=local_messages,
            tools=tools_schema,
            tool_choice="auto",
        )

        message = response.choices[0].message
        tool_calls = message.tool_calls or []

        if not tool_calls:
            return message.content or ""

        local_messages.append(
            {
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in tool_calls
                ],
            }
        )

        for tc in tool_calls:
            tool_name = tc.function.name
            raw_args = tc.function.arguments or "{}"
            try:
                args = json.loads(raw_args)
            except json.JSONDecodeError:
                args = {}

            result = _call_tool(tool_handlers, tool_name, args)
            local_messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "name": tool_name,
                    "content": result,
                }
            )


def _extract_system_prompt(messages: list[dict]) -> str:
    parts = [msg.get("content", "") for msg in messages if msg.get("role") == "system"]
    return "\n".join(part for part in parts if part)


def _strip_system_messages(messages: list[dict]) -> list[dict]:
    stripped = []
    for msg in messages:
        role = msg.get("role")
        if role == "system":
            continue
        if role in ("user", "assistant"):
            stripped.append({"role": role, "content": msg.get("content", "")})
    return stripped


def _run_anthropic(messages: list[dict], tools_schema: list[dict], tool_handlers: dict[str, Callable]) -> str:
    api_key = os.getenv("ANTHROPIC_API_PRACTICE_KEY")
    if not api_key:
        return "[错误] 未设置 ANTHROPIC_API_PRACTICE_KEY"

    Anthropic = import_module("anthropic").Anthropic
    client = Anthropic(api_key=api_key)
    local_messages = _strip_system_messages(messages)
    system_prompt = _extract_system_prompt(messages)
    anthropic_tools = _to_anthropic_tools(tools_schema)

    while True:
        response = client.messages.create(
            model=os.getenv("MODEL", "claude-opus-4-6"),
            max_tokens=4096,
            system=system_prompt,
            messages=local_messages,
            tools=anthropic_tools,
        )

        if response.stop_reason == "end_turn":
            text = "".join(block.text for block in response.content if block.type == "text").strip()
            return text

        local_messages.append(
            {
                "role": "assistant",
                "content": [block.model_dump() for block in response.content],
            }
        )

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            result = _call_tool(tool_handlers, block.name, block.input or {})
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                }
            )

        if not tool_results:
            text = "".join(block.text for block in response.content if block.type == "text").strip()
            return text

        local_messages.append({"role": "user", "content": tool_results})


def run_tool_loop(messages: list[dict], tools_schema: list[dict], tool_handlers: dict[str, Callable]) -> str:
    """根据环境变量自动选择 Anthropic 或 Ollama 后端执行 Tool Use 循环。"""
    if os.getenv("ANTHROPIC_API_PRACTICE_KEY"):
        return _run_anthropic(messages, tools_schema, tool_handlers)
    return _run_ollama(messages, tools_schema, tool_handlers)
