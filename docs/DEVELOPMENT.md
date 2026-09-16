# Tamizh JARVIS Developer Guide

## Local Setup

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
# Activate:
.venv\Scripts\activate   # Windows
# source .venv/bin/activate # Linux/Mac

pip install -r requirements.txt
pytest
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Running Tests
```bash
# Run backend tests
pytest -v tests/
```

### 4. Coding Standards
- Python code strictly uses type annotations and Pydantic schemas.
- Vanilla CSS in `frontend/src/index.css` maintaining the dark-first futuristic palette.
- Keep business logic deterministic where possible; use the AI Provider only for language understanding, decomposition, and summarization.
