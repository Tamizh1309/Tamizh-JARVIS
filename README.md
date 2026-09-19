# Tamizh JARVIS — Personal Agentic AI Assistant (Release Candidate v1.0.0)

[![CI/CD Pipeline](https://github.com/Tamizh1309/Tamizh-JARVIS/actions/workflows/deploy.yml/badge.svg)](https://github.com/Tamizh1309/Tamizh-JARVIS/actions/workflows/deploy.yml)
[![Live Dashboard](https://img.shields.io/badge/Live-GitHub%20Pages-00f2fe)](https://tamizh1309.github.io/Tamizh-JARVIS/)
[![Backend Tests](https://img.shields.io/badge/Tests-98%20Passed%20(100%25)-brightgreen)](https://github.com/Tamizh1309/Tamizh-JARVIS)
[![Python](https://img.shields.io/badge/Python-3.11+-3776ab)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61dafb)](https://react.dev)

> **Tagline:** Think. Plan. Execute. Learn.

Tamizh JARVIS is a personal agentic artificial intelligence system designed for engineering productivity, GATE CS preparation, algorithmic coding mastery, and career roadmap execution.

---

## Release Candidate Architecture (Phase 9)

| Subsystem | Status | Details |
|---|---|---|
| **JarvisCore Engine** | ✅ IMPLEMENTED | 5-stage lifecycle (`Thinking` → `Planning` → `Verifying` → `Executing` → `Responding`) with guaranteed schema consistency. |
| **Tool Registry** | ✅ IMPLEMENTED | 6 registered tools (`task_tool`, `study_tool`, `schedule_tool`, `progress_tool`, `profile_tool`, `coding_tool`) validated across all 22 system intents. |
| **DecisionEngine (Next Best Action)** | ✅ IMPLEMENTED | Multi-factor mathematical scoring supporting Scenarios A through E (No Data, Urgent Task, Weak Topic, Revision Overdue, Target Completed). |
| **Memory & Profile Isolation** | ✅ IMPLEMENTED | Domain-scoped storage across `USER_PROFILE`, `GOAL`, `PREFERENCE`, `TASK`, `STUDY`, `ACHIEVEMENT`, `MISTAKE`, `REVISION`; short-term conversational context isolated from long-term records. |
| **SQLite Persistence** | ✅ IMPLEMENTED | Asynchronous database driver (`aiosqlite`) with automated schema migrations for seamless backward compatibility. |
| **AI Providers & Key Masking** | ✅ IMPLEMENTED | Robust `AUTO` mode selecting between `GeminiProvider`, `LocalProvider`, and deterministic `FallbackProvider`; credentials strictly masked in logs. |
| **Security Gates** | ✅ IMPLEMENTED | 4-tier risk classification (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`), parameter sanitization, injection detection, and blocked shell tools. |
| **Coding Assistant** | ✅ IMPLEMENTED | Static AST code inspection, algorithm explanations, and DSA plans without false claims of execution. |
| **Cyberpunk HUD Dashboard** | ✅ IMPLEMENTED | High-performance React 19 + Vite dashboard with live telemetry, configurable API endpoint, and clean build. |
| **CI/CD Pipeline** | ✅ IMPLEMENTED | GitHub Actions pipeline running Python backend pytest suite before building frontend and deploying to GitHub Pages. |

---

## Verification & Automated Testing

The complete test suite runs synchronously with **98 passing tests** and **0 failures**:

```bash
# Run full test suite
pytest -q
# 98 passed in 3.49s
```

### Supported Natural Language Workflows:
1. **Career Goals:** `"My career goal is to become a Software Engineer."` → Persisted to SQLite.
2. **Goal Retrieval:** `"What is my career goal?"` → Dynamically loaded from database.
3. **Task Engine:** `"Create a task to solve 3 LeetCode problems today."` → SQLite record created.
4. **Task Backlog:** `"List my pending tasks."` → Backlog rendered with priorities.
5. **Next Best Action:** `"What should I study now?"` → Evaluated dynamically via DecisionEngine.
6. **Study Logging:** `"Log 45 minutes of DBMS Transactions study."` → Saved in `study_sessions`.
7. **Weak Topics:** `"What are my weak topics?"` → Spaced repetition retention tracker.
8. **GATE Revision:** `"Plan my GATE revision."` → 3-block structured revision.
9. **Coding Help:** `"Explain binary search."` → Algorithm explanation with time and space complexity.

---

## Quickstart

### Backend
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate  # or source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run build
npm run dev
```

---

## License
MIT License. Created by [Tamizharasan E](https://github.com/Tamizh1309).
