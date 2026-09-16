import pytest
from memory.memory_manager import MemoryManager


@pytest.mark.asyncio
async def test_memory_profile():
    mem = MemoryManager(db_path=":memory:")
    await mem.initialize()

    profile = mem.get_user_profile()
    assert "name" in profile
    assert profile["name"] == "Tamizharasan"
    assert "GATE" in profile["primary_goal"]


@pytest.mark.asyncio
async def test_memory_conversation_history():
    mem = MemoryManager(db_path=":memory:")
    await mem.initialize()

    mem.record_interaction("user", "Hello JARVIS", intent="GENERAL_CHAT")
    mem.record_interaction("jarvis", "Hello Tamizh", intent="GENERAL_CHAT")

    history = mem.get_conversation_context(count=2)
    assert len(history) == 2
    assert history[0]["sender"] == "user"
    assert history[1]["sender"] == "jarvis"


@pytest.mark.asyncio
async def test_memory_tasks_crud():
    mem = MemoryManager(db_path=":memory:")
    await mem.initialize()

    task_id = await mem.long_term.create_task("Test Task", "Test Description", "HIGH")
    assert task_id > 0

    tasks = await mem.long_term.list_tasks()
    assert any(t["id"] == task_id and t["title"] == "Test Task" for t in tasks)

    updated = await mem.long_term.update_task_status(task_id, "COMPLETED")
    assert updated is True

    pending_tasks = await mem.long_term.list_tasks(status="PENDING")
    assert not any(t["id"] == task_id for t in pending_tasks)
