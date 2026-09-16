# Tamizh JARVIS API Documentation

All API endpoints are prefixed with `/api`.

## 1. System & Health

### `GET /api/health`
Returns the status and runtime information of the service.

**Response**:
```json
{
  "status": "ok",
  "service": "tamizh-jarvis",
  "version": "1.0.0",
  "environment": "development",
  "ai_provider": "gemini"
}
```

---

## 2. Core Interaction

### `POST /api/chat`
Sends a query to Tamizh JARVIS core.

**Request**:
```json
{
  "message": "What should I revise for GATE today?",
  "session_id": "session-xyz",
  "context": {}
}
```

**Response**:
```json
{
  "success": true,
  "intent": "NEXT_BEST_ACTION",
  "action": "REVISION_SESSION",
  "response": "Revise DBMS Transactions for 45 minutes.",
  "data": {
    "topic": "DBMS Transactions",
    "duration_minutes": 45,
    "priority": "HIGH"
  },
  "tool_used": "study_tool",
  "memory_updated": true
}
```

---

## 3. Tasks & Study

- `GET /api/tasks` — List active tasks
- `POST /api/tasks` — Create task
- `GET /api/study/next-action` — Fetch Next Best Action
- `GET /api/memory` — Retrieve stored user memories
