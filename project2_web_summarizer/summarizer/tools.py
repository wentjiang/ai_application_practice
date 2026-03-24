"""项目 2 工具定义：抓取网页正文。"""

from typing import Callable
import warnings

import requests
from bs4 import BeautifulSoup
from requests.exceptions import SSLError
import urllib3

# 抑制 SSL 不安全连接警告（仅在必要时使用 verify=False）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "fetch_webpage",
            "description": "抓取网页正文，返回标题和文本内容。",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "完整网页 URL，例如 https://example.com/article",
                    },
                    "max_chars": {
                        "type": "integer",
                        "description": "正文最大返回字符数，默认 8000",
                        "default": 8000,
                    },
                },
                "required": ["url"],
            },
        },
    }
]


def fetch_webpage(url: str, max_chars: int = 8000) -> str:
    """抓取 URL 并提取网页标题与正文文本。"""
    normalized = url.strip()
    if not normalized.startswith(("http://", "https://")):
        normalized = "https://" + normalized

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; project2-web-summarizer/0.1)",
    }

    response = None
    last_error = None

    # 尝试 1：标准 HTTPS + SSL 验证
    try:
        response = requests.get(normalized, timeout=10, headers=headers)
        response.raise_for_status()
    except SSLError as e:
        last_error = e
        # 尝试 2：禁用 SSL 验证（某些本地环境证书链不完整）
        try:
            response = requests.get(normalized, timeout=10, headers=headers, verify=False)
            response.raise_for_status()
        except Exception as e:
            last_error = e
    except requests.exceptions.Timeout:
        return f"[错误] 超时（10 秒）：网站 {normalized} 响应过慢或无法访问"
    except requests.exceptions.ConnectionError:
        return f"[错误] 连接失败：无法访问 {normalized}（网络问题或 DNS 解析失败）"
    except Exception as e:
        return f"[错误] 抓取失败：{type(e).__name__}: {e}"

    if response is None:
        return f"[错误] 抓取失败：{type(last_error).__name__}: {last_error}"

    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript", "svg", "iframe"]):
        tag.decompose()

    title = (soup.title.string or "").strip() if soup.title else "(无标题)"

    # 优先选择语义化正文标签，回退到 body 全文。
    candidates = []
    for selector in ("article", "main", "[role='main']"):
        node = soup.select_one(selector)
        if node:
            text = node.get_text("\n", strip=True)
            if text:
                candidates.append(text)

    if candidates:
        body_text = max(candidates, key=len)
    else:
        body = soup.body or soup
        body_text = body.get_text("\n", strip=True)

    lines = [line.strip() for line in body_text.splitlines() if line.strip()]
    compact_text = "\n".join(lines)

    if len(compact_text) > max_chars:
        compact_text = compact_text[:max_chars] + "\n...(正文过长，已截断)"

    return f"URL: {normalized}\n标题: {title}\n\n正文:\n{compact_text}"


TOOL_HANDLERS: dict[str, Callable] = {
    "fetch_webpage": fetch_webpage,
}
