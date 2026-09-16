# Tamizh JARVIS API Documentation

All API endpoints are prefixed with `/api`.

---

## 1. System & Health

### `GET /api/health`
Returns the status, service name, version, and active AI provider state.

**Response**:
```json
{
  "status": "ok",
  "service": "Tamizh JARVIS",
  "version": "1.0.0",
  "environment": "development",
  "ai_provider": "fallback"
}
```

---

## 2. Agentic Chat & Core Interaction

### `POST /api/chat`
Sends a query to the Tamizh JARVIS agentic core engine.

**Request**:
```json
{
  "message": "What should I study now?",
  "context": {}
}
```

**Response**:
```json
{
  "success": true,
  "intent": "NEXT_BEST_ACTION",
  "action": "REVISION_SESSION",
  "response": "Next Best Action: Revise DBMS Transactions & Concurrency Control for 45 minutes. Revision interval is due and recent performance indicates this weak topic needs reinforcement.",
  "data": {
    "success": true,
    "action": "REVISION_SESSION",
    "subject": "Database Management Systems",
    "topic": "DBMS Transactions & Concurrency Control",
    "duration_minutes": 45,
    "priority": "HIGH",
    "reason": "Revision interval is due and recent performance indicates this weak topic needs reinforcement."
  },
  "toolUsed": "study_tool",
  "memoryUpdated": true
}
```

---

## 3. Study Intelligence

### `GET /api/study/next-action`
Computes and returns the transparent Next Best Action from the deterministic decision engine.

**Response**:
```json
{
  "success": true,
  "action": "EXECUTE_HIGH_PRIORITY_TASK",
  "title": "Revise DBMS Transactions",
  "duration_minutes": 45,
  "priority": "HIGH",
  "reason": "High priority task pending in your backlog: 'Revise DBMS Transactions'.",
  "description": "Review ACID properties and 2PL locking protocols."
}
```

### `GET /api/study/briefing`
Aggregates and returns daily study and task metrics.

**Response**:
```json
{
  "success": true,
  "action": "daily_briefing",
  "pending_tasks_count": 6,
  "today_study_hours": 0.0,
  "target_study_hours": 3.5,
  "completion_percentage": 0,
  "message": "Daily Briefing: 6 pending tasks, 0.0h / 3.5h studied (0% complete)."
}
```

---

## 4. Task Management

### `GET /api/tasks?status=PENDING`
Returns tasks from SQLite storage.

### `POST /api/tasks`
Creates a new task.

**Request**:
```json
{
  "title": "Solve 3 LeetCode dynamic programming problems",
  "description": "0/1 knapsack and coin change variants",
  "priority": "HIGH"
}
```

---

## 5. Memory & Context

### `GET /api/memory`
Retrieves user profile, active study goals, weak topics, and recent dialogue turns.
