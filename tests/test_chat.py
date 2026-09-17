import sys
from pathlib import Path
import pytest
from httpx import ASGITransport, AsyncClient

backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from main import app


@pytest.mark.asyncio
async def test_chat_hello_jarvis():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat", json={"message": "Hello JARVIS", "context": {}})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["intent"] == "GENERAL_CHAT"
        assert len(data["response"]) > 0
        assert data["memoryUpdated"] is True


@pytest.mark.asyncio
async def test_chat_create_task():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat", json={
            "message": "Create a task to solve 3 LeetCode problems today",
            "context": {}
        })
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["intent"] == "TASK_CREATE"
        assert data["action"] == "task_created"
        assert data["toolUsed"] == "task_tool"
        assert "LeetCode" in data["data"]["title"]


@pytest.mark.asyncio
async def test_chat_list_tasks():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat", json={"message": "List my pending tasks", "context": {}})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["intent"] == "TASK_LIST"
        assert data["toolUsed"] == "task_tool"
        assert "tasks" in data["data"]


@pytest.mark.asyncio
async def test_chat_complete_task():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat", json={"message": "Complete my DSA task", "context": {}})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["intent"] == "TASK_COMPLETE"
        assert data["action"] == "task_updated"
        assert data["toolUsed"] == "task_tool"


@pytest.mark.asyncio
async def test_chat_next_best_action():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat", json={"message": "What should I study now?", "context": {}})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["intent"] == "NEXT_BEST_ACTION"
        assert "duration_minutes" in data["data"] or "title" in data["data"]


@pytest.mark.asyncio
async def test_chat_plan_gate_revision():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat", json={"message": "Plan my GATE revision", "context": {}})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["intent"] == "GATE_REVISION"
        assert data["action"] == "gate_revision_plan"
        assert data["toolUsed"] == "study_tool"
        assert "GATE" in data["response"]


@pytest.mark.asyncio
async def test_chat_weak_topics():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat", json={"message": "What are my weak topics?", "context": {}})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["intent"] == "MISTAKE_ANALYSIS"
        assert data["action"] == "weak_topics"
        assert data["toolUsed"] == "study_tool"
        assert len(data["data"]["weak_topics"]) > 0


@pytest.mark.asyncio
async def test_chat_career_goal():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat", json={"message": "What is my career goal?", "context": {}})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["intent"] == "CAREER"
        assert data["action"] == "career_goal"
        assert data["toolUsed"] == "profile_tool"
        assert "primary_goal" in data["data"]


@pytest.mark.asyncio
async def test_chat_explain_binary_search():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat", json={"message": "Explain binary search", "context": {}})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["intent"] == "CODING_HELP"
        assert data["action"] == "explain_algorithm"
        assert data["toolUsed"] == "coding_tool"
        assert "O(log N)" in data["response"]


@pytest.mark.asyncio
async def test_chat_reminder():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat", json={"message": "Create a reminder to revise DBMS", "context": {}})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["intent"] == "REMINDER"
        assert data["action"] == "reminder_created"
        assert data["toolUsed"] == "task_tool"


@pytest.mark.asyncio
async def test_chat_permission_denied_prohibited():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # High risk action without confirmation
        res = await client.post("/api/chat", json={
            "message": "update task",
            "context": {"confirmed": False}
        })
        assert res.status_code == 200
