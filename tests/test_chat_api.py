import sys
from pathlib import Path
import pytest
from httpx import ASGITransport, AsyncClient

backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from main import app


@pytest.mark.asyncio
async def test_api_chat_1_hello_jarvis():
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
async def test_api_chat_2_create_task():
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
async def test_api_chat_3_list_tasks():
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
async def test_api_chat_4_complete_task():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat", json={"message": "Complete my DSA task", "context": {}})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["intent"] == "TASK_UPDATE"
        assert data["action"] == "task_updated"
        assert data["toolUsed"] == "task_tool"


@pytest.mark.asyncio
async def test_api_chat_5_next_best_action():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat", json={"message": "What should I study now?", "context": {}})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["intent"] == "NEXT_BEST_ACTION"
        assert data["toolUsed"] in ["study_tool", "none"]
        assert "duration_minutes" in data["data"] or "topic" in data["data"]


@pytest.mark.asyncio
async def test_api_chat_6_plan_gate_revision():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat", json={"message": "Plan my GATE revision", "context": {}})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["intent"] == "STUDY_PLAN"
        assert data["action"] == "gate_revision_plan"
        assert data["toolUsed"] == "study_tool"
        assert "GATE" in data["response"]


@pytest.mark.asyncio
async def test_api_chat_7_weak_topics():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat", json={"message": "What are my weak topics?", "context": {}})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["intent"] == "WEAK_TOPICS"
        assert data["action"] == "weak_topics"
        assert data["toolUsed"] == "study_tool"
        assert len(data["data"]["weak_topics"]) > 0


@pytest.mark.asyncio
async def test_api_chat_8_career_goal():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/chat", json={"message": "What is my career goal?", "context": {}})
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["intent"] == "CAREER_GOAL"
        assert data["action"] == "career_goal"
        assert data["toolUsed"] == "profile_tool"
        assert "GATE CS" in data["data"]["primary_goal"]


@pytest.mark.asyncio
async def test_api_chat_9_explain_binary_search():
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
async def test_api_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_api_study_next_action():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/study/next-action")
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert "title" in data
        assert "priority" in data


@pytest.mark.asyncio
async def test_api_study_briefing():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/study/briefing")
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert "pending_tasks_count" in data
