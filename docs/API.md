# TAMIZH JARVIS — REST API REFERENCE

All endpoints are hosted at `/api`. In development, requests are served on `http://127.0.0.1:8000`.

---

## 1. Chat & Agentic Execution

### `POST /api/chat`
Main conversational and agentic entrypoint. Accepts user query, evaluates intent, checks permissions, executes tools if necessary, records memory, and synthesizes structured response.

**Request Body:**
```json
{
  "message": "Create a task to solve 3 LeetCode problems today",
  "context": {
    "confirmed": false
  }
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "intent": "TASK_CREATE",
  "action": "task_created",
  "response": "Created task: \"Solve 3 LeetCode problems today\" [Priority: MEDIUM].",
  "data": {
    "success": true,
    "action": "task_created",
    "task_id": 4,
    "title": "Solve 3 LeetCode problems today",
    "priority": "MEDIUM",
    "category": "GENERAL",
    "message": "Task 'Solve 3 LeetCode problems today' created successfully [Priority: MEDIUM]."
  },
  "toolUsed": "task_tool",
  "memoryUpdated": true
}
```

---

## 2. Health & Telemetry

### `GET /api/health`
Returns system status, active environment, version, and current AI provider.

**Response (200 OK):**
```json
{
  "status": "ok",
  "service": "Tamizh JARVIS",
  "version": "1.0.0",
  "environment": "development",
  "ai_provider": "gemini"
}
```

---

## 3. Study & Decision Intelligence

### `GET /api/study/next-action`
Computes the dynamic Next Best Action using the multi-factor deterministic scoring engine.

**Response (200 OK):**
```json
{
  "success": true,
  "action": "REVISION_SESSION",
  "title": "Revise DBMS Transactions & Concurrency Control",
  "duration_minutes": 45,
  "priority": "HIGH",
  "reason": "Spaced revision is due for weak topic 'DBMS Transactions & Concurrency Control' to maintain retention curve.",
  "description": "Targeted focus block on DBMS Transactions & Concurrency Control with active recall and PYQ practice."
}
```

### `GET /api/study/briefing`
Returns structured daily progress computed directly from SQLite.

**Response (200 OK):**
```json
{
  "success": true,
  "action": "daily_briefing",
  "pending_tasks_count": 3,
  "today_study_hours": 1.5,
  "target_study_hours": 3.5,
  "completion_percentage": 42,
  "message": "Daily Briefing: 3 pending tasks, 1.5h / 3.5h studied (42% complete)."
}
```

### `GET /api/study/history`
Returns logged study sessions in reverse chronological order.

### `GET /api/study/weak-topics`
Returns list of weak topics and recorded mistakes.

### `POST /api/study/session`
Logs a completed study session into SQLite.

**Request Body:**
```json
{
  "subject": "Operating Systems",
  "topic": "Deadlocks & Bankers Algorithm",
  "duration": 45,
  "notes": "Covered 4 conditions and safety check algorithm."
}
```

---

## 4. Task Management

### `GET /api/tasks`
Lists tasks with optional filtering by `status`, `category`, and `limit`.

### `POST /api/tasks`
Creates a new task with complete schema.

**Request Body:**
```json
{
  "title": "Practice 10 GATE CSE PYQs",
  "description": "Focus on Computer Networks subnetting questions",
  "priority": "HIGH",
  "due_at": "2026-10-01",
  "category": "GATE",
  "source": "USER"
}
```

### `PATCH /api/tasks/{task_id}`
Updates task attributes (`title`, `description`, `status`, `priority`, `due_at`, `category`).

### `POST /api/tasks/{task_id}/complete`
Marks the task as `COMPLETED` and sets `completed_at` to the current ISO timestamp.

### `DELETE /api/tasks/{task_id}`
Removes the specified task from SQLite.

---

## 5. Long-Term Memory

### `GET /api/memory`
Retrieves aggregated profile context, active goals, and recent turns.

### `GET /api/memory/search?q={query}&category={optional}`
Full-text search across all persistent SQLite memory records.

### `POST /api/memory`
Creates or updates a memory record in a specified category (`USER_PROFILE`, `GOALS`, `PREFERENCES`, `TOPIC_MASTERY`, `MISTAKES`, etc.).

### `DELETE /api/memory/{category}/{key}`
Deletes the specific memory item.
