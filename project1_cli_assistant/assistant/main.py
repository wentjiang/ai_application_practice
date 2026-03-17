"""
程序入口 —— 多轮对话 REPL。
"""

import os
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件

from . import agent

SYSTEM_PROMPT = (
    "你是一个命令行 AI 助手，可以帮用户操作本地文件系统和执行 shell 命令。\n"
    f"当前工作目录：{os.getcwd()}\n"
    "遇到需要查看文件或执行命令的问题，主动使用工具获取信息，再给出回答。"
)


def main() -> None:
    print("=" * 50)
    print(f"命令行 AI 助手（{os.getenv('MODEL', 'qwen3:8b')}）")
    print("输入 'exit' 或 'quit' 退出")
    print("=" * 50)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            user_input = input("\n你: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("再见！")
            break

        messages.append({"role": "user", "content": user_input})

        print("\n助手: ", end="", flush=True)
        reply = agent.run(messages)
        print(reply)

        messages.append({"role": "assistant", "content": reply})
