# 快速开始 — 5分钟内运行你的第一个Review

## 前置要求

- ✅ Python 3.13
- ✅ git 仓库
- ✅ 已安装项目依赖

---

## 步骤1: 环境设置（仅第一次）

```bash
# 进入项目根目录
cd ai_application_practice

# 创建Python虚拟环境
python3 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate  # Windows

# 安装所有依赖
pip install -r requirements.txt

# 安装code-review-bot项目
pip install -e project3_code_review_bot/
```

---

## 步骤2: 配置LLM后端

### 选项A: 使用Ollama（推荐开始）

```bash
# 1. 安装Ollama：https://ollama.ai
# 2. 在另一个终端启动Ollama server
ollama serve

# 3. 在第三个终端中拉取模型
ollama pull qwen3:8b

# .env 文件已经配置好了:
# MODEL=qwen3:8b
# OLLAMA_BASE_URL=http://localhost:11434/v1
```

### 选项B: 使用Anthropic Claude（更强大）

```bash
# 1. 获取API Key: https://console.anthropic.com/keys
# 2. 编辑 .env 文件，取消注释并填入你的key:
# ANTHROPIC_API_PRACTICE_KEY=sk-ant-...
```

---

## 步骤3: 运行你的第一个Review

```bash
# 激活虚拟环境（如果还没有）
source .venv/bin/activate

# 方法A：Review未提交的改动
codereview

# 方法B：Review已暂存的改动
git add your_file.py
codereview --staged

# 方法C：Review特定提交
codereview --commit HEAD~1
```

---

## 完整示例

```bash
# 1. 创建一个有问题的文件
cat > test_code.py << 'EOF'
import sqlite3

def get_user(user_id):
    db = sqlite3.connect(":memory:")
    # SQL注入风险！
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query).fetchone()
EOF

# 2. 加入git
git add test_code.py

# 3. 运行Review
codereview --staged

# 4. 查看详细的Review报告
```

---

## 输出示例

```
============================================================
代码Review Bot（qwen3:8b）
============================================================

🔍 正在分析代码变动...

## 代码Review报告

### 🔒 安全问题 (严重度: 高)
**问题1: SQL注入漏洞**
- 位置: 第5行
- 描述: 直接拼接用户输入到SQL语句
- 建议: 使用参数化查询

### ⚡ 性能问题
[无]

### 📝 代码规范
[无]

### ✅ 总结
- 总体评分: 4/10
- 主要关注项: 必须修复SQL注入
- 是否可发布: 否

============================================================
```

---

## 常见问题

### Q: 如何只Review特定的文件？

A: 使用git命令先准备好，再用codereview：

```bash
git add specific_file.py
codereview --staged
```

### Q: Review耗时太长了怎么办？

A: 
- 确保LLM server运行正常
- 缩小review范围（不要一次性review太多代码）
- 考虑分批提交

### Q: 如何跳过某个问题？

A: 在代码中添加注释（取决于LLM的理解）：

```python
# codereview: ignore=performance
for item in large_list:
    do_something(item)
```

### Q: 能否自定义Review规则？

A: 可以！编辑 `code_reviewer/main.py` 中的 `SYSTEM_PROMPT`，定制你的Review标准。

---

## 下一步

- 📖 查看 [README.md](./README.md) 了解详细功能
- 🔧 查看 [INTEGRATION.md](./INTEGRATION.md) 将Review集成到你的CI/CD
- 💡 查看 [DEMO.sh](./DEMO.sh) 了解更多使用方式

---

## 获得帮助

```bash
# 查看所有选项
codereview --help

# 查看项目状态
git status

# 查看当前配置
cat .env
```

祝你使用愉快！ 🚀
