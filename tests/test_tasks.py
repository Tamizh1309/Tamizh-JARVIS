import pytest
from core.jarvis_core import JarvisCore
from memory.memory_manager import MemoryManager
from tools.task_tool import TaskTool


@pytest.mark.asyncio
async def test_tasks_lifecycle_create_list_complete(tmp_path):
    db_file = str(tmp_path / "test_task_lifecycle.db")
    mem = MemoryManager(db_path=db_file)
    await mem.initialize()
    tool = TaskTool(mem)

    # 1. CREATE_TASK: "Study DBMS Transactions"
    create_res = await tool.execute({
        "action": "create",
        "title": "Study DBMS Transactions",
        "priority": "HIGH",
        "category": "DBMS"
    })
    assert create_res["success"] is True
    assert create_res["action"] == "task_created"
    task_id = create_res["data"]["task_id"]
    assert task_id > 0
    assert create_res["data"]["status"] == "PENDING"

    # 2. LIST_TASKS: Verify status is PENDING / TODO
    list_res = await tool.execute({"action": "list", "status": "PENDING"})
    assert list_res["success"] is True
    tasks = list_res["data"]["tasks"]
    assert any(t["id"] == task_id and t["title"] == "Study DBMS Transactions" for t in tasks)

    # 3. COMPLETE_TASK: Complete task
    complete_res = await tool.execute({
        "action": "complete",
        "task_id": task_id
    })
    assert complete_res["success"] is True
    assert complete_res["data"]["status"] == "COMPLETED"

    # 4. LIST AGAIN: Status has transitioned to COMPLETED
    all_tasks = await mem.long_term.list_tasks(status="COMPLETED")
    completed_task = next((t for t in all_tasks if t["id"] == task_id), None)
    assert completed_task is not None
    assert completed_task["status"] == "COMPLETED"
    assert completed_task["completed_at"] is not None

    # 5. DELETE_TASK
    del_res = await tool.execute({"action": "delete", "task_id": task_id})
    assert del_res["success"] is True

    await mem.long_term.close()


@pytest.mark.asyncio
async def test_tasks_reminder_creation(tmp_path):
    db_file = str(tmp_path / "test_reminders.db")
    mem = MemoryManager(db_path=db_file)
    await mem.initialize()
    tool = TaskTool(mem)

    res = await tool.execute({
        "action": "reminder",
        "reminder_text": "Check GATE syllabus completion"
    })
    assert res["success"] is True
    assert res["action"] == "reminder_created"
    assert "Reminder:" in res["data"]["title"]
    await mem.long_term.close()


@pytest.mark.asyncio
async def test_tasks_nlp_integration(tmp_path):
    db_file = str(tmp_path / "test_tasks_nlp.db")
    mem = MemoryManager(db_path=db_file)
    core = JarvisCore(memory_manager=mem)

    # Create task via core handle
    res_create = await core.handle("Create a task to solve 3 LeetCode problems")
    assert res_create["success"] is True
    assert res_create["intent"] == "TASK_CREATE"
    assert "LeetCode" in res_create["response"]

    # List tasks
    res_list = await core.handle("List my pending tasks")
    assert res_list["success"] is True
    assert res_list["intent"] == "TASK_LIST"
    assert len(res_list["data"]["tasks"]) >= 1

    # Complete task
    res_comp = await core.handle("Mark my LeetCode task as complete")
    assert res_comp["success"] is True
    assert res_comp["intent"] == "TASK_COMPLETE"
    assert "COMPLETED" in res_comp["response"]

    await mem.long_term.close()
