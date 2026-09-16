import sys
from pathlib import Path
import pytest
from httpx import ASGITransport, AsyncClient

backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from main import app


@pytest.mark.asyncio
async def test_api_chat_next_best_action():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "What should I study now?",
            "context": {}
        }
        response = await client.post("/api/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["intent"] == "NEXT_BEST_ACTION"
        assert "response" in data
        assert "data" in data
        assert "toolUsed" in data
        assert "memoryUpdated" in data


@pytest.mark.asyncio
async def test_api_chat_task_creation():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "message": "create task: Review Operating System Semaphores",
            "context": {}
        }
        response = await client.post("/api/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["intent"] == "TASK_CREATE"
        assert data["toolUsed"] == "task_tool"


@pytest.mark.asyncio
async def test_api_study_next_action():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/study/next-action")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "title" in data
        assert "priority" in data
        assert "duration_minutes" in data


@pytest.mark.asyncio
async def test_api_study_briefing():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/study/briefing")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "pending_tasks_count" in data
        assert "target_study_hours" in data
