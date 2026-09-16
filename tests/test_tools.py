import pytest
from memory.memory_manager import MemoryManager
from tools.task_tool import TaskTool
from tools.study_tool import StudyTool
from tools.progress_tool import ProgressTool


@pytest.mark.asyncio
async def test_task_tool_create_and_list():
    mem = MemoryManager(db_path=":memory:")
    await mem.initialize()
    tool = TaskTool(mem)

    res = await tool.execute({"action": "create", "title": "Prepare DBMS notes", "priority": "HIGH"})
    assert res["success"] is True
    assert res["title"] == "Prepare DBMS notes"

    list_res = await tool.execute({"action": "list"})
    assert list_res["success"] is True
    assert list_res["count"] >= 1


@pytest.mark.asyncio
async def test_study_tool_recommend():
    mem = MemoryManager(db_path=":memory:")
    await mem.initialize()
    tool = StudyTool(mem)

    res = await tool.execute({"action": "recommend"})
    assert res["success"] is True
    assert "DBMS" in res["topic"] or len(res["topic"]) > 0
    assert res["duration_minutes"] == 45
    assert res["priority"] == "HIGH"


@pytest.mark.asyncio
async def test_progress_tool_briefing():
    mem = MemoryManager(db_path=":memory:")
    await mem.initialize()
    tool = ProgressTool(mem)

    res = await tool.execute({"action": "briefing"})
    assert res["success"] is True
    assert "pending_tasks_count" in res
    assert "target_study_hours" in res
