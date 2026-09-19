# Tamizh JARVIS Architecture (Phase 9 Release Candidate)

## System Overview
Tamizh JARVIS is an agentic, data-driven AI assistant engineered for engineering productivity, GATE CS mastery, algorithmic coding preparation, and career execution.

```
[ User Input ]
       │
       ▼
[ ContextManager ] ──► Gathers User Profile, Backlog, Study History & Recent Conversational Turns
       │
       ▼
[ IntentRouter ] ──────► Classifies 22 system intents & extracts entities (code, dates, durations)
       │
       ▼
[ Planner ] ──────────► Decomposes intent into a TaskPlan (tool_name, action, parameters)
       │
       ▼
[ Security Gate ] ────► PermissionManager + ActionValidator + RiskClassifier
       │
       ├─► CRITICAL / Unsafe Shell / Injection ──► BLOCKED
       ├─► HIGH Risk (Deletions) ────────────────► Requires Explicit User Confirmation
       └─► LOW / MEDIUM Risk ────────────────────► Authorized for Execution
       │
       ▼
[ Tool Registry ] ────► Dispatches to BaseTool (task_tool, study_tool, schedule_tool, progress_tool, profile_tool, coding_tool)
       │
       ▼
[ ResponseManager ] ──► Formats polite, actionable UTF-8 responses
       │
       ▼
[ MemoryManager ] ────► Scoped separation: Short-term Conversation Window vs. SQLite Long-term Storage
```

## Subsystem Implementation Matrix

| Component | Status | Verification & Capabilities |
|---|---|---|
| **JarvisCore** | ✅ IMPLEMENTED | Master lifecycle coordinator executing 5-stage safe flow; zero unhandled crashes. |
| **IntentRouter** | ✅ IMPLEMENTED | Multi-intent deterministic routing with regex + AI fallback across 22 intents. |
| **Planner** | ✅ IMPLEMENTED | 100% route alignment: all planned tool calls map to registered `BaseTool` instances. |
| **DecisionEngine** | ✅ IMPLEMENTED | Scenarios A through E covered: No Data, Urgent Task, Weak Topic, Revision Overdue, Target Completed. |
| **Tool Registry** | ✅ IMPLEMENTED | 6 verified tools (`task_tool`, `study_tool`, `schedule_tool`, `progress_tool`, `profile_tool`, `coding_tool`). |
| **PermissionManager** | ✅ IMPLEMENTED | Defense-in-depth gate enforcing 4 risk tiers (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`). |
| **Memory Isolation** | ✅ IMPLEMENTED | Conversational chatter isolated from long-term facts; multi-domain separation (`GOAL`, `PREFERENCE`, `STUDY`). |
| **SQLite Persistence** | ✅ IMPLEMENTED | Async storage via `aiosqlite` with automatic schema migrations for seamless upgrades. |
| **AI Providers** | ✅ IMPLEMENTED | Robust fallback pipeline (`AUTO` -> `GEMINI` -> `LOCAL` -> `FALLBACK`) with credential masking. |
| **Web Dashboard** | ✅ IMPLEMENTED | Cyberpunk React + Vite HUD dashboard with dynamic API configuration and real-time telemetry. |
| **Vector Memory** | 🟡 PLANNED | Local RAG vector store for indexing textbooks and research papers. |
| **Voice Interface** | 🟡 PLANNED | Low-latency voice command loop using local speech-to-text. |
