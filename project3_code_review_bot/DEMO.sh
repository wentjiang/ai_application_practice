#!/bin/bash
# 代码Review Bot 的演示脚本
# 展示如何在实际工作流中使用codereview命令

echo "========================================"
echo "代码Review Bot 演示"
echo "========================================"
echo ""

# 1. 显示帮助
echo "📚 1. 查看帮助信息"
echo "   Command: codereview --help"
echo ""

# 2. 创建一个有问题的代码文件
echo "📝 2. 创建一个包含安全和性能问题的Python文件"
cat > unsafe_code.py << 'EOF'
import sqlite3

def get_user(user_id: str):
    """获取用户 - 存在SQL注入风险"""
    db = sqlite3.connect(":memory:")
    # ❌ 直接字符串拼接，SQL注入风险
    query = f"SELECT * FROM users WHERE id = {user_id}"
    return db.execute(query).fetchone()

def get_user_posts(user_id: int):
    """获取用户帖子 - N+1查询问题"""
    db = sqlite3.connect(":memory:")
    posts = db.execute("SELECT * FROM posts WHERE user_id = ?", (user_id,)).fetchall()
    
    result = []
    # ❌ N+1查询：每条帖子都单独查询一次
    for post in posts:
        comments = db.execute("SELECT * FROM comments WHERE post_id = ?", (post[0],)).fetchall()
        result.append({"post": post, "comments": comments})
    return result
EOF
echo "   Created: unsafe_code.py"
echo ""

# 3. 舞台代码进行review
echo "🔄 3. 将代码加入git暂存区"
echo "   Command: git add unsafe_code.py"
echo ""

# 4. 运行review
echo "🔍 4. 运行代码Review"
echo "   Command: codereview --staged"
echo ""
echo "   说明："
echo "   - 如果使用Ollama，需要先启动: ollama run qwen3:8b"
echo "   - 如果使用Anthropic，需要设置: ANTHROPIC_API_PRACTICE_KEY=sk-ant-..."
echo ""

# 5. 查看输出示例
echo "📋 5. Review输出示例（什么时候会看到）："
cat << 'EOF'
============================================================
代码Review Bot（qwen3:8b）
============================================================

🔍 正在分析代码变动...

## 代码Review报告

### 🔒 安全问题 (严重度: 高)
**问题1: SQL注入漏洞**
- 位置: 第5行
- 描述: 直接拼接用户输入到SQL语句中，攻击者可以执行任意SQL代码
- 建议: 使用参数化查询（prepared statements）
- 示例代码:
  ```python
  # 修复前
  query = f"SELECT * FROM users WHERE id = {user_id}"
  
  # 修复后
  query = "SELECT * FROM users WHERE id = ?"
  db.execute(query, (user_id,))
  ```

### ⚡ 性能问题 (严重度: 中)
**问题1: N+1查询问题**
- 位置: 第12-15行
- 描述: 整体查询N条记录，然后为每条记录单独查询，导致N+1次数据库往返
- 建议: 使用JOIN或批量查询来优化
- 示例代码:
  ```python
  # 修复前
  for post in posts:
      comments = db.execute("SELECT * FROM comments WHERE post_id = ?", (post[0],)).fetchall()
  
  # 修复后
  comments = db.execute("""
      SELECT c.* FROM comments c
      JOIN posts p ON p.id = c.post_id
      WHERE p.user_id = ?
  """, (user_id,)).fetchall()
  ```

### ✅ 总结
- 总体评分: 5/10
- 主要关注项: 必须修复SQL注入安全漏洞再发布
- 是否可发布: 否 (需要修复上述2个问题)
============================================================
EOF
echo ""
echo ""

echo "📖 6. 更多用法："
echo "   审查未提交的所有改动:"
echo "     codereview"
echo ""
echo "   审查与上一个提交的差异:"
echo "     codereview --commit HEAD~1"
echo ""
echo "   审查两个提交之间的差异:"
echo "     codereview --commit main..feature-branch"
echo ""

# 清理
echo "🧹 7. 清理演示文件"
echo "   rm -f unsafe_code.py"
echo ""

echo "✅ 演示完成！"
