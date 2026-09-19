# Tamizh JARVIS REST API Specification (Phase 9 Release Candidate)

All endpoints return structured JSON responses.

## Endpoint Status & Matrix

| Endpoint | Method | Status | Description |
|---|---|---|---|
| `/api/chat` | `POST` | ✅ IMPLEMENTED | Core natural language agent interface. Dispatches to IntentRouter, Planner, SecurityGate, Tool, and Memory. |
| `/api/health` | `GET` | ✅ IMPLEMENTED | Service health, version, environment, and active AI provider inspection. |
| `/api/study/next-action` | `GET` | ✅ IMPLEMENTED | Computes data-driven Next Best Action based on Scenarios A–E with mathematical `score_breakdown`. |
| `/api/study/briefing` | `GET` | ✅ IMPLEMENTED | Real-time daily study briefing, study hours completed, and target percentage. |
| `/api/study/history` | `GET` | ✅ IMPLEMENTED | Historical study sessions in reverse chronological order with pagination (`limit`). |
| `/api/study/weak-topics` | `GET` | ✅ IMPLEMENTED | Weak topics requiring spaced repetition reinforcement. |
| `/api/study/session` | `POST` | ✅ IMPLEMENTED | Logs completed study session directly into SQLite with validation. |
| `/api/tasks` | `GET` | ✅ IMPLEMENTED | Lists tasks filtered by `status` (PENDING, COMPLETED) or `category`. |
| `/api/tasks` | `POST` | ✅ IMPLEMENTED | Creates a new task with title, priority, category, and due date. |
| `/api/tasks/{id}` | `PATCH` / `PUT` | ✅ IMPLEMENTED | Updates task details, priority, or category. |
| `/api/tasks/{id}/complete` | `POST` | ✅ IMPLEMENTED | Marks task status as COMPLETED and timestamps completion. |
| `/api/tasks/{id}` | `DELETE` | ✅ IMPLEMENTED | Removes task; enforces confirmation protocol for HIGH risk deletion. |
| `/api/memory/profile` | `GET` | ✅ IMPLEMENTED | Retrieves user profile, primary goal, target hours, and weak topics. |
| `/api/memory/domain` | `GET` | ✅ IMPLEMENTED | Lists memory records scoped by category (e.g. GOAL, PREFERENCE, STUDY). |
| `/api/voice/stream` | `POST` | 🟡 PLANNED | Full-duplex WebRTC audio streaming for hands-free study mode. |
| `/api/embeddings/search` | `POST` | 🟡 PLANNED | Semantic vector search over personal study notes and syllabus. |

## Request & Response Schemas

### POST /api/chat
**Request:**
```json
{
  "message": "Create a task to solve 3 LeetCode problems today",
  "context": {}
}
```
**Response (200 OK):**
```json
{
  "success": true,
  "intent": "TASK_CREATE",
  "action": "task_created",
  "response": "Created task: Solve 3 LeetCode problems today (Priority: HIGH)",
  "data": {
    "task_id": 12,
    "title": "Solve 3 LeetCode problems today",
    "status": "PENDING",
    "priority": "HIGH"
  },
  "toolUsed": "task_tool",
  "memoryUpdated": true
}
```

### Error Responses
- `400 Bad Request`: Invalid parameters (e.g. empty message, negative query limit).
- `404 Not Found`: Entity not found (e.g. non-existent task ID).
- `422 Unprocessable Entity`: Schema validation errors (e.g. missing required fields).
- `500 Internal Server Error`: Unhandled server exception (stack traces sanitized in production).
