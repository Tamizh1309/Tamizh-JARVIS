import os
import sys
import tempfile
import pytest
from httpx import ASGITransport, AsyncClient

from main import app
from core.jarvis_core import JarvisCore
from core.decision_engine import DecisionEngine
from memory.memory_manager import MemoryManager
from security.risk_classifier import RiskClassifier, RiskLevel
from security.action_validator import ActionValidator
from ai.provider import get_ai_provider
from ai.gemini_provider import GeminiProvider
from ai.fallback_provider import FallbackProvider
from tools.task_tool import TaskTool
from tools.profile_tool import ProfileTool
from tools.coding_tool import CodingTool

# ====================================================
# SECTION 2: CONVERSATIONAL TASK REGRESSION
# ====================================================
@pytest.mark.asyncio
async def test_p10_conversational_task_matching(tmp_path):
    db_file = str(tmp_path / "p10_tasks.db")
    mem = MemoryManager(db_path=db_file)
    await mem.initialize()
    tool = TaskTool(mem)

    # 1. Create a task to study DBMS today
    r_create = await tool.execute({"action": "create", "title": "Study DBMS", "category": "DBMS"})
    assert r_create["success"] is True
    dbms_id = r_create["task_id"]

    # 2. Complete my DBMS task
    r_comp = await tool.execute({"action": "complete", "keyword": "dbms"})
    assert r_comp["success"] is True
    assert r_comp["data"]["task_id"] == dbms_id

    # 3. List my pending tasks -> verified completed DBMS task is not in pending list
    r_list = await tool.execute({"action": "list", "status": "PENDING"})
    assert not any(t["id"] == dbms_id for t in r_list["data"]["tasks"])

    # 4. Test specific keyword variants
    t2_id = (await tool.execute({"action": "create", "title": "Solve 3 Graph Theory problems"}))["task_id"]
    r_variant1 = await tool.execute({"action": "complete", "keyword": "graph"})
    assert r_variant1["success"] is True
    assert r_variant1["data"]["task_id"] == t2_id

    # 5. Test disambiguation: multiple tasks exist, generic pronoun must not accidentally complete wrong task
    t_a = (await tool.execute({"action": "create", "title": "Operating Systems Paging"}))["task_id"]
    t_b = (await tool.execute({"action": "create", "title": "Computer Networks Routing"}))["task_id"]

    r_generic_multi = await tool.execute({"action": "complete", "keyword": "the task"})
    assert r_generic_multi["success"] is False  # Must require disambiguation!
    assert "Multiple pending tasks exist" in r_generic_multi["message"]

    # Specific keyword completes the intended task
    r_specific = await tool.execute({"action": "complete", "keyword": "networks"})
    assert r_specific["success"] is True
    assert r_specific["data"]["task_id"] == t_b

    await mem.long_term.close()

# ====================================================
# SECTION 3: PROFILE / CAREER REGRESSION
# ====================================================
@pytest.mark.asyncio
async def test_p10_profile_action_aliases(tmp_path):
    db_file = str(tmp_path / "p10_profile.db")
    mem = MemoryManager(db_path=db_file)
    await mem.initialize()
    tool = ProfileTool(mem)

    # Set goal
    r_set = await tool.execute({"action": "set_goal", "goal": "Software Engineer"})
    assert r_set["success"] is True

    # Get goal
    r_get = await tool.execute({"action": "get_career_goal"})
    assert r_get["primary_goal"] == "Software Engineer"

    # Action alias: placement & placement_prep
    for act in ["placement", "placement_prep"]:
        r_plc = await tool.execute({"action": act})
        assert r_plc["success"] is True
        assert "Software Engineer" in r_plc["data"]["primary_goal"]

    # Action alias: interview & interview_prep
    for act in ["interview", "interview_prep"]:
        r_int = await tool.execute({"action": act})
        assert r_int["success"] is True
        assert len(r_int["data"]["sample_questions"]) > 0

    # Action alias: resume, resume_review, analyze_resume
    resume_sample = "Software Engineer experienced in Python, FastAPI, Docker, and distributed systems."
    for act in ["resume", "resume_review", "analyze_resume"]:
        r_res = await tool.execute({"action": act, "resume_text": resume_sample})
        assert r_res["success"] is True
        assert r_res["data"]["ats_score"] > 50

    await mem.long_term.close()

# ====================================================
# SECTION 6: MEMORY REGRESSION & PERSISTENCE
# ====================================================
@pytest.mark.asyncio
async def test_p10_memory_persistence(tmp_path):
    db_file = str(tmp_path / "p10_mem.db")

    # Session 1: Store facts
    mem1 = MemoryManager(db_path=db_file)
    await mem1.initialize()
    await mem1.profile.set_goal("Distinguished ML Engineer")
    await mem1.create("PREFERENCE", "preferred_language", "Python")
    await mem1.create("STUDY", "active_subject", "Distributed Systems")
    await mem1.long_term.close()

    # Session 2: Reinitialize
    mem2 = MemoryManager(db_path=db_file)
    await mem2.initialize()
    prof = mem2.get_user_profile()
    assert prof["primary_goal"] == "Distinguished ML Engineer"

    pref = await mem2.read("PREFERENCE", "preferred_language")
    assert pref["value"] == "Python"

    study = await mem2.read("STUDY", "active_subject")
    assert study["value"] == "Distributed Systems"
    await mem2.long_term.close()

# ====================================================
# SECTION 12: REALISTIC 11-STEP UX SESSION
# ====================================================
@pytest.mark.asyncio
async def test_p10_realistic_11_step_ux_session():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Step 1: Open JARVIS
        r1 = await client.get("/api/health")
        assert r1.status_code == 200

        # Step 2: Today's priority
        r2 = await client.get("/api/study/next-action")
        assert r2.status_code == 200

        # Step 3: Create a study task
        r3 = await client.post("/api/chat", json={"message": "Create a task to study DBMS today"})
        assert r3.status_code == 200 and r3.json()["intent"] == "TASK_CREATE"

        # Step 4: Start study session
        r4 = await client.post("/api/study/session", json={
            "subject": "DBMS", "topic": "ACID Properties", "duration": 45, "notes": "Studied atomicity & isolation"
        })
        assert r4.status_code == 200 and r4.json()["success"] is True

        # Step 5: What to study next
        r5 = await client.post("/api/chat", json={"message": "What should I study now?"})
        assert r5.status_code == 200 and r5.json()["intent"] == "NEXT_BEST_ACTION"

        # Step 6: Check weak topics
        r6 = await client.get("/api/study/weak-topics")
        assert r6.status_code == 200 and "weak_topics" in r6.json()

        # Step 7: GATE revision
        r7 = await client.post("/api/chat", json={"message": "Plan my GATE revision"})
        assert r7.status_code == 200 and r7.json()["intent"] == "GATE_REVISION"

        # Step 8: Coding question
        r8 = await client.post("/api/chat", json={"message": "Explain binary search"})
        assert r8.status_code == 200 and r8.json()["intent"] == "CODING_HELP"

        # Step 9: Placement preparation
        r9 = await client.post("/api/chat", json={"message": "Help me with campus placement preparation"})
        assert r9.status_code == 200 and r9.json()["intent"] == "PLACEMENT"

        # Step 10: Career goal
        r10 = await client.post("/api/chat", json={"message": "What is my career goal?"})
        assert r10.status_code == 200 and r10.json()["intent"] == "CAREER"

        # Step 11: Complete task
        r11 = await client.post("/api/chat", json={"message": "Complete my DBMS task"})
        assert r11.status_code == 200 and r11.json()["intent"] == "TASK_COMPLETE"
