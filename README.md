# Tamizh JARVIS — Personal Agentic AI Assistant

[![CI/CD Suite & Agent Validation](https://github.com/Tamizh1309/Tamizh-JARVIS/actions/workflows/ci.yml/badge.svg)](https://github.com/Tamizh1309/Tamizh-JARVIS/actions/workflows/ci.yml)
[![Live Dashboard](https://img.shields.io/badge/Live-GitHub%20Pages-00f2fe)](https://tamizh1309.github.io/Tamizh-JARVIS/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776ab)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61dafb)](https://react.dev)

> **Tagline:** Think. Plan. Execute. Learn.

Tamizh JARVIS is a personal agentic artificial intelligence system designed for engineering productivity, GATE CS preparation, algorithmic coding mastery, and career roadmap execution.

---

## Current Architecture & Capabilities (Phase 7 Production-Ready)

| Subsystem | Status | Implementation Details |
|---|---|---|
| **JarvisCore Engine** | `[IMPLEMENTED]` | 5-stage lifecycle (`Thinking` → `Planning` → `Verifying` → `Executing` → `Responding`) with stable structured JSON schema. |
| **Tool Registry** | `[IMPLEMENTED]` | 6 active tools (`task_tool`, `study_tool`, `schedule_tool`, `progress_tool`, `profile_tool`, `coding_tool`) validated via automated test suite. |
| **Deterministic Next Best Action** | `[IMPLEMENTED]` | Multi-factor mathematical scoring evaluating deadline urgency, goal relevance, weakness priority, and available time. |
| **Memory Classification** | `[IMPLEMENTED]` | Domain-classified storage across `USER_PROFILE`, `GOAL`, `PREFERENCE`, `TASK`, `STUDY`, `ACHIEVEMENT`, `MISTAKE`, `REVISION`, `CONVERSATION_CONTEXT`. |
| **SQLite Persistence** | `[IMPLEMENTED]` | Asynchronous database driver (`aiosqlite`) persisting tasks, study sessions, and memory across restarts. |
| **Personalized Coding Assistant** | `[IMPLEMENTED]` | Dynamic DSA plans filtered by weak topics, AST/AI code debugging with fixes/complexity, and production code review. |
| **Security Gates** | `[IMPLEMENTED]` | 4-tier risk classification (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), parameter sanitization, and shell injection blocking. |
| **Futuristic Dashboard** | `[IMPLEMENTED]` | Cyberpunk HUD interface in React + Vite with real-time telemetry, agent state transitions, and live backend connection. |

---

## End-to-End Verification

JARVIS supports natural language interaction across all core workflows:
1. **Career Goals:** `"My career goal is to become a Software Engineer."` → Persisted to SQLite.
2. **Goal Retrieval:** `"What is my career goal?"` → Dynamically loaded from database.
3. **Task Engine:** `"Create a task to solve 3 LeetCode problems today."` → SQLite record created.
4. **Task Listing:** `"List my pending tasks."` → Backlog rendered with priorities.
5. **Next Best Action:** `"What should I study now?"` → Evaluated dynamically via DecisionEngine.
6. **Study Logging:** `"Log 45 minutes of DBMS Transactions study."` → Saved in `study_sessions`.
7. **Weak Topics:** `"What are my weak topics?"` → Spaced repetition retention tracker.
8. **GATE Revision:** `"Plan my GATE revision."` → 3-block 90-minute structured revision.
9. **DSA Practice:** `"Give me DSA practice."` → Pattern-based problem solving recommendations.
10. **Algorithm Explanation:** `"Explain binary search."` → Intuition, time/space complexity, and code.

---

## Local Development & Testing

```bash
# 1. Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# 2. Run automated test suite
pytest -q

# 3. Start Backend Server
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# 4. Start Frontend
cd frontend && npm run dev
```

---

## License

MIT License. Copyright (c) 2026 Tamizharasan E.
