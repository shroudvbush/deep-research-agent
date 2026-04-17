# Deep Research Agent

An AI-powered automated deep research assistant that transforms any research topic into a structured report through intelligent task planning, multi-source search, summarization, and synthesis.

## Features

- **Intelligent Task Planning** — LLM automatically decomposes research topics into 3-7 actionable sub-tasks
- **Multi-Source Search** — Aggregates information from diverse web sources
- **Real-Time Progress** — SSE streaming delivers live research progress updates
- **Structured Reports** — Generates formatted Markdown reports with sections, references, and key findings
- **History Management** — SQLite-backed persistent storage with category filtering and report export
- **Real-Time Card Sync** — Card counts update incrementally as each sub-task completes

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Vue 3 + TypeScript + Vite |
| Backend | FastAPI (Python) |
| AI | OpenAI-compatible API (DeepSeek V3, GPT-4o, etc.) |
| Storage | SQLite |
| Communication | Server-Sent Events (SSE) |

## Architecture

```
researcher.py ──► PlanningService ──► [Task 1] ──► SearchService ──► SummarizationService
                                 └─► [Task 2] ──► SearchService ──► SummarizationService
                                 └─► [Task N] ──► ... ──► ReportingService ──► Report
```

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/your-username/deep-research-agent.git
cd deep-research-agent

# Backend
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your LLM API key

# Frontend
cd ../frontend
npm install
```

### 2. Start Services

Double-click `start.bat` or run manually:

```bash
# Terminal 1 — Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

Then open **http://localhost:5173** in your browser.

## Environment Variables

```env
# .env (backend/)
LLM_API_KEY=your_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
SEARCH_PROVIDER=duckduckgo
TAVILY_API_KEY=
```

> **Note:** Without an API key, the system runs in demo mode with a built-in fallback task planner.

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/research/stream` | POST | SSE streaming research endpoint |
| `/research/history` | GET | List research history |
| `/research/history/{id}` | GET | Get single record |
| `/research/history/{id}` | DELETE | Delete a record |
| `/health` | GET | Health check |

### SSE Events

```
research_started → planning_started → planning_completed
→ task_started → task_completed (×N) → task_saved (×N)
→ report_started → report_completed → research_finished
```

## License

MIT
