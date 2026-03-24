"""
代码Review工具定义与执行。
"""

import os
import subprocess
from typing import Callable


# ── Schema（发给模型的工具说明） ───────────────────────────────
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_git_diff",
            "description": "获取当前 git 仓库与上一次提交之间的差异（diff），用于代码Review。可指定特定的 commit range 或直接获取 HEAD 与工作目录的差异。",
            "parameters": {
                "type": "object",
                "properties": {
                    "args": {
                        "type": "string",
                        "description": "git diff 的额外参数，例如空字符串表示未提交的改动，'HEAD~1' 表示与上一条提交对比，'commit1..commit2' 表示两次提交之间的差异",
                        "default": "",
                    }
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "读取本地文件内容，用于获取完整的上下文或了解文件的部分内容。",
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
def get_git_diff(args: str = "") -> str:
    """
    执行 git diff 获取代码差异。
    默认获取 HEAD 与工作目录的差异。
    """
    try:
        cmd = f"git diff {args}".strip()
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
        )
        if result.returncode != 0:
            return f"[错误] git diff 执行失败: {result.stderr}"
        
        if not result.stdout.strip():
            return "[提示] 没有检测到代码差异"
        
        return result.stdout
    except Exception as e:
        return f"[错误] 执行 git diff 失败: {e}"


def read_file(path: str) -> str:
    """读取本地文件内容，返回文件的全部或部分内容。"""
    try:
        # 处理相对路径
        if not os.path.isabs(path):
            path = os.path.join(os.getcwd(), path)
        
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 限制输出大小，防止超过上下文
        max_size = 50000
        if len(content) > max_size:
            return content[:max_size] + f"\n... [文件过大，仅显示前 {max_size} 个字符]"
        
        return content
    except FileNotFoundError:
        return f"[错误] 文件不存在: {path}"
    except Exception as e:
        return f"[错误] 读取文件失败: {e}"


# ── 工具处理器字典 ───────────────────────────────────────────
TOOL_HANDLERS: dict[str, Callable] = {
    "get_git_diff": get_git_diff,
    "read_file": read_file,
}
