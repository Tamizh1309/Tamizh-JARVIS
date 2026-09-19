# Tamizh JARVIS Development Guide (Phase 9 Release Candidate)

## Prerequisites
- Python 3.11 or higher
- Node.js 20 or higher
- npm 10 or higher

## Local Setup

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
# Activate:
.venv\Scripts\activate   # Windows
# source .venv/bin/activate # Linux/Mac

pip install -r requirements.txt
pytest -q
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run build
npm run dev
```

### 3. Running Automated Tests
```bash
# Full test suite (98 tests across unit, integration, e2e, security)
pytest -q

# Targeted test suites
pytest -q tests/test_end_to_end_agent.py
pytest -q tests/test_registry_consistency.py
pytest -q tests/test_error_paths.py
pytest -q tests/test_chat_api.py
pytest -q tests/test_memory.py
pytest -q tests/test_study.py
pytest -q tests/test_tasks.py
pytest -q tests/test_security.py
pytest -q tests/test_phase9_release_validation.py
```

## Production Build & Verification Checklist
- ✅ Run `pytest -q` (must show 0 failures).
- ✅ Run `npm run build` in `frontend/` (must transform modules and generate `dist/` cleanly).
- ✅ Configure `ALLOWED_ORIGINS` in production backend `.env`.
- ✅ Configure `VITE_API_BASE_URL` in frontend build or runtime settings.
