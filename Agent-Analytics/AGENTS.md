# Agent-Analytics — Project Context

## Overview
Standalone industrial analytics agent extracted from the industrial-multi-agent monorepo. Uses CrewAI 1.x with Reasoner (manager) + Worker architecture, Ollama/Qwen3 4B LLM.

## Architecture
- `agents/reasoner.py` — Plant Operations Analyst (manager, delegates to worker)
- `agents/worker.py` — Data Processing Engineer (executes tools)
- `tools/*.py` — 9 LangChain tools adapted to CrewAI via tools/adapt.py
- `db/connection.py` — PostgreSQL with SQLite fallback
- `cli.py` — CLI entrypoint (seed, analyze, troubleshoot, serve)
- `main.py` — FastAPI server (/analyze, /troubleshoot, /health)

## CrewAI 1.x Rules
- `llm` param (string) instead of `llm_config` dict
- Use `llm="ollama/qwen3:4b"` format
- Hierarchical: `agents=[worker]`, `manager_agent=reasoner`
- Task has NO `agent=` assigned (leave None)

## Key Commands
```bash
python3 cli.py seed                          # seed DB (once)
python3 cli.py analyze LINE-01 "query"       # free-form analysis
python3 cli.py troubleshoot LINE-03 "issue"  # troubleshooting
python3 cli.py serve                         # FastAPI on :8000
python3 cli.py pipeline drying               # (future) pipeline mode
```

## Environment
- Ollama with qwen3:4b at localhost:11434
- OPENAI_BASE_URL=http://localhost:11434/v1
- OPENAI_API_KEY=ollama

## Data Source
PDC device → InfluxDB (time-series). Schema TBD.

## Files
- `CHAT_SUMMARY.md` — full session log and progress
- `cli.py` — all CLI commands
- `main.py` — FastAPI endpoints
- `tools/adapt.py` — LangChain → CrewAI tool adapter
- `db/connection.py` — dual-mode DB connection
