# Tamizh JARVIS Roadmap

## Phase 0: Audit & Foundation Setup (Completed)
- Environment audit (Python 3.14/3.10, Node.js v23, SQLite).
- Repository initialization, Git hooks, .env.example, documentation structure.

## Phase 1: Foundation (Current)
- Backend FastAPI app with logging, configuration, and `/api/health`.
- Frontend React Dashboard with dark futuristic aesthetic, sidebar, chat, and status telemetry.
- Automated health and integration tests.

## Phase 2: AI Provider Layer
- `AIProvider` base class.
- `GeminiProvider` implementation with key rotation/failover.
- `LocalProvider` for Ollama/OpenAI API compatibility.
- Graceful offline fallback provider.

## Phase 3: JARVIS Core & Intent Router
- Agentic execution pipeline: Understand -> Think -> Plan -> Decide -> Select Tool -> Execute -> Verify -> Remember -> Respond.
- Intent classification engine (General Chat, Study, Task, Career, Coding, System).

## Phase 4: Storage & Memory Layer
- SQLite database via SQLAlchemy & aiosqlite.
- User profile, goals, conversation history, and study metrics.
- Targeted memory queries (avoiding context-window saturation).

## Phase 5: Tool & Security System
- Base tool contract with schema validation.
- Four-tier risk classifier (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`).
- Security approval gate preventing unauthorized execution.

## Phase 6: Study Intelligence & Next Best Action Engine
- GATE examination scheduler and syllabus tracker.
- DSA practice tracker and mistake log.
- Deterministic Next Best Action algorithm.

## Phase 7: Voice Layer
- Speech-to-Text (STT) and Text-to-Speech (TTS) integration with visual waveforms.

## Phase 8: Controlled Computer Assistance
- Permission-gated application launching, web browser automation, and screen reading.
