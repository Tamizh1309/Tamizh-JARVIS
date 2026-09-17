import pytest
import pytest_asyncio
from memory.memory_manager import MemoryManager
from tools.task_tool import TaskTool
from tools.study_tool import StudyTool
from tools.coding_tool import CodingTool
from tools.profile_tool import ProfileTool
from tools.progress_tool import ProgressTool


@pytest_asyncio.fixture
async def memory_mgr(tmp_path):
    db_file = str(tmp_path / "tools_test.db")
    mgr = MemoryManager(db_path=db_file)
    await mgr.initialize()
    yield mgr
    await mgr.long_term.close()


@pytest.mark.asyncio
async def test_task_tool_lifecycle(memory_mgr):
    tool = TaskTool(memory_mgr)

    # 1. Create
    res = await tool.execute({"action": "create", "title": "Solve 3 LeetCode problems", "priority": "HIGH", "category": "DSA"})
    assert res["success"] is True
    task_id = res["task_id"]

    # 2. List
    list_res = await tool.execute({"action": "list", "status": "PENDING"})
    assert list_res["success"] is True
    assert any(t["id"] == task_id for t in list_res["tasks"])

    # 3. Complete
    comp_res = await tool.execute({"action": "complete", "task_id": task_id})
    assert comp_res["success"] is True

    # 4. Delete
    del_res = await tool.execute({"action": "delete", "task_id": task_id})
    assert del_res["success"] is True


@pytest.mark.asyncio
async def test_study_tool_sessions_and_plans(memory_mgr):
    tool = StudyTool(memory_mgr)

    # Log study session
    log_res = await tool.execute({
        "action": "log_session",
        "subject": "DBMS",
        "topic": "ACID Properties & 2PL",
        "duration": 45
    })
    assert log_res["success"] is True
    assert log_res["duration"] == 45

    # Check history
    hist_res = await tool.execute({"action": "history"})
    assert hist_res["success"] is True
    assert len(hist_res["sessions"]) >= 1

    # Check revision plan
    plan_res = await tool.execute({"action": "plan_revision"})
    assert plan_res["success"] is True
    assert "GATE" in plan_res["target_exam"]


@pytest.mark.asyncio
async def test_coding_tool_binary_search_and_dsa():
    tool = CodingTool()

    # Explain Binary Search
    algo_res = await tool.execute({"action": "explain", "topic": "binary search"})
    assert algo_res["success"] is True
    assert algo_res["algorithm"] == "Binary Search"
    assert "O(log N)" in algo_res["time_complexity"]
    assert "def binary_search" in algo_res["code_example"]

    # DSA Practice
    dsa_res = await tool.execute({"action": "dsa_practice"})
    assert dsa_res["success"] is True
    assert len(dsa_res["recommended_problems"]) >= 3


@pytest.mark.asyncio
async def test_profile_tool_goal_update(memory_mgr):
    tool = ProfileTool(memory_mgr)

    # Get career goal
    get_res = await tool.execute({"action": "get_career_goal"})
    assert get_res["success"] is True
    assert "GATE" in get_res["primary_goal"]

    # Set new career goal
    set_res = await tool.execute({"action": "set_goal", "goal": "Principal AI Systems Engineer"})
    assert set_res["success"] is True
    assert set_res["primary_goal"] == "Principal AI Systems Engineer"

    # Verify retrieved goal updated
    get_res2 = await tool.execute({"action": "get_career_goal"})
    assert get_res2["primary_goal"] == "Principal AI Systems Engineer"


@pytest.mark.asyncio
async def test_progress_tool_briefing(memory_mgr):
    tool = ProgressTool(memory_mgr)
    briefing = await tool.execute({"action": "briefing"})
    assert briefing["success"] is True
    assert "pending_tasks_count" in briefing
    assert "today_study_hours" in briefing
    assert "target_study_hours" in briefing
    assert "completion_percentage" in briefing
