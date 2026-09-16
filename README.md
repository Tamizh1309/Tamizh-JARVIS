# TAMIZH JARVIS

> **Think. Plan. Execute. Learn.**

**Tamizh JARVIS** is a personal, modular, and secure agentic AI assistant designed for productivity, study, coding, career development, and controlled computer assistance.

---

## Key Features

- **AI Brain & Agentic Loop**: Autonomous reasoning with explicit steps: *Understand -> Think -> Plan -> Decide -> Select Tool -> Permission Check -> Execute -> Verify -> Remember -> Respond*.
- **Next Best Action Engine**: Deterministic and transparent decision engine that analyzes deadlines, priority, and recent performance to recommend what to do next.
- **Hierarchical Memory**: Fast in-memory working context paired with SQLite persistent storage for user profile, goals, mistakes, topic mastery, and study progress.
- **Pluggable AI Provider**: Works seamlessly with Google Gemini, local models (Ollama), or an offline fallback provider with zero external dependencies.
- **Enterprise Security Model**: Strict 4-tier risk classification (LOW, MEDIUM, HIGH, CRITICAL) with mandatory confirmation gates for sensitive actions. No direct LLM shell execution.
- **Study & GATE/DSA Intelligence**: Dedicated engines for GATE preparation, revision scheduling, and weak-topic tracking.
- **Futuristic Dark-First Dashboard**: Modern, clean, responsive UI built with React, styled with Vanilla CSS and subtle micro-animations.

---

## Architecture Overview

```text
User Input (Text / Voice)
          │
          ▼
    TAMIZH JARVIS Core Engine
          │
┌─────────┴─────────┐
│   Intent Router   │
└─────────┬─────────┘
          ▼
┌───────────────────┐
│ Planner & Decision│ ◄── Active Memory & Context
└─────────┬─────────┘
          ▼
┌───────────────────┐
│ Permission System │ ──► Risk Classifier (LOW / MEDIUM / HIGH / CRITICAL)
└─────────┬─────────┘
          ▼
┌───────────────────┐
│   Tool Executor   │ ──► TaskTool, StudyTool, ScheduleTool, WebTool...
└─────────┬─────────┘
          ▼
┌───────────────────┐
│ Verify & Remember │ ──► Short-Term Context & Long-Term SQLite Storage
└─────────┬─────────┘
          ▼
    Response & UI Update
```

---

## Quick Start

### Prerequisites
- **Python 3.10+** (Tested on Python 3.14 & 3.10)
- **Node.js 18+** & **npm**

### 1. Clone & Configure
```bash
git clone https://github.com/Tamizh1309/tamizh-jarvis.git
cd tamizh-jarvis
cp .env.example .env
```
Edit `.env` to configure `GEMINI_API_KEY` (optional if using local or offline fallback).

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## Documentation

- [Architecture Guide](docs/ARCHITECTURE.md)
- [Roadmap & Milestones](docs/ROADMAP.md)
- [Security Model](docs/SECURITY.md)
- [API Reference](docs/API.md)
- [Development Guide](docs/DEVELOPMENT.md)

---

## License

Distributed under the [MIT License](LICENSE).
