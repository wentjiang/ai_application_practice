"""
代码Review Bot 的程序入口。

用法：
  codereview                    # 审查当前工作目录的未提交改动
  codereview --staged           # 审查已暂存（staged）的改动
  codereview --commit HEAD~1    # 审查与上一次提交的差异
"""

import os
import sys
from argparse import ArgumentParser
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件

from . import agent

SYSTEM_PROMPT = """你是一个专业的代码Review助手，能够分析代码变动并给出规范化的Review意见。

## 分析框架

对于提交的代码diff，你需要从以下三个方面进行深入分析：

### 1. **安全问题** 🔒
检查代码是否存在：
- SQL注入、命令注入等安全漏洞
- 敏感信息泄露（密钥、密码、token）
- 权限验证不足
- 输入验证缺失
- 不安全的加密或哈希算法
- 其他OWASP Top 10 相关的问题

### 2. **性能问题** ⚡
识别可能的性能隐患：
- N+1查询问题
- 死循环或低效算法
- 内存泄漏风险
- 不必要的深拷贝或序列化
- 缺失的缓存机制
- 使用了低效的数据结构

### 3. **代码规范** 📝
检查代码是否符合最佳实践：
- 命名规范不一致
- 函数/方法过长（超过30-50行）
- 圈复杂度过高
- 缺少必要的文档注释
- 错误处理不完善
- 代码重复度高

## 输出格式

如果有问题，按如下结构组织你的回复：

```
## 代码Review报告

### 🔒 安全问题 (严重度: 高/中/低)
**问题1: [简要标题]**
- 位置: 第XX行
- 描述: 具体问题描述
- 建议: 修复建议
- 示例代码:
  ```python
  # 修复前
  ...
  # 修复后
  ...
  ```

**问题2: ...**

### ⚡ 性能问题 (严重度: 高/中/低)
...

### 📝 代码规范 (严重度: 低/中)
...

### ✅ 总结
- 总体评分: X/10
- 主要关注项: ...
- 是否可发布: 是 / 否 (需要修复上述X个问题)
```

如果代码没有发现问题，回复：
```
✅ 代码Review通过！代码质量良好，可以发布。
```

## 注意事项

- 优先处理**安全和性能问题**，其次才是规范问题
- 只指出真实存在的问题，避免过度设计建议
- 对于改进建议要具体，最好给出代码示例
- 考虑代码的**上下文和业务场景**，给出合理建议
- 语言使用中文，确保清晰准确
"""


def main() -> None:
    parser = ArgumentParser(
        description="自动化代码Review Bot - 分析git diff并给出Review意见",
        epilog="示例:\n  codereview              # 审查未提交的改动\n  codereview --staged     # 审查已暂存的改动\n  codereview --commit HEAD~1  # 审查与上一次提交的差异",
    )
    
    parser.add_argument(
        "--staged",
        action="store_true",
        help="审查已暂存（staged）的改动，而不是未提交的所有改动",
    )
    
    parser.add_argument(
        "--commit",
        type=str,
        default="",
        metavar="COMMIT",
        help="指定特定的提交范围，例如 'HEAD~1' 表示与上一条提交对比，'commit1..commit2' 表示两次提交之间的差异",
    )
    
    args = parser.parse_args()
    
    # 根据参数确定 git diff 的参数
    diff_args = ""
    if args.staged:
        diff_args = "--staged"
    elif args.commit:
        diff_args = args.commit
    
    print("=" * 60)
    print(f"代码Review Bot（{os.getenv('MODEL', 'qwen3:8b')}）")
    print("=" * 60)
    print()
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # 构造用户请求
    if diff_args:
        user_input = f"请对我的代码变动 (git diff {diff_args}) 进行Review，分析安全问题、性能问题和代码规范。"
    else:
        user_input = "请对我的代码变动 (当前未提交的改动) 进行Review，分析安全问题、性能问题和代码规范。"
    
    messages.append({"role": "user", "content": user_input})
    
    print("🔍 正在分析代码变动...\n")
    reply = agent.run(messages)
    
    print(reply)
    print()
    print("=" * 60)
