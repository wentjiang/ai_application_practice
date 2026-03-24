# 项目 3：自动化代码Review Bot

这是一个AI驱动的自动化代码审查工具，能够分析 git diff 并提供结构化的Review意见。

## 功能

✨ **三维度代码分析：**
- 🔒 **安全问题** — SQL注入、权限漏洞、敏感信息泄露等
- ⚡ **性能问题** — N+1查询、死循环、内存泄漏等
- 📝 **代码规范** — 命名、复杂度、文档注释等

📊 **结构化输出：**
- 按严重度分类问题（高/中/低）
- 给出具体的问题位置和修复建议
- 代码示例展示改进方案

🎯 **灵活的使用方式：**
- 审查未提交的改动（默认）
- 审查已暂存（staged）的改动
- 审查特定提交或提交范围

## 快速开始

### 1. 安装项目

在仓库根目录：
```bash
pip install -e project3_code_review_bot/
```

### 2. 使用 codereview 命令

```bash
# 审查当前未提交的改动
codereview

# 审查已暂存的改动
codereview --staged

# 审查与上一条提交的差异
codereview --commit HEAD~1

# 审查两次提交之间的差异
codereview --commit commit1..commit2
```

## 工作原理

1. **获取代码变动** — 通过 `get_git_diff` 工具读取 git diff 内容
2. **上下文补充** — 如需要，通过 `read_file` 工具获取完整的文件内容
3. **智能分析** — Claude 分析代码变动，从安全、性能、规范三个维度评估
4. **结构化反馈** — 输出格式化的Review报告，包含问题描述、严重度和修复建议

## 项目结构

```
project3_code_review_bot/
├── pyproject.toml          # 项目元数据和依赖
├── code_reviewer/
│   ├── __init__.py
│   ├── main.py            # CLI 入口点
│   ├── agent.py           # Agent 适配层（调用 shared_agent 的通用循环）
│   └── tools.py           # 工具定义（get_git_diff、read_file）
└── README.md              # 本文件
```

## 技术栈

- **LLM 后端**：支持 Ollama（qwen3:8b 等）和 Anthropic Claude API
- **工具实现**：subprocess 调用 git，文件系统操作
- **架构**：基于 shared_agent 的通用 Tool Use 循环

## 使用示例

### 场景 1：代码提交前的本地Review

```bash
# 修改了代码
vim src/auth.py

# 想要提交前做个快速Review
codereview

# 获得安全性和性能的反馈后再决定是否修改、提交
```

### 场景 2：Review 同学的 PR（基于本地 git）

```bash
# 拉取目标分支的最新代码
git fetch origin feature-branch

# 对比你的改动和 feature-branch 的差异
codereview --commit main..feature-branch

# 得到详细的Review意见
```

### 场景 3：集成到 CI/CD 或 Git Hook

创建 `.git/hooks/pre-push` 脚本：
```bash
#!/bin/bash
# 在push前自动做Review
codereview --staged
echo "Review完毕，继续push..."
```

## 扩展方向

1. **GitHub Actions 集成** — 自动在PR上发表评论
2. **多语言支持** — 支持 Python、JavaScript、Go 等语言的特定检查
3. **自定义规则** — 让用户定义团队特定的代码规范
4. **持久化存储** — 记录Review历史，生成代码质量报告
5. **Batch Review** — 一次审查多个文件或提交

## 环境配置

项目使用 `.env` 文件配置后端：

```bash
# 使用 Ollama（本地运行，无需 API Key）
MODEL=qwen3:8b
OLLAMA_BASE_URL=http://localhost:11434/v1

# 或使用 Anthropic Claude（需要 API Key）
ANTHROPIC_API_PRACTICE_KEY=sk-ant-...
```

## 相关文件

- [practice_projects.md](../doc/practice_projects.md) — 项目设计文档
- [CLAUDE.md](../CLAUDE.md) — 环境配置指南
- [shared_agent/tool_loop.py](../shared_agent/tool_loop.py) — 通用 Tool Use 循环实现
