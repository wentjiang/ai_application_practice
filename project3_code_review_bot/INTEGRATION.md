# 集成指南 — 代码Review Bot在实际工作流中的应用

本文档展示如何将自动化代码Review Bot集成到你的开发流程中。

## 方案 1：Git Pre-Push Hook（本地自动Review）

在每次push代码之前，自动运行Review，防止有问题的代码被推送。

### 步骤

1. **创建hook脚本** `.git/hooks/pre-push`

```bash
#!/bin/bash

echo "🔍 正在执行代码Review..."
codereview --staged

if [ $? -ne 0 ]; then
    echo "❌ Review失败，请先修复问题"
    exit 1
fi

echo "✅ Review通过，可以安全推送"
exit 0
```

2. **添加执行权限**

```bash
chmod +x .git/hooks/pre-push
```

3. **验证**

```bash
# 修改代码并staged
git add .

# 尝试push时会自动运行Review
git push
```

### 优势
- ✅ 在push前及早发现问题
- ✅ 无需额外的CI/CD配置
- ✅ 开发者本地立即获得反馈

### 劣势
- ❌ 不是强制的（可以通过--no-verify跳过）
- ❌ 依赖本地环境正确配置

---

## 方案 2：GitHub Actions（CI/CD自动Review）

在PR被创建时自动运行Review，并在PR上发表意见。

### 步骤

1. **创建GitHub Actions工作流** `.github/workflows/code-review.yml`

```yaml
name: Automated Code Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      
      - name: Install dependencies
        run: |
          pip install -e project3_code_review_bot/
          pip install -r requirements.txt
      
      - name: Run code review
        id: review
        env:
          ANTHROPIC_API_PRACTICE_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          # 获取PR的diff
          codereview --commit ${{ github.event.pull_request.base.sha }}..${{ github.event.pull_request.head.sha }} > review_output.txt 2>&1
          cat review_output.txt
      
      - name: Post review as comment
        if: always()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const reviewOutput = fs.readFileSync('review_output.txt', 'utf8');
            
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '## 🤖 自动代码Review\n\n' + reviewOutput
            });
```

2. **配置secrets**

在GitHub仓库设置中：
- Settings → Secrets and variables → Actions
- 添加 `ANTHROPIC_API_KEY`

3. **验证**

创建一个PR，GitHub Actions会自动运行并发表Review意见。

### 优势
- ✅ 强制执行（pull_request之前必须review）
- ✅ 团队成员都能看到Review结果
- ✅ 完整的审计日志

### 劣势
- ❌ 需要ANTHROPIC API Key配置
- ❌ 依赖网络和API可用性

---

## 方案 3：GitLab CI（CI/CD自动Review）

在GitLab的CI/CD管道中运行Review。

### 步骤

1. **创建CI/CD配置** `.gitlab-ci.yml`

```yaml
code-review:
  image: python:3.13
  
  script:
    - pip install -e project3_code_review_bot/
    - pip install -r requirements.txt
    - codereview --commit ${CI_COMMIT_BEFORE_SHA}..${CI_COMMIT_SHA}
  
  only:
    - merge_requests
  
  variables:
    ANTHROPIC_API_PRACTICE_KEY: $ANTHROPIC_API_KEY
```

2. **配置CI/CD变量**

在GitLab项目设置中：
- Settings → CI/CD → Variables
- 添加 `ANTHROPIC_API_KEY`

---

## 方案 4：Husky + npm (JavaScript项目)

使用Husky和npm scripts自动化JavaScript项目的Review。

### 步骤

```bash
# 安装Husky
npm install husky --save-dev
npx husky install

# 创建pre-push hook
npx husky add .husky/pre-push "codereview --staged"
```

---

## 方案 5：Pre-commit Framework

使用Python的pre-commit框架管理git hooks。

### 步骤

1. **安装pre-commit**

```bash
pip install pre-commit
```

2. **创建配置** `.pre-commit-config.yaml`

```yaml
repos:
  - repo: local
    hooks:
      - id: code-review-bot
        name: Code Review Bot
        entry: codereview
        language: system
        types: [python]
        pass_filenames: false
        stages: [push]
```

3. **安装hooks**

```bash
pre-commit install --hook-type push
```

---

## 对比表

| 方案 | 实施难度 | 强制性 | 实时反馈 | 成本 |
|------|--------|--------|---------|------|
| Pre-Push Hook | ⭐ 简单 | ❌ 否 | ✅ 是 | 免费 |
| GitHub Actions | ⭐⭐ 中等 | ✅ 是 | ⚠️ 数分钟 | $0.35/1000分钟 |
| GitLab CI | ⭐⭐ 中等 | ✅ 是 | ⚠️ 数分钟 | 包含在plan内 |
| Husky | ⭐⭐ 中等 | ❌ 否 | ✅ 是 | 免费 |
| Pre-commit | ⭐ 简单 | ❌ 否 | ✅ 是 | 免费 |

---

## 环境配置

无论使用哪种集成方式，都需要配置LLM后端：

### 使用Ollama（本地，推荐小型团队）

```bash
# 拉取模型
ollama pull qwen3:8b

# 启动server
ollama serve

# .env配置
MODEL=qwen3:8b
OLLAMA_BASE_URL=http://localhost:11434/v1
```

### 使用Anthropic Claude（云端，推荐CI/CD）

```bash
# .env配置
ANTHROPIC_API_PRACTICE_KEY=sk-ant-...
```

---

## 最佳实践

1. **配置Review规则**
   - 定义哪些问题是blocking（不能merge）
   - 定义哪些是warning（需要讨论）

2. **自定义提示词**
   - 根据团队的编码规范调整system prompt
   - 针对特定技术栈做定制（如安全框架、性能要求）

3. **监控和改进**
   - 记录Review历史，识别常见问题
   - 定期更新Review规则，改进提示词

4. **权限控制**
   - 限制谁能跳过Review
   - 记录所有的skip操作

---

## 故障排查

### 问题1: "命令未找到：codereview"

**原因：** 未正确安装项目

**解决：**
```bash
pip install -e project3_code_review_bot/
```

### 问题2: "连接rejected: Ollama/"

**原因：** Ollama server未运行

**解决：**
```bash
ollama serve
# 在另一个终端
ollama run qwen3:8b
```

### 问题3: "ANTHROPIC_API_PRACTICE_KEY not found"

**原因：** 环境变量未配置

**解决：**
```bash
# .env文件中配置
export ANTHROPIC_API_PRACTICE_KEY=sk-ant-...

# 或在GitHub/GitLab中配置secrets
```

---

## 扩展阅读

- [GitHub Actions 官方文档](https://docs.github.com/en/actions)
- [GitLab CI/CD 官方文档](https://docs.gitlab.com/ee/ci/)
- [Pre-commit Framework](https://pre-commit.com/)
- [Husky文档](https://typicode.github.io/husky/)
