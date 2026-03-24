"""
工具定义与执行。

每个工具由两部分组成：
  - SCHEMA：告诉模型"这个工具能做什么、需要什么参数"
  - handler：实际执行逻辑
"""

import os
import subprocess
from typing import Callable

# ── Schema（发给模型的工具说明） ───────────────────────────────
# function call固定的格式，详见 Ollama 官方文档：https://ollama.com/docs/tools#function-calls
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "run_shell",
            "description": "执行 shell 命令，返回命令输出。适合查看文件、git 操作、查询系统信息等。",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "要执行的 shell 命令，例如 'ls -lh' 或 'git log --oneline -10'",
                    }
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取本地文件内容。适合查看代码、配置文件、文档等。",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "文件的绝对路径或相对路径",
                    }
                },
                "required": ["path"],
            },
        },
    },
]


# ── Handlers（实际执行逻辑） ───────────────────────────────────
def run_shell(command: str) -> str:
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.getcwd(),
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]: {result.stderr}"
        return output.strip() or "(命令执行成功，无输出)"
    except subprocess.TimeoutExpired:
        return "[错误] 命令执行超时"
    except Exception as e:
        return f"[错误] {e}"


def read_file(path: str) -> str:
    try:
        with open(os.path.expanduser(path), "r", encoding="utf-8") as f:
            content = f.read()
        if len(content) > 4000:
            content = content[:4000] + "\n...(文件过长，已截断)"
        return content
    except FileNotFoundError:
        return f"[错误] 文件不存在：{path}"
    except Exception as e:
        return f"[错误] {e}"


# ── 工具注册表（名称 → handler） ──────────────────────────────
TOOL_HANDLERS: dict[str, Callable] = {
    "run_shell": run_shell,
    "read_file": read_file,
}
