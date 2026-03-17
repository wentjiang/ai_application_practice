# AI 应用实践项目清单

> 对应 learning_roadmap.md，从易到难，每个项目都能练到核心技能

---

## 第一阶段：Tool Use + Agent 基础

### 项目 1：命令行 AI 助手（增强版）
**练习技能：** Tool Use、多轮对话、System Prompt 设计

**做什么：**
让 Claude 能执行本地命令行操作，比如：
- 查看当前目录文件，回答"哪个文件最大"
- 执行 git 操作（git log 总结、自动写 commit message）
- 查询天气/时间等

**核心实现：**
```python
tools = [
    {"name": "run_shell", "description": "执行shell命令", ...},
    {"name": "read_file", "description": "读取文件内容", ...},
]
# Claude 决定调用哪个工具，你执行并返回结果
```

**难度：** ⭐⭐
**预计时间：** 1–2 天

---

### 项目 2：网页内容总结 Bot
**练习技能：** Tool Use、Prompt Engineering、结构化输出

**做什么：**
输入一个 URL，自动抓取网页内容，输出：
- 三句话摘要
- 关键观点（bullet points）
- 打分（1–10，是否值得精读）

**扩展：** 批量处理一组 URL，生成每日阅读简报

**难度：** ⭐⭐
**预计时间：** 1 天

---

### 项目 3：自动化代码 Review Bot
**练习技能：** Tool Use、Prompt Engineering、实际工程应用

**做什么：**
- 读取 git diff 内容
- 让 Claude 按固定格式输出 Review 意见（安全问题、性能问题、代码规范）
- 可以做成 pre-push hook 或 GitHub Action

**为什么练这个：** 这是国内很多公司真实在用的 AI 应用场景，做出来可以直接放简历

**难度：** ⭐⭐⭐
**预计时间：** 2–3 天

---

## 第二阶段：RAG 系统

### 项目 4：本地文档问答系统
**练习技能：** RAG 全流程、向量数据库、Embedding

**做什么：**
把一堆 PDF/Markdown 文档（比如你自己的笔记、技术文档）导入，然后用自然语言提问：
- "XXX 技术的优缺点是什么？"
- "我之前记录过 Flink 的配置是怎么写的？"

**技术栈：**
```
文档解析：pypdf / markdownify
Embedding：OpenAI text-embedding-3-small 或 本地 bge-m3
向量存储：Chroma（最简单，纯本地）
检索 + 生成：Claude Messages API
```

**难度：** ⭐⭐⭐
**预计时间：** 3–5 天

---

### 项目 5：个人知识库 + 对话界面
**练习技能：** RAG + Web UI + Streaming 输出

**在项目 4 基础上加：**
- 用 Streamlit 或 Gradio 做一个简单 Web 界面
- 支持流式回复（打字机效果）
- 显示参考来源（引用了哪个文档的哪一段）

**难度：** ⭐⭐⭐
**预计时间：** 3–5 天（在项目 4 之上）

---

## 第三阶段：Multi-Agent 系统

### 项目 6：自动写周报 Agent
**练习技能：** Multi-Agent、Tool Use、实际业务价值

**做什么：**
- Agent 1（数据收集）：读取 git commit 记录、日历事件、笔记文件
- Agent 2（写作）：根据收集的信息，按模板生成周报草稿
- Agent 3（润色）：检查格式、补充细节、调整语气

**扩展：** 自动发送到钉钉/飞书群

**为什么练这个：** Multi-Agent 的标准范式，编排 + 专注角色分工

**难度：** ⭐⭐⭐⭐
**预计时间：** 3–5 天

---

### 项目 7：技术调研 Agent
**练习技能：** Multi-Agent、搜索工具集成、报告生成

**做什么：**
输入一个技术问题（比如"选 Kafka 还是 RocketMQ"），Agent 自动：
1. 搜索最新资料（调用搜索 API）
2. 抓取关键文章内容
3. 对比分析，生成结构化报告（Markdown）
4. 给出推荐结论和理由

**工具：** Tavily Search API（专为 AI Agent 设计的搜索 API）

**难度：** ⭐⭐⭐⭐
**预计时间：** 3–5 天

---

## 第四阶段：MCP Server

### 项目 8：自定义 MCP Server
**练习技能：** MCP 协议开发、工具暴露

**做什么（选一个）：**

**选项 A：本地数据库 MCP**
暴露本地 SQLite 数据库给 Claude，可以用自然语言查询数据

**选项 B：笔记系统 MCP**
把你的 Markdown 笔记目录暴露给 Claude，支持搜索、创建、更新笔记

**选项 C：工作流 MCP**
暴露常用工作脚本（跑测试、构建项目、查日志）给 Claude 调用

**难度：** ⭐⭐⭐
**预计时间：** 2–3 天

---

## 第五阶段：工程化实践

### 项目 9：AI 输出评估框架
**练习技能：** Evaluation、质量保障

**做什么：**
为你之前某个项目（比如项目 4 的 RAG）建立评估体系：
- 准备 20–30 个测试问题 + 标准答案
- 自动批量运行，计算准确率
- 对比不同 Prompt / 不同 Chunk 策略的效果差异
- 用 Langfuse 记录每次调用的详细数据

**为什么练这个：** 这是 AI 应用工程师区别于"玩具级"开发者的核心能力

**难度：** ⭐⭐⭐
**预计时间：** 2–3 天

---

## 综合项目（可以作为简历主打）

### 项目 10：企业知识库问答平台（mini 版）
**覆盖技能：** RAG + Multi-Agent + Web UI + Eval + 可观测性

**功能：**
- 上传文档（PDF/Word/Markdown）
- 自然语言问答，返回答案 + 来源引用
- 对话历史记录
- 管理员界面：查看每次调用日志、Token 消耗
- 一键导出对话为 Markdown 报告

**技术栈建议：**
```
后端：Python + FastAPI
前端：Streamlit 或 Next.js（简单版用 Streamlit）
向量库：Chroma
LLM：Claude API（或同时支持通义千问，练习多模型兼容）
可观测：Langfuse
```

**难度：** ⭐⭐⭐⭐⭐
**预计时间：** 2–3 周

---

## 推荐练习顺序

```
项目 1（Tool Use 入门）
    ↓
项目 3（代码 Review，有实际价值）
    ↓
项目 4（RAG 基础）
    ↓
项目 5（RAG + UI，可以展示）
    ↓
项目 6 或 7（Multi-Agent）
    ↓
项目 8（MCP Server）
    ↓
项目 9（Eval，工程化思维）
    ↓
项目 10（综合，简历主打）
```

---

## 工具/资源

| 工具 | 用途 | 链接 |
|------|------|------|
| Chroma | 本地向量数据库 | pip install chromadb |
| Streamlit | 快速搭建 AI Web UI | pip install streamlit |
| Langfuse | LLM 调用可观测 | langfuse.com（有免费版） |
| Tavily | Agent 专用搜索 API | tavily.com（有免费额度） |
| Instructor | 结构化输出 | pip install instructor |
| pypdf | PDF 解析 | pip install pypdf |

---

*最后更新：2026-03-17*
