# AI 应用实践项目

## 环境准备

### 1. 确认 Python 版本

本项目使用 pyenv 管理 Python 版本，根目录的 `.python-version` 会自动锁定版本。

```bash
python --version  # 应显示 Python 3.13.3
```

### 2. 创建并激活虚拟环境

```bash
cd /path/to/ai_application_practice

python -m venv .venv
source .venv/bin/activate
```

激活后命令行前缀会出现 `(.venv)`。

### 3. 配置环境变量

```bash
cp .env.example .env
# 按需修改 .env 中的配置
```

---

## 项目列表

### 项目 1：命令行 AI 助手

```bash
pip install -e project1_cli_assistant/
assistant
```

依赖本地 Ollama 运行，启动前确保模型已就绪：

```bash
ollama run qwen3:8b
```

---

## 日常使用

每次进入项目时激活虚拟环境：

```bash
source .venv/bin/activate
```

退出虚拟环境：

```bash
deactivate
```
