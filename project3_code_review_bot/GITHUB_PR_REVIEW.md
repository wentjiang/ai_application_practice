# GitHub PR Review 功能指南

## 🆕 新增功能

现在你可以直接使用 `codereview` 命令来Review GitHub PR，无需克隆代码到本地！

## 快速开始

### 方式1：使用完整PR URL

```bash
codereview --pr https://github.com/owner/repo/pull/123
```

### 方式2：使用简短格式

```bash
codereview --pr owner/repo/123
```

## 使用示例

### 示例1：Review一个真实的PR

```bash
codereview --pr numpy/numpy/25000
```

## 工作原理

1. **解析PR链接** — 提取 GitHub URL 中的仓库信息和PR编号
2. **获取PR Diff** — 调用 GitHub API 获取 PR 的完整代码变动
3. **上传给Claude** — 将 diff 发送给 Claude 进行智能分析
4. **生成Review** — 返回安全、性能、规范三个维度的Review意见

```
用户输入PR链接
       ↓
[tools.py] → get_github_pr_diff()
       ↓
GitHub API → 获取PR diff
       ↓
Claude → 智能分析
       ↓
[main.py] → 格式化输出
       ↓
Review报告输出
```

## 高级用法

### 避免API速率限制

GitHub API 有速率限制：
- 匿名请求：60次/小时
- 已认证请求：5000次/小时

如果你频繁使用，建议配置 `GITHUB_TOKEN`：

```bash
# 1. 在 GitHub 生成 Personal Access Token
#    访问：https://github.com/settings/tokens
#    选择 "repo" 权限即可

# 2. 添加到 .env 文件
echo "GITHUB_TOKEN=ghp_your_token_here" >> .env

# 3. 重新运行
codereview --pr owner/repo/123
```

### 处理大型PR

如果PR包含大量代码变动，Review Bot 会自动截断 diff 以保持合理的上下文大小：

```
... (diff过大，仅显示前 100000 个字符)
```

## 故障排查

### 问题1：找不到PR

```
[错误] PR不存在: owner/repo/123
```

**原因：** PR编号或repo名称错误

**解决：** 确认PR链接正确

### 问题2：请求被限制

```
[错误] 请求被限制。建议在.env中设置 GITHUB_TOKEN=your_token ...
```

**原因：** 触发了GitHub API的速率限制

**解决：** 配置 GITHUB_TOKEN (见上方)

### 问题3：网络连接失败

```
[错误] 网络连接失败。请检查网络连接和GitHub API是否可访问。
```

**原因：** 网络问题或无法访问GitHub

**解决：** 检查网络连接

## 对比：本地Review vs GitHub PR Review

| 方式 | 本地Review | GitHub PR Review |
|------|-----------|-----------------|
| 命令 | `codereview` | `codereview --pr url` |
| 需要本地repo | ✅ 是 | ❌ 否 |
| 速度 | 快 | 中等（API调用） |
| 跨仓库Review | ❌ 否 | ✅ 可以Review任何公开repo |
| 隐私性 | ✅ 本地 | ⚠️ 发送到GitHub API再到Claude |

## 技术细节

### 支持的GitHub URL格式

✅ 支持以下格式：
- `https://github.com/owner/repo/pull/123`
- `https://github.com/owner/repo/pull/123/`
- `https://github.com/owner/repo/pull/123#discussion_r123456`
- `owner/repo/123` (简短格式)

❌ 不支持：
- `github.com/owner/repo/pull/123` (缺少https://)
- `owner/repo` (缺少PR编号)

### API Endpoints

内部使用的GitHub API endpoints：

```
GET https://api.github.com/repos/{owner}/{repo}/pulls/{number}
GET https://github.com/{owner}/{repo}/pull/{number}.diff
```

### 限制

- ⚠️ 只能Review **公开仓库** 的PR
- ⚠️ 对于私有仓库，需要提供有效的 GITHUB_TOKEN（并且token要有 `repo` 权限）
- ⚠️ PR diff 大小限制在 100KB（超过会截断）

## 与CI/CD集成

在CI/CD流程中使用GitHub PR Review：

### GitHub Actions 示例

```yaml
name: Review PRs
on:
  pull_request:

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install code-review-bot
        run: pip install -e .
      
      - name: Review this PR
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          codereview --pr ${{ github.repository }}/${{ github.event.pull_request.number }}
```

## 常见问题

### Q: 能Review私有仓库的PR吗？

**A:** 可以，需要：
1. 生成有 `repo` 权限的 Personal Access Token
2. 在 `.env` 中配置 `GITHUB_TOKEN`

### Q: Review结果会被保存吗？

**A:** 不会。结果在终端显示后就消失了。如果需要保存，请手动复制或重定向到文件：

```bash
codereview --pr owner/repo/123 > review_result.txt
```

### Q: 为什么Review某个PR很慢？

**A:** 可能的原因：
- GitHub API 响应缓慢
- PR 包含大量代码变动
- LLM（Claude/Ollama）处理缓慢

### Q: 支持GitLab、Gitee等其他平台吗？

**A:** 当前只支持GitHub。如果你需要支持其他平台，欢迎提交PR或issue！

## 未来计划

🚀 未来可能会支持：
- [ ] GitLab MR Review
- [ ] Gitee PR Review  
- [ ] Bitbucket PR Review
- [ ] 批量Review多个PR
- [ ] 自动在PR上发表Review评论
- [ ] 保存Review历史

## 相关文档

- [QUICKSTART.md](./QUICKSTART.md) — 快速开始指南
- [README.md](./README.md) — 项目详细说明
- [INTEGRATION.md](./INTEGRATION.md) — 集成方案
