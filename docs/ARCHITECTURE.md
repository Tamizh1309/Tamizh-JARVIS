# Tamizh JARVIS Architecture

## Core Architectural Principles

1. **Deterministic Logic First**: Business rules, study schedules, and task priorities are handled by testable deterministic engines. The LLM acts as an understanding, reasoning, and conversational layer.
2. **Decoupled AI Providers**: The system never binds directly to a single LLM vendor. An `AIProvider` abstraction allows switching between Google Gemini, local Ollama models, and offline deterministic fallbacks.
3. **Strict Security Interception**: Tools cannot be executed without passing through the `PermissionManager` and `RiskClassifier`.
4. **Structured Internal Contract**: Every request follows the `JarvisCore.handle(user_input, context)` contract and produces structured JSON responses with explicit intent, tool, and memory state.

---

## Component Breakdown

### 1. `backend/api/`
FastAPI routes exposing REST endpoints:
- `/api/health`: Health status and service configuration.
- `/api/chat`: Interaction with JARVIS Core.
- `/api/tasks`: Task management and next actions.
- `/api/memory`: Long-term memory query and update.
- `/api/study`: Study sessions, GATE planning, and revision metrics.

### 2. `backend/core/`
- `jarvis_core.py`: Orchestrator of the agentic loop.
- `router.py`: Categorizes user input into predefined and extensible intents.
- `planner.py`: Decomposes multi-step tasks into actionable sub-goals.
- `decision_engine.py`: Computes Next Best Action based on schedules, deadlines, and mastery gaps.
- `context_manager.py`: Manages the active session context window.
- `response_manager.py`: Formats user-facing responses, stripping internal reasoning.

### 3. `backend/ai/`
- `provider.py`: Abstract `AIProvider` base interface.
- `gemini_provider.py`: Google Gemini API implementation.
- `local_provider.py`: Local LLM (Ollama) endpoint.
- `fallback_provider.py`: Offline rule-based fallback ensuring zero downtime.

### 4. `backend/memory/`
- `memory_manager.py`: Coordinates short-term memory and long-term storage.
- `profile_memory.py`: User profile, preferences, and long-term goals.
- `study_memory.py`: Revision intervals, quiz results, weak topics, and mastery level.
- `conversation_memory.py`: In-flight conversational history with summarization.

### 5. `backend/security/`
- `risk_classifier.py`: Evaluates risk tier (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- `permission_manager.py`: Gates tool execution; demands explicit confirmation for high-risk operations.
- `action_validator.py`: Validates input arguments against Pydantic schemas.

### 6. `backend/tools/`
- Standardized `BaseTool` class (`name`, `description`, `input_schema`, `execute()`).
- Implementations for task management, study planning, schedule checks, and controlled web retrieval.
