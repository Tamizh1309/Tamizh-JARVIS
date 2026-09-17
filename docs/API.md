# Tamizh JARVIS REST API Specification

## Endpoints

### 1. Chat
- **POST** `/api/chat`
  - Body: `{"message": str, "context": Optional[dict]}`
  - Status Codes: `200 OK`, `400 Bad Request`, `422 Unprocessable Entity`, `500 Server Error`
  - Response Schema:
    ```json
    {
      "success": true,
      "intent": "TASK_CREATE",
      "action": "task_created",
      "response": "Created task...",
      "data": {},
      "toolUsed": "task_tool",
      "memoryUpdated": true
    }
    ```

### 2. Health
- **GET** `/api/health`
  - Status: `200 OK`
  - Returns service status, version, environment, and active AI provider.

### 3. Study Subsystem
- **GET** `/api/study/next-action`: Computes Next Best Action with `score_breakdown`.
- **GET** `/api/study/briefing`: Returns dynamic daily briefing metrics from SQLite.
- **GET** `/api/study/history?limit=10`: Returns study session log.
- **GET** `/api/study/weak-topics`: Returns tracked weak topics.
- **POST** `/api/study/session`: Logs a study session (`subject`, `topic`, `duration`, `notes`, `score`, `timestamp`).

### 4. Tasks Subsystem
- **GET** `/api/tasks`: List tasks filtered by `status` or `category`.
- **POST** `/api/tasks`: Create a new task.
- **PATCH / PUT** `/api/tasks/{task_id}`: Update task properties.
- **POST** `/api/tasks/{task_id}/complete`: Mark task as completed.
- **DELETE** `/api/tasks/{task_id}`: Delete task record.
