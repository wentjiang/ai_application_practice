# AI 应用开发学习路线

> 背景：已有使用 Claude + Agent Skill 开发经验，已能编写自定义 Agent Skill

---

## 一、已掌握的基础能力

- 日常使用 Claude 进行开发辅助
- 调用 Agent Skill 完成任务
- 编写自定义 Agent Skill

---

## 二、下一步学习方向

### 1. Prompt Engineering 深化

当前可能停留在"能用"阶段，进阶方向：

- **Chain-of-Thought (CoT)**：让模型逐步推理，提升复杂任务准确率
- **Few-shot vs Zero-shot**：何时提供示例、如何选择示例
- **System Prompt 设计**：角色定义、约束边界、输出格式控制
- **Prompt 版本管理**：将 prompt 当代码管理，可追溯、可测试
- 推荐资源：[Anthropic Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)

---

### 2. Claude API / Anthropic SDK 进阶

已用过 Agent Skill，但 API 层面可能还有盲区：

- **Messages API** 完整参数：`temperature`、`top_p`、`stop_sequences`、`max_tokens`
- **Streaming**：流式输出实现更好的用户体验
- **Tool Use（Function Calling）**：让模型调用外部工具，这是 Agent 的核心机制
- **Vision**：传入图片/截图进行分析
- **Batch API**：批量处理大量请求，降低成本
- **Token 计算与成本控制**

```python
import anthropic

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    tools=[...],   # Tool Use
    messages=[{"role": "user", "content": "..."}]
)
```

---

### 3. Agent 架构设计

从"写单个 Skill"到"设计 Agent 系统"：

- **ReAct 模式**：Reasoning + Acting，模型思考后决定调用哪个工具
- **多 Agent 协作**：Orchestrator + Sub-agents 分工
- **Agent Memory**：
  - Short-term：对话上下文窗口
  - Long-term：向量数据库 / 外部存储
- **Agent Loop 控制**：何时终止、如何处理错误、防止无限循环
- **Human-in-the-loop**：哪些步骤需要人工确认

---

### 4. RAG（检索增强生成）

让 AI 能访问私有知识库：

- **基本流程**：文档切分 → Embedding → 向量存储 → 检索 → 注入 Prompt
- **Embedding 模型选择**：OpenAI `text-embedding-3`、Cohere、本地模型
- **向量数据库**：Chroma（本地轻量）、Pinecone（云端）、pgvector（PostgreSQL 扩展）
- **Chunking 策略**：固定大小 vs 语义分割，对检索质量影响很大
- **Reranking**：检索后用 Cross-encoder 重新排序，提升相关性

---

### 5. MCP（Model Context Protocol）

已有 MCP.md 文档，可以深入：

- 编写自定义 MCP Server，暴露内部工具给 Claude
- MCP 与 Agent Skill 的边界：何时用 MCP，何时用 Skill
- 常用 MCP Server：文件系统、数据库、Slack、GitHub、Jira 等
- 本地 MCP Server 开发调试

---

### 6. LangChain / LlamaIndex（选学）

社区流行框架，了解其思路但不必深陷：

- LangChain：Chain、Agent、Memory、Retriever 抽象
- LlamaIndex：专注于文档索引和 RAG
- **建议**：先理解它们解决什么问题，用原生 SDK 能做到的就不依赖框架

---

### 7. AI 应用工程化

把 AI 能力变成可靠的生产系统：

- **Evaluation（评估）**：如何测试 AI 输出质量？构建 eval 数据集
- **Observability（可观测性）**：
  - LangSmith / Langfuse：追踪每次 LLM 调用的输入输出、耗时、Token 消耗
- **Guardrails（护栏）**：输出过滤、有害内容检测、结构化输出校验
- **Caching**：语义缓存减少重复调用
- **Rate Limiting & Retry**：处理 API 限流和网络错误

---

### 8. 结构化输出

让模型返回可解析的格式：

- **JSON Mode**：强制模型输出合法 JSON
- **Pydantic + Instructor**：用 Python 类型系统约束输出结构
- **XML 标签技巧**：Claude 对 XML 格式指令理解较好

---

### 9. 本地模型（可选拓展）

了解闭源 API 之外的选项：

- **Ollama**：本地运行 Llama 3、Mistral 等开源模型
- 适合场景：数据隐私要求高、离线环境、降低成本
- 与 Claude API 接口差异对比

---

## 三、推荐学习顺序

```
Tool Use 深化
    ↓
Agent 架构设计（ReAct / Multi-Agent）
    ↓
RAG 基础实现
    ↓
MCP Server 开发
    ↓
AI 应用评估与可观测性
    ↓
结构化输出 + 工程化实践
```

---

## 四、推荐资源

| 资源 | 说明 |
|------|------|
| [Anthropic Docs](https://docs.anthropic.com) | 官方文档，Tool Use / Prompt Engineering |
| [Claude Agent SDK](https://docs.anthropic.com/en/docs/agents) | Agent 构建指南 |
| [deeplearning.ai](https://www.deeplearning.ai/short-courses/) | 免费短课程，RAG / Agent 专题 |
| [Langfuse](https://langfuse.com) | 开源 LLM 可观测性工具 |
| [Instructor](https://github.com/jxnl/instructor) | 结构化输出库 |

---

*最后更新：2026-03-17*
