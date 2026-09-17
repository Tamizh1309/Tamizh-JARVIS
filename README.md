# TAMIZH JARVIS

> **Think. Plan. Execute. Learn.**

**Tamizh JARVIS** is a personal, modular, and secure agentic AI assistant designed for productivity, study, coding, career development, and controlled assistance.

Repository: [https://github.com/Tamizh1309/Tamizh-JARVIS](https://github.com/Tamizh1309/Tamizh-JARVIS)

---

## Architecture Overview

```text
User Input (Text / Voice / API)
              │
              ▼
   TAMIZH JARVIS Core Engine
              │
    ┌─────────┴─────────┐
    │   Intent Router   │  (21 Core Deterministic & AI Intents)
    └─────────┬─────────┘
              ▼
    ┌───────────────────┐
    │ Planner & Scoring │ ◄───► Memory & Persistence (SQLite Async)
    └─────────┬─────────┘
              ▼
    ┌───────────────────┐
    │  Security Layer   │ ────► Permission Gate & Risk Classifier (LOW/MED/HIGH/CRITICAL)
    └─────────┬─────────┘
              ▼
    ┌───────────────────┐
    │   Tool Executor   │ ────► TaskTool, StudyTool, ScheduleTool, CodingTool, ProfileTool
    └─────────┬─────────┘
              ▼
    ┌───────────────────┐
    │  Response Manager │ ────► Clean Synthesis & Telemetry Update
    └───────────────────┘
```

---

## Implementation Status (Phase 4 Verified)

| Component | Status | Verification & Capabilities |
|---|---|---|
| **AI Provider Layer** | ✅ Implemented & Tested | `AUTO`, `GEMINI`, `LOCAL`, `FALLBACK`. Automatic failover, credential masking, timeout/rate-limit shielding. |
| **Chat API (`POST /api/chat`)** | ✅ Implemented & Tested | Returns `{success, intent, action, response, data, toolUsed, memoryUpdated}`. |
| **Intent Router** | ✅ Implemented & Tested | All 21 core intents with deterministic rules, structured entity extraction, and AI fallback. |
| **Task Engine** | ✅ Implemented & Tested | Schema: `(id, title, description, status, priority, created_at, due_at, completed_at, category, source)`. Full CRUD + completion in SQLite. |
| **Long-Term Memory** | ✅ Implemented & Tested | 14 memory domains with SQLite persistence across restarts: `USER_PROFILE`, `GOALS`, `PREFERENCES`, `STUDY_HISTORY`, `TOPIC_MASTERY`, `MISTAKES`, `TASKS`, etc. |
| **Study & GATE Engine** | ✅ Implemented & Tested | Real study session logging, weak topic tracking, GATE CS revision plans, dynamic study hours calculation. |
| **Next Best Action Engine** | ✅ Implemented & Tested | Multi-factor deterministic scoring based on deadlines, weak topics, study history, and career goals. Non-fixed, explainable. |
| **Daily Briefing (`GET /api/study/briefing`)** | ✅ Implemented & Tested | Dynamic calculation from database: active pending tasks, target study hours, completed study hours, completion percentage. |
| **Security & Permissions** | ✅ Implemented & Tested | 4-tier risk classification (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`). Prohibits raw shell execution. Requires confirmation for high-risk actions. |
| **Frontend UI (React + Vite)** | ✅ Implemented & Tested | Dark-first dashboard connected to real backend APIs with `VITE_API_BASE_URL` support. |
| **Automated Test Suite** | ✅ Implemented & Tested | 50 automated tests passing with pytest (`tests/test_*.py`). |

---

## Project Structure

```
Tamizh-JARVIS/
├── backend/
│   ├── ai/
│   │   ├── provider.py            # AIProvider abstract base & factory
│   │   ├── gemini_provider.py     # Hardened Google Gemini 1.5/2.5 client
│   │   ├── local_provider.py      # Ollama/Local REST LLM client
│   │   └── fallback_provider.py   # Resilient offline deterministic engine
│   ├── api/
│   │   ├── chat.py                # POST /api/chat endpoint
│   │   ├── health.py              # GET /api/health endpoint
│   │   ├── tasks.py               # Task CRUD endpoints
│   │   ├── study.py               # Next action & briefing endpoints
│   │   └── memory.py              # Memory query and persistence endpoints
│   ├── core/
│   │   ├── jarvis_core.py         # Master agentic lifecycle orchestrator
│   │   ├── router.py              # 21-intent semantic router
│   │   ├── planner.py             # Multi-step task planner
│   │   ├── decision_engine.py     # Deterministic NBA scoring engine
│   │   ├── context_manager.py     # Session & memory context builder
│   │   └── response_manager.py    # Structured response formatter
│   ├── memory/
│   │   ├── memory_manager.py      # Memory coordinator
│   │   ├── long_term_memory.py    # SQLite async driver (aiosqlite)
│   │   ├── profile_memory.py      # Persistent user goals and profile
│   │   └── conversation_memory.py # Sliding context buffer
│   ├── security/
│   │   ├── permission_manager.py  # Action authorization & confirmation gate
│   │   ├── risk_classifier.py     # 4-tier risk classification
│   │   └── action_validator.py    # Parameter validation & injection guard
│   ├── tools/
│   │   ├── base_tool.py           # Base tool interface
│   │   ├── task_tool.py           # Task management tool
│   │   ├── study_tool.py          # GATE study and weak-topic tool
│   │   ├── coding_tool.py         # DSA & algorithm explanation tool
│   │   ├── profile_tool.py        # Goal setting & career roadmap tool
│   │   ├── progress_tool.py       # Metrics & briefing calculation tool
│   │   └── schedule_tool.py       # Calendar & time-slot tool
│   ├── config/
│   │   └── settings.py            # Pydantic environment configuration
│   └── main.py                    # FastAPI application entrypoint
├── frontend/
│   ├── src/
│   │   ├── App.jsx                # React dashboard with API integration
│   │   ├── index.css              # Futuristic dark-first stylesheet
│   │   └── main.jsx               # React mount entrypoint
│   ├── package.json               # Frontend dependencies
│   └── vite.config.js             # Vite proxy and base URL config
├── tests/
│   ├── test_chat.py               # Chat API & intent verification tests
│   ├── test_router.py             # 21-intent router tests
│   ├── test_planner.py            # Plan formulation tests
│   ├── test_memory.py             # Memory persistence across restarts tests
│   ├── test_tools.py              # Tool execution tests
│   ├── test_security.py            # Risk tiers and injection prevention tests
│   ├── test_study.py               # Study data calculations tests
│   └── test_decision_engine.py    # Scoring engine tests
└── docs/
    ├── ARCHITECTURE.md            # Detailed system design
    ├── API.md                     # REST API reference
    ├── SECURITY.md                # Threat model and security policies
    ├── DEVELOPMENT.md             # Developer setup and testing guide
    └── ROADMAP.md                 # Project milestones
```

---

## Local Run Commands

### 1. Backend Server (FastAPI)
```bash
cd backend
# Create virtual environment if not present
python -m venv .venv
source .venv/bin/activate  # Or on Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run FastAPI with live reload on http://127.0.0.1:8000
python main.py
```

### 2. Frontend Application (React + Vite)
```bash
cd frontend
npm install
npm run dev
# Running on http://localhost:5173 (proxies /api to backend)
```

### 3. Running Test Suites
```bash
# Run pytest with venv python
python -m pytest -q
```

---

## Production Deployment Architecture

- **Frontend (GitHub Pages)**:
  Static production bundle built with `npm run build` is published to the `gh-pages` branch.
  Configure environment variable `VITE_API_BASE_URL=https://<your-backend-domain>` to direct frontend requests to the deployed backend.
- **Backend (Render / Railway / Cloud VPS)**:
  Deploy the FastAPI application using Uvicorn or Docker.
  Set environment variables:
  - `APP_ENV=production`
  - `PORT=8000`
  - `GEMINI_API_KEY=<your-key>`
  - `ALLOWED_ORIGINS=https://tamizh1309.github.io,http://localhost:5173`
