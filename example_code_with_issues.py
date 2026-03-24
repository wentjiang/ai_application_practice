"""示例代码文件 - 包含多个需要Review的问题"""

import sqlite3
import os
from typing import List


class UserManager:
    """用户管理类 - 包含安全和性能问题"""
    
    def __init__(self, db_path: str):
        self.db = sqlite3.connect(db_path)
        self.cursor = self.db.cursor()
    
    
    def get_user_by_username(self, username: str) -> dict:
        """根据用户名获取用户信息 - SQL注入风险"""
        # ❌ 问题：直接字符串拼接，存在SQL注入风险
        query = "SELECT * FROM users WHERE username = '" + username + "'"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return dict(result) if result else None
    
    
    def get_user_posts(self, user_id: int) -> List[dict]:
        """获取用户的所有帖子 - N+1查询问题"""
        # ❌ 问题：N+1 查询 - 先查用户，再逐个查每条帖子的评论
        query = "SELECT * FROM posts WHERE user_id = ?"
        self.cursor.execute(query, (user_id,))
        posts = self.cursor.fetchall()
        
        result = []
        for post in posts:
            # 每条帖子都单独查询一次评论，导致N+1问题
            comment_query = "SELECT * FROM comments WHERE post_id = ?"
            self.cursor.execute(comment_query, (post[0],))
            comments = self.cursor.fetchall()
            result.append({
                "post": post,
                "comments": comments
            })
        
        return result
    
    
    def update_user_password(self, user_id: int, password: str) -> bool:
        """更新用户密码 - 不安全的密码存储"""
        # ❌ 问题：密码明文存储，没有加盐没有hash
        query = "UPDATE users SET password = ? WHERE id = ?"
        self.cursor.execute(query, (password, user_id))
        self.db.commit()
        return True
    
    
    def process_bulk_data(self, data: List[str]) -> None:
        """批量处理数据 - 代码复杂度高"""
        # ❌ 问题：圈复杂度过高，代码冗长难以维护
        for item in data:
            if item.startswith("user"):
                if item[5] == "_":
                    if item[6:10] == "admin":
                        if len(item) > 10:
                            username = item[11:]
                            if username != "":
                                if username.isalpha():
                                    if len(username) < 20:
                                        insert_query = "INSERT INTO users (username) VALUES (?)"
                                        self.cursor.execute(insert_query, (username,))
                                    else:
                                        print("Username too long")
                                else:
                                    print("Invalid username")
                        else:
                            print("Incomplete item")
            elif item.startswith("post"):
                if item[5] == "_":
                    if item[6:10] == "text":
                        if item[11:].strip() != "":
                            post_text = item[11:]
                            insert_post = "INSERT INTO posts (content) VALUES (?)"
                            self.cursor.execute(insert_post, (post_text,))


def get_api_key() -> str:
    """获取API密钥 - 敏感信息泄露"""
    # ❌ 问题：硬编码密钥在代码中，版本控制会泄露敏感信息
    api_key = "sk_live_abc123xyz789def456ghi789"
    return api_key
