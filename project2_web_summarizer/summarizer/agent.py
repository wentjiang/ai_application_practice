"""项目 2 的 Agent 适配层。"""

import sys
from pathlib import Path

try:
    from shared_agent import run_tool_loop
except ModuleNotFoundError:
    # 兜底：把仓库根目录加入搜索路径，以支持从任意 cwd 启动。
    repo_root = Path(__file__).resolve().parents[2]
    if str(repo_root) not in sys.path:
        sys.path.append(str(repo_root))
    from shared_agent import run_tool_loop

from .tools import TOOL_HANDLERS, TOOLS_SCHEMA


def run(messages: list[dict]) -> str:
    """执行项目 2 工具配置下的通用 Tool Use 循环。"""
    return run_tool_loop(messages, TOOLS_SCHEMA, TOOL_HANDLERS)
