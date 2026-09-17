import pytest
import pytest_asyncio
from core.jarvis_core import JarvisCore
from memory.memory_manager import MemoryManager


@pytest_asyncio.fixture
async def agent(tmp_path):
    db_file = str(tmp_path / "e2e_agent.db")
    memory = MemoryManager(db_path=db_file)
    await memory.initialize()
    core = JarvisCore(memory_manager=memory)
    await core.initialize()
    yield core
    await memory.long_term.close()


@pytest.mark.asyncio
async def test_task_create_end_to_end(agent):
    """User input -> Router -> Planner -> Permission -> Tool -> Memory -> Response"""
    res = await agent.handle("Create a task to practice Dynamic Programming today")
    assert res["success"] is True
    assert res["intent"] == "TASK_CREATE"
    assert res["action"] == "task_created"
    assert res["toolUsed"] == "task_tool"
    assert res["memoryUpdated"] is True
    assert "Dynamic Programming" in res["response"]

    # Verify task was persisted in SQLite
    tasks = await agent.memory.long_term.list_tasks(status="PENDING")
    assert any("Dynamic Programming" in t["title"] for t in tasks)


@pytest.mark.asyncio
async def test_task_list_end_to_end(agent):
    # Pre-create task
    await agent.handle("Create a task to revise Operating Systems")

    res = await agent.handle("List my pending tasks")
    assert res["success"] is True
    assert res["intent"] == "TASK_LIST"
    assert res["action"] == "task_list"
    assert res["toolUsed"] == "task_tool"
    assert len(res["data"]["tasks"]) >= 1


@pytest.mark.asyncio
async def test_task_complete_end_to_end(agent):
    await agent.handle("Create a task to solve binary search")
    res = await agent.handle("Complete binary search task")
    assert res["success"] is True
    assert res["intent"] == "TASK_COMPLETE"
    assert res["action"] == "task_updated"
    assert res["toolUsed"] == "task_tool"
    assert "COMPLETED" in res["response"]


@pytest.mark.asyncio
async def test_study_plan_end_to_end(agent):
    res = await agent.handle("Plan my study schedule for DBMS")
    assert res["success"] is True
    assert res["intent"] == "STUDY_PLAN"
    assert res["toolUsed"] == "study_tool"
    assert "Revision" in res["response"] or "Revise" in res["response"]


@pytest.mark.asyncio
async def test_next_best_action_end_to_end(agent):
    res = await agent.handle("What is my next best study action?")
    assert res["success"] is True
    assert res["intent"] == "NEXT_BEST_ACTION"
    assert res["toolUsed"] == "decision_engine"
    assert "Next Best Action:" in res["response"]
    assert "data" in res and ("title" in res["data"] or "topic" in res["data"])


@pytest.mark.asyncio
async def test_gate_revision_end_to_end(agent):
    res = await agent.handle("Plan my GATE revision")
    assert res["success"] is True
    assert res["intent"] == "GATE_REVISION"
    assert res["toolUsed"] == "study_tool"
    assert "GATE" in res["response"]


@pytest.mark.asyncio
async def test_dsa_practice_end_to_end(agent):
    res = await agent.handle("Give me DSA practice problems for today")
    assert res["success"] is True
    assert res["intent"] == "DSA_PRACTICE"
    assert res["toolUsed"] == "coding_tool"
    assert len(res["data"]["recommended_problems"]) >= 3


@pytest.mark.asyncio
async def test_coding_help_end_to_end(agent):
    res = await agent.handle("Explain binary search algorithm")
    assert res["success"] is True
    assert res["intent"] == "CODING_HELP"
    assert res["toolUsed"] == "coding_tool"
    assert "Binary Search" in res["response"]
    assert "O(log N)" in res["response"]


@pytest.mark.asyncio
async def test_career_goal_end_to_end(agent):
    # Set career goal
    res_set = await agent.handle("My goal is to become a Lead Systems Architect")
    assert res_set["success"] is True
    assert res_set["intent"] == "CAREER"
    assert res_set["toolUsed"] == "profile_tool"
    assert "Lead Systems Architect" in res_set["response"]

    # Retrieve career goal - must read persisted value from SQLite, not hardcoded!
    res_get = await agent.handle("What is my career goal?")
    assert res_get["success"] is True
    assert res_get["intent"] == "CAREER"
    assert "Lead Systems Architect" in res_get["response"]
    assert res_get["data"]["primary_goal"] == "Lead Systems Architect"


@pytest.mark.asyncio
async def test_progress_analysis_end_to_end(agent):
    res = await agent.handle("Show me today's daily briefing and progress analysis")
    assert res["success"] is True
    assert res["intent"] == "PROGRESS_ANALYSIS"
    assert res["toolUsed"] == "progress_tool"
    assert "Daily Briefing" in res["response"]


@pytest.mark.asyncio
async def test_schedule_end_to_end(agent):
    res = await agent.handle("Check my daily routine and timetable schedule")
    assert res["success"] is True
    assert res["intent"] == "SCHEDULE"
    assert res["toolUsed"] == "schedule_tool"
    assert "Current time is" in res["response"]
