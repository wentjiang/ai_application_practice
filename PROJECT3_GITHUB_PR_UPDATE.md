# GitHub PR Review 功能更新总结

## 🎉 新增功能

你现在可以直接使用 `codereview` 命令来Review **任何GitHub PR**，无需克隆代码到本地！

## ✨ 快速示例

```bash
# Review一个真实的PR - 完整URL格式
codereview --pr https://github.com/numpy/numpy/pull/25000

# 或使用简短格式
codereview --pr numpy/numpy/25000

# 立即获得结构化的Review报告
```

## 📝 核心改动

### 1. **新增工具：`get_github_pr_diff`** 

在 `code_reviewer/tools.py` 中添加了新的工具函数：

```python
def get_github_pr_diff(pr_url_or_path: str) -> str:
    """获取GitHub PR的diff内容"""
    # ✅ 支持完整URL: https://github.com/owner/repo/pull/123
    # ✅ 支持简短格式: owner/repo/123
    # ✅ 调用GitHub API自动获取diff
    # ✅ 支持GITHUB_TOKEN来提高API速率限制
```

**功能特性：**
- 自动解析GitHub PR URL
- 调用GitHub API获取完整diff
- 支持公开和私有仓库（需要token）
- 错误处理和友好的错误提示
- 自动截断超大diff（>100KB）

### 2. **CLI参数扩展**

在 `code_reviewer/main.py` 中添加了新参数：

```bash
codereview --pr <PR_URL_OR_PATH>
```

**支持的格式：**
- 完整URL: `https://github.com/owner/repo/pull/123`
- 简短格式: `owner/repo/123`

**互斥性检查：**
- `--pr`、`--staged`、`--commit` 参数互斥，一次只能使用一个

### 3. **依赖更新**

在 `pyproject.toml` 中添加了依赖：

```toml
dependencies = [
    "openai>=1.0.0",
    "anthropic>=0.40.0",
    "python-dotenv>=1.0.0",
    "requests>=2.32.0",  # ← 新增用于GitHub API调用
]
```

## 📚 新增文档

### [GITHUB_PR_REVIEW.md](./GITHUB_PR_REVIEW.md)

**详细介绍以下内容：**
- ✅ 快速开始（2种格式）
- ✅ 工作原理和流程图
- ✅ 避免API速率限制的方法
- ✅ 处理大型PR的方式
- ✅ 完整的故障排查指南
- ✅ 本地Review vs GitHub PR Review对比
- ✅ CI/CD集成示例
- ✅ 常见问题解答
- ✅ 未来计划

**推荐首次使用GitHub功能时查看！**

## 🔧 配置建议

### 可选（但推荐）：配置GITHUB_TOKEN

GitHub API 有速率限制，配置token可以提高限制：

```bash
# 1. 在GitHub创建Personal Access Token
#    访问：https://github.com/settings/tokens
#    选择 "repo" 权限即可

# 2. 添加到 .env 文件
echo "GITHUB_TOKEN=ghp_your_token_here" >> .env

# 3. 重新运行 - 现在有5000次/小时的限制
codereview --pr owner/repo/123
```

## 🎯 使用场景

### ✅ 场景1：快速Review他人PR（无需克隆）

```bash
# 同事问："你能帮我Review这个PR吗？"
# 你直接运行：
codereview --pr https://github.com/company/project/pull/456

# 5秒内得到详细的安全、性能、规范分析
```

### ✅ 场景2：审查开源项目PR

```bash
# 关注一个开源项目，想参与贡献
# 直接Review PR看看有没有遗漏的地方
codereview --pr torchvision/vision/pulls/7200

# 学习他们的最佳实践
```

### ✅ 场景3：CI/CD中自动Review

```yaml
# GitHub Actions工作流
- name: Review PRs
  run: codereview --pr ${{ github.repository }}/${{ github.event.number }}
```

## 🚀 工作流程

```
用户输入 PR 链接
     ↓
[解析] → 提取 owner/repo/pr_number
     ↓
[调用GitHub API] → 获取PR的diff
     ↓
[解析] → 提取PR标题、作者、描述
     ↓
[发送给Claude] → 智能分析三个维度
     ↓
[格式化输出] → 结构化Review报告
     ↓
用户查看结果
```

## 📊 功能对比表

| 功能 | 本地Git | GitHub PR（新） |
|------|--------|-----------------|
| 审查本地改动 | ✅ 是 | ❌ 否 |
| 审查GitHub PR | ❌ 否 | ✅ 是 |
| 需要克隆仓库 | ✅ 是 | ❌ 否 |
| 公开仓库 | ✅ 可 | ✅ 可 |
| 私有仓库 | ✅ 可 | ⚠️ 需token |
| 跨仓库Review | ❌ 否 | ✅ 可 |
| 速度 | 快 | 中等（API） |
| Token需求 | 无 | 可选 |

## ⚠️ 限制和注意事项

### GitHub API限制

- **速率限制**：未认证 60次/小时，已认证 5000次/小时
- **Diff大小**：最大100KB（超出会截断）
- **可访问性**：只能访问公开仓库（私有需token）

### 隐私考虑

⚠️ 使用GitHub PR Review时：
- PR diff会被发送到Claude API进行分析
- 如果使用Anthropic Claude后端，这意味着代码会上传到Anthropic服务器
- 如果使用Ollama本地后端，diff会在本地处理（更私密）

**隐私等级：** `Local Git > Ollama (PR) > Anthropic (PR)`

## 🔐 安全建议

1. **生成Limited Token**
   - 只给予 `repo` 权限（不需要更多）
   - 定期轮换token
   - 不要提交token到git中

2. **保护敏感代码**
   - 不要Review包含密钥/密码的PR
   - 考虑使用Ollama本地后端处理敏感代码

3. **.env文件安全**
   - 在 `.gitignore` 中添加 `.env`
   - 避免提交 GITHUB_TOKEN

## 📖 文档导航

| 文档 | 用途 |
|------|------|
| **README.md** | 项目总体介绍，包含新功能说明 |
| **GITHUB_PR_REVIEW.md** | 📍 GitHub PR Review 详细指南 |
| **QUICKSTART.md** | 5分钟快速上手 |
| **INTEGRATION.md** | CI/CD集成方案 |

## 🎓 学习价值

通过这个功能扩展，你学到了：

✅ **HTTP API集成** — 调用GitHub API
✅ **错误处理** — 网络请求、超时、速率限制处理  
✅ **CLI参数设计** — 支持多种输入格式
✅ **Real-world工程** — 处理公开和私有资源

## 🚀 未来扩展方向

可以进一步扩展支持：

- [ ] GitLab MR Review
- [ ] Gitee PR Review
- [ ] Bitbucket PR Review
- [ ] 批量Review多个PR
- [ ] 自动在PR上发表Review评论
- [ ] Review历史记录和报告生成

## ✅ 检查清单

- [x] 新增 `get_github_pr_diff` 工具
- [x] 工具schema添加到TOOLS_SCHEMA
- [x] 工具handler添加到TOOL_HANDLERS
- [x] CLI支持 `--pr` 参数
- [x] 参数互斥性检查
- [x] GITHUB_PR_REVIEW.md 详细文档
- [x] README.md 更新
- [x] pyproject.toml 添加requests依赖
- [x] 错误处理和用户提示
- [x] 支持多种输入格式

## 💡 快速命令参考

```bash
# 查看帮助
codereview --help

# 本地Review（原有功能）
codereview                     # 未提交改动
codereview --staged            # 已暂存改动
codereview --commit HEAD~1     # 特定提交

# GitHub PR Review（新功能！）
codereview --pr https://github.com/owner/repo/pull/123
codereview --pr owner/repo/123

# 配置token（可选但推荐）
export GITHUB_TOKEN="ghp_..."
codereview --pr owner/repo/123
```

---

**准备好了吗？** 👉 [查看GitHub PR Review详细指南](./GITHUB_PR_REVIEW.md)
