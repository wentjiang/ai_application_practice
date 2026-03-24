"""
代码Review工具定义与执行。
"""

import os
import re
import subprocess
from typing import Callable

import requests


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
            "name": "get_github_pr_diff",
            "description": "获取GitHub PR的diff内容。接收PR URL或者owner/repo/pr_number的格式。",
            "parameters": {
                "type": "object",
                "properties": {
                    "pr_url_or_path": {
                        "type": "string",
                        "description": "GitHub PR的完整URL（如 https://github.com/owner/repo/pull/123）或简短格式（如 owner/repo/123）",
                    }
                },
                "required": ["pr_url_or_path"],
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


def get_github_pr_diff(pr_url_or_path: str) -> str:
    """
    获取GitHub PR的diff内容。
    支持的格式：
    - 完整URL: https://github.com/owner/repo/pull/123
    - 简短格式: owner/repo/123
    """
    try:
        # 解析PR信息
        match = None
        
        # 匹配完整URL格式
        if pr_url_or_path.startswith("http"):
            match = re.search(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)", pr_url_or_path)
        # 匹配简短格式：owner/repo/123
        else:
            match = re.match(r"([^/]+)/([^/]+)/(\d+)", pr_url_or_path)
        
        if not match:
            return f"[错误] 无效的PR格式。请使用以下格式之一：\n  - https://github.com/owner/repo/pull/123\n  - owner/repo/123"
        
        owner, repo, pr_number = match.groups()
        
        # 调用GitHub API获取PR的diff
        github_token = os.getenv("GITHUB_TOKEN", "")
        headers = {
            "Accept": "application/vnd.github.v3.diff",
            "User-Agent": "CodeReviewBot",
        }
        
        if github_token:
            headers["Authorization"] = f"token {github_token}"
        
        url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
        
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 404:
            return f"[错误] PR不存在: {owner}/{repo}/#{pr_number}"
        elif response.status_code == 403:
            return "[错误] 请求被限制。建议在.env中设置 GITHUB_TOKEN=your_token 来提高速率限制。\n访问 https://github.com/settings/tokens 创建一个personal access token"
        elif response.status_code != 200:
            return f"[错误] GitHub API错误 ({response.status_code}): {response.text[:200]}"
        
        # 从响应头中获取diff URL
        diff_url = response.links.get("diff", {}).get("url") if hasattr(response, "links") else None
        if not diff_url:
            # 手动构造diff URL
            diff_url = f"https://github.com/{owner}/{repo}/pull/{pr_number}.diff"
        
        # 获取diff内容
        diff_response = requests.get(diff_url, headers={"User-Agent": "CodeReviewBot"}, timeout=30)
        
        if diff_response.status_code != 200:
            return f"[错误] 获取PR diff失败 ({diff_response.status_code})"
        
        diff_content = diff_response.text
        
        # 获取PR的基本信息
        pr_info = response.json()
        pr_title = pr_info.get("title", "")
        pr_description = pr_info.get("body", "")
        pr_author = pr_info.get("user", {}).get("login", "unknown")
        
        # 组织返回内容
        header = f"""=== GitHub PR Review ==="
标题: {pr_title}
作者: {pr_author}
URL: https://github.com/{owner}/{repo}/pull/{pr_number}

描述:
{pr_description if pr_description else "（无描述）"}

代码变动:
"""
        
        # 限制diff大小
        max_diff_size = 100000
        if len(diff_content) > max_diff_size:
            diff_content = diff_content[:max_diff_size] + f"\n...（diff过大，仅显示前 {max_diff_size} 个字符）"
        
        return header + diff_content
        
    except requests.exceptions.Timeout:
        return "[错误] 请求超时。GitHub服务器响应缓慢，请稍后重试。"
    except requests.exceptions.ConnectionError:
        return "[错误] 网络连接失败。请检查网络连接和GitHub API是否可访问。"
    except Exception as e:
        return f"[错误] 获取GitHub PR diff失败: {e}"


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
    "get_github_pr_diff": get_github_pr_diff,
    "read_file": read_file,
}
