# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment Setup

Python version is managed via pyenv and locked to **3.13.3** (`.python-version`).

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e project1_cli_assistant/
cp .env.example .env
```

## Project Structure

This is a multi-project monorepo for practicing AI application development. Each project lives in its own subdirectory with its own `pyproject.toml`.

- **project1_cli_assistant/** — A CLI AI assistant using Tool Use + multi-turn conversation (complete)
- Future projects will follow the same pattern (one directory per project)

## Running a Project

```bash
source .venv/bin/activate
assistant
```

**Ollama backend** (default): ensure the model is running first:
```bash
ollama run qwen3:8b
```

**Anthropic backend**: set `ANTHROPIC_API_PRACTICE_KEY` in `.env` — the assistant switches automatically.

## Environment Variables

Configured via `.env` (copied from `.env.example`):

| Variable | Default | Purpose |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434/v1` | Ollama OpenAI-compatible endpoint |
| `MODEL` | `qwen3:8b` | Model name (e.g. `qwen3:8b` for Ollama, `claude-opus-4-6` for Anthropic) |
| `ANTHROPIC_API_PRACTICE_KEY` | — | If set, switches backend to Anthropic Claude API |

## Architecture: Project 1 (CLI Assistant)

`agent.py` selects the backend at import time based on whether `ANTHROPIC_API_PRACTICE_KEY` is set:

- **Anthropic path** (`_run_anthropic`): uses `anthropic.Anthropic` client; converts OpenAI-format tool schemas to Anthropic format; handles `tool_use` blocks and feeds `tool_result` back until `stop_reason == "end_turn"`
- **Ollama path** (`_run_ollama`): uses `openai.OpenAI` client pointed at Ollama; handles `tool_calls` until `finish_reason == "stop"`

Both paths share the same tools layer:

1. `main.py` — REPL entry point, manages the `messages` list across turns, extracts `system` message
2. `agent.py` — dual-backend Tool Use loop
3. `tools.py` — tool schemas (`TOOLS_SCHEMA` in OpenAI format) + handler functions (`run_shell`, `read_file`)

New tools require adding both a schema entry to `TOOLS_SCHEMA` and a handler to `TOOL_HANDLERS` in `tools.py`. The Anthropic schema conversion in `agent.py` happens automatically.

## Planned Projects (doc/practice_projects.md)

Projects follow a learning progression:
1. CLI Assistant (Tool Use) ✅
2. Web Content Summarizer (Tool Use + structured output)
3. Code Review Bot (git diff + Tool Use)
4. Local Document Q&A (RAG: Chroma + embeddings)
5. Knowledge Base + Web UI (RAG + Streamlit + streaming)
6. Weekly Report Agent (Multi-Agent)
7. Tech Research Agent (Multi-Agent + search API)
8. Custom MCP Server
9. AI Output Evaluation Framework
10. Enterprise Knowledge Base Platform (comprehensive)
