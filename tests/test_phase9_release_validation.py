import os
import sys
import tempfile
import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from core.jarvis_core import JarvisCore
from core.planner import Planner
from core.decision_engine import DecisionEngine
from memory.memory_manager import MemoryManager
from security.risk_classifier import RiskClassifier, RiskLevel
from security.action_validator import ActionValidator
from ai.provider import get_ai_provider
from ai.gemini_provider import GeminiProvider
from ai.local_provider import LocalProvider
from ai.fallback_provider import FallbackProvider
from tools.coding_tool import CodingTool

ALL_INTENTS = [
    "GENERAL_CHAT", "TASK_CREATE", "TASK_LIST", "TASK_UPDATE", "TASK_COMPLETE",
    "REMINDER", "STUDY_PLAN", "NEXT_BEST_ACTION", "GATE_PREPARATION", "GATE_REVISION",
    "DSA_PRACTICE", "CODING_HELP", "DEBUG_CODE", "CODE_REVIEW", "MISTAKE_ANALYSIS",
    "PROGRESS_ANALYSIS", "CAREER", "PLACEMENT", "INTERVIEW", "RESUME",
    "SCHEDULE", "STUDY_LOG",
]

@pytest.mark.asyncio
async def test_p9_ai_providers_and_masking():
    fallback = get_ai_provider("FALLBACK")
    assert isinstance(fallback, FallbackProvider)
    assert await fallback.is_available() is True
    res = await fallback.generate("Explain binary search")
    assert "binary search" in res.lower()

    gemini_invalid = GeminiProvider(api_key="AIzaSyFakeKey123456789")
    assert "..." in gemini_invalid._masked_key()
    assert "AIzaSyFakeKey123456789" not in gemini_invalid._masked_key()

@pytest.mark.asyncio
async def test_p9_real_chat_intents():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        queries = [
            ("Hello JARVIS", "GENERAL_CHAT"),
            ("Create a task to solve 3 LeetCode problems today", "TASK_CREATE"),
            ("List my pending tasks", "TASK_LIST"),
            ("What should I study now?", "NEXT_BEST_ACTION"),
            ("Plan my GATE revision", "GATE_REVISION"),
            ("What is my career goal?", "CAREER"),
            ("Explain binary search", "CODING_HELP"),
        ]
        for msg, exp_intent in queries:
            resp = await client.post("/api/chat", json={"message": msg, "context": {}})
            assert resp.status_code == 200
            data = resp.json()
            assert data["success"] is True
            assert data["intent"] == exp_intent
            assert len(data["response"]) > 0

@pytest.mark.asyncio
async def test_p9_database_persistence_across_instances(tmp_path):
    db_file = str(tmp_path / "p9_persist.db")
    
    # Instance 1
    mem1 = MemoryManager(db_path=db_file)
    await mem1.initialize()
    core1 = JarvisCore(memory_manager=mem1)
    await core1.initialize()
    await mem1.profile.set_goal("Software Engineer at Google")
    task_id = await mem1.long_term.create_task(title="Persistent LeetCode Task", priority="HIGH")
    await mem1.long_term.complete_task(task_id)
    await core1.tools["study_tool"].execute({
        "action": "log_session", "subject": "CS", "topic": "OS Concurrency", "duration": 45
    })
    await mem1.long_term.close()

    # Instance 2 (Simulating backend restart)
    mem2 = MemoryManager(db_path=db_file)
    await mem2.initialize()
    core2 = JarvisCore(memory_manager=mem2)
    await core2.initialize()
    profile = mem2.get_user_profile()
    assert profile["primary_goal"] == "Software Engineer at Google"
    task = await mem2.long_term.get_task(task_id)
    assert task["status"] == "COMPLETED"
    hist = await core2.tools["study_tool"].execute({"action": "history"})
    assert any(s["topic"] == "OS Concurrency" for s in hist["sessions"])
    await mem2.long_term.close()

@pytest.mark.asyncio
async def test_p9_tool_registry_and_planner_consistency():
    core = JarvisCore()
    await core.initialize()
    for rt in ["task_tool", "study_tool", "schedule_tool", "progress_tool", "profile_tool", "coding_tool"]:
        assert rt in core.tools
    assert core.validate_tool_registry() is True
    for intent in ALL_INTENTS:
        plan = Planner.create_plan(intent, {"title": "Test"}, {})
        if plan.tool_name:
            assert plan.tool_name in core.tools

@pytest.mark.asyncio
async def test_p9_study_apis_and_session_logging():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r_nba = await client.get("/api/study/next-action")
        assert r_nba.status_code == 200
        assert r_nba.json()["success"] is True

        r_post = await client.post("/api/study/session", json={
            "subject": "Math", "topic": "Linear Algebra", "duration": 40, "score": 90.0
        })
        assert r_post.status_code == 200
        assert r_post.json()["success"] is True

        r_hist = await client.get("/api/study/history?limit=5")
        assert r_hist.status_code == 200
        assert any(s["topic"] == "Linear Algebra" for s in r_hist.json()["sessions"])
