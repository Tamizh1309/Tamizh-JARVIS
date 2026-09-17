# Tamizh JARVIS Roadmap

## Status Matrix

### Implemented & Verified (Phase 1 - Phase 4)
- ✅ **Phase 1: Foundation & Telemetry**: FastAPI backend, React futuristic dark UI, `/api/health`, environment validation.
- ✅ **Phase 2: Real AI Provider Chain**: Predictable provider selection (`AUTO`, `GEMINI`, `LOCAL`, `FALLBACK`), Google Gemini 1.5/2.5 client with rate-limit and error shielding, Ollama local client, offline fallback engine.
- ✅ **Phase 3: Agentic Core & Intent Routing**: 7-stage lifecycle loop, 21 deterministic and semantic intents, multi-step planner, structured JSON contract.
- ✅ **Phase 4: Real Persistence, Tools & Hardening**:
  - Full Task Engine schema with SQLite persistence (`id`, `title`, `description`, `status`, `priority`, `created_at`, `due_at`, `completed_at`, `category`, `source`).
  - 14-domain long-term memory store surviving backend restarts (`USER_PROFILE`, `GOALS`, `PREFERENCES`, `STUDY_HISTORY`, `TOPIC_MASTERY`, `MISTAKES`, `TASKS`, etc.).
  - Deterministic Next Best Action scoring engine.
  - Dynamic Daily Briefing calculated from SQLite.
  - 4-tier security layer (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) with confirmation gates and injection guards.
  - Frontend API configuration with `VITE_API_BASE_URL`.
  - Comprehensive test suite (50 tests passing with 0 failures).

---

### In Development
- ⚠️ **Continuous Audio Streaming**: Enhancing Web Speech API with bidirectional audio streaming and live waveform visualizations.
- ⚠️ **Advanced Spaced Repetition**: Automatic Leitner box interval calculation from historical mistake logs.

---

### Planned (Future Phases)
- ❌ **Phase 5: Local Vector Search**: Hybrid BM25 and vector embedding indexing for million-token technical textbooks.
- ❌ **Phase 6: Multi-Device Sync**: Optional end-to-end encrypted cloud sync for mobile companion app.
- ❌ **Phase 7: Controlled Desktop Automation**: Safe, permission-gated OS accessibility automation for local developer tooling.
