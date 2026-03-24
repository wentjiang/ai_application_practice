"""项目 2 入口：网页内容总结 Bot。"""

import os
from dotenv import load_dotenv

from . import agent

load_dotenv()

SYSTEM_PROMPT = (
    "你是一个网页内容总结助手。\n\n"
    "【关键规则】每次用户给出 URL 时，你必须：\n"
    "1. 立即调用 fetch_webpage 工具获取真实网页内容\n"
    "2. 不要猜测或虚构网页内容\n"
    "3. 基于工具返回的真实内容生成摘要\n\n"
    "【输出格式】使用以下固定结构，且使用中文：\n"
    "1) 三句话摘要：正好 3 条编号句子\n"
    "2) 关键观点：4-6 条 bullet points\n"
    "3) 值得精读评分：1-10 的整数，并给出一句理由\n\n"
    "【错误处理】如果工具返回错误，先说明错误，再给出可操作建议。"
)


def main() -> None:
    print("=" * 50)
    print(f"网页内容总结 Bot（{os.getenv('MODEL', 'qwen3:8b')}）")
    print("输入 URL 开始总结；输入 'exit' 或 'quit' 退出")
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

        # 把裸 URL 自动补成强制工具调用的需求表达
        if user_input.startswith(("http://", "https://")) or "." in user_input:
            # 使用更强制的语言来确保 LLM 调用工具而不是虚构内容
            prompt = f"【任务】总结网页内容\n【URL】{user_input}\n请先调用 fetch_webpage 工具获取真实网页内容，然后按照规定格式输出摘要。"
        else:
            prompt = user_input

        messages.append({"role": "user", "content": prompt})

        print("\n助手: ", end="", flush=True)
        reply = agent.run(messages)
        print(reply)

        messages.append({"role": "assistant", "content": reply})
