# Tamizh JARVIS Architecture

## System Overview
Tamizh JARVIS is architected as an agentic assistant orchestrating user context, NLP intent classification, planning, security permission verification, tool execution, and memory persistence.

```
[ User Input ]
       │
       ▼
[ ContextManager ] ──> Gathers User Profile, Backlog, Study History & Recent Turns
       │
       ▼
[ IntentRouter ] ────> Classifies 21 intents & extracts entities (code, dates, durations)
       │
       ▼
[ Planner ] ─────────> Decomposes intent into a TaskPlan (tool, action, parameters)
       │
       ▼
[ Security Gate ] ───> PermissionManager + ActionValidator + RiskClassifier
       │
       ├── CRITICAL / Unsafe Shell ──> Blocked
       ├── HIGH Risk ────────────────> Requires Human Approval
       └── LOW / MEDIUM Risk ────────> Authorized
       │
       ▼
[ Tool Registry ] ───> Executes BaseTool (task_tool, study_tool, profile_tool, coding_tool, etc.)
       │
       ▼
[ ResponseManager ] ─> Formats polite, actionable UTF-8 responses
       │
       ▼
[ MemoryManager ] ───> Updates ConversationContext (short-term) and SQLite (long-term)
```

## Core Modules Status
- `JarvisCore`: `[IMPLEMENTED]` Master lifecycle orchestrator with stable schema.
- `DecisionEngine`: `[IMPLEMENTED]` Multi-factor candidate scoring with transparent `score_breakdown`.
- `TaskTool`: `[IMPLEMENTED]` Relational task backlog (`PENDING`, `COMPLETED`, `DELETED`).
- `StudyTool`: `[IMPLEMENTED]` Real session logging, spaced repetition, weak topic tracking.
- `ProfileTool`: `[IMPLEMENTED]` Career goal storage, placement strategy, ATS resume analysis.
- `CodingTool`: `[IMPLEMENTED]` AST/AI debugging, code review, and personalized DSA plans.
- `MemoryManager`: `[IMPLEMENTED]` 8-domain memory classification.
- `DatabaseManager`: `[IMPLEMENTED]` SQLite async management (`aiosqlite`).
