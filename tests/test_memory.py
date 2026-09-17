import os
import pytest
from memory.memory_manager import MemoryManager


@pytest.mark.asyncio
async def test_memory_profile_persistence_across_restarts(tmp_path):
    db_file = str(tmp_path / "test_persist.db")

    # Instance 1: Set goal
    mem1 = MemoryManager(db_path=db_file)
    await mem1.initialize()
    await mem1.profile.set_goal("Senior Software Engineer at Google")
    profile1 = mem1.get_user_profile()
    assert profile1["primary_goal"] == "Senior Software Engineer at Google"
    await mem1.long_term.close()

    # Instance 2: Simulate backend restart with same database
    mem2 = MemoryManager(db_path=db_file)
    await mem2.initialize()
    profile2 = mem2.get_user_profile()
    assert profile2["primary_goal"] == "Senior Software Engineer at Google"
    await mem2.long_term.close()


@pytest.mark.asyncio
async def test_memory_crud_and_search(tmp_path):
    db_file = str(tmp_path / "test_crud.db")
    mem = MemoryManager(db_path=db_file)
    await mem.initialize()

    # Create
    created = await mem.create("GOALS", "target_role", "Distributed Systems Engineer", {"tier": "Tier 1"})
    assert created is True

    # Read
    item = await mem.read("GOALS", "target_role")
    assert item is not None
    assert item["value"] == "Distributed Systems Engineer"

    # Update
    updated = await mem.update("GOALS", "target_role", "Principal Architect")
    assert updated is True
    item_updated = await mem.read("GOALS", "target_role")
    assert item_updated["value"] == "Principal Architect"

    # Search
    search_res = await mem.search("Architect")
    assert len(search_res) >= 1
    assert search_res[0]["key"] == "target_role"

    # Delete
    deleted = await mem.delete("GOALS", "target_role")
    assert deleted is True
    item_deleted = await mem.read("GOALS", "target_role")
    assert item_deleted is None

    await mem.long_term.close()


@pytest.mark.asyncio
async def test_memory_tasks_crud_full_schema(tmp_path):
    db_file = str(tmp_path / "test_tasks.db")
    mem = MemoryManager(db_path=db_file)
    await mem.initialize()

    # 1. Create task
    task_id = await mem.long_term.create_task(
        title="Complete 3 LeetCode Problems",
        description="Two Pointers and Sliding Window",
        priority="HIGH",
        due_at="2026-10-01",
        category="DSA",
        source="USER"
    )
    assert task_id > 0

    # 2. List tasks
    tasks = await mem.long_term.list_tasks(status="PENDING")
    created_task = next(t for t in tasks if t["id"] == task_id)
    assert created_task["title"] == "Complete 3 LeetCode Problems"
    assert created_task["priority"] == "HIGH"
    assert created_task["category"] == "DSA"

    # 3. Update task
    updated = await mem.long_term.update_task(task_id, {"priority": "LOW", "description": "Updated desc"})
    assert updated is True
    t = await mem.long_term.get_task(task_id)
    assert t["priority"] == "LOW"
    assert t["description"] == "Updated desc"

    # 4. Complete task
    completed = await mem.long_term.complete_task(task_id)
    assert completed is True
    t_done = await mem.long_term.get_task(task_id)
    assert t_done["status"] == "COMPLETED"
    assert t_done["completed_at"] is not None

    # 5. Delete task
    deleted = await mem.long_term.delete_task(task_id)
    assert deleted is True
    t_del = await mem.long_term.get_task(task_id)
    assert t_del is None

    await mem.long_term.close()


@pytest.mark.asyncio
async def test_memory_domain_classification(tmp_path):
    db_file = str(tmp_path / "test_domains.db")
    mem = MemoryManager(db_path=db_file)
    await mem.initialize()

    # Test distinct memory domain classifications
    domains = ["USER_PROFILE", "GOAL", "PREFERENCE", "TASK", "STUDY", "ACHIEVEMENT", "MISTAKE", "REVISION"]
    for d in domains:
        k = f"key_{d.lower()}"
        v = f"val_{d.lower()}"
        ok = await mem.create(d, k, v)
        assert ok is True
        item = await mem.read(d, k)
        assert item is not None
        assert item["value"] == v

    await mem.long_term.close()


@pytest.mark.asyncio
async def test_conversational_chat_not_persisted_as_permanent_facts(tmp_path):
    db_file = str(tmp_path / "test_chat_isolation.db")
    mem = MemoryManager(db_path=db_file)
    await mem.initialize()

    # Record general chat interaction
    mem.record_interaction("user", "How is the weather today?", "GENERAL_CHAT")
    mem.record_interaction("jarvis", "I am here to assist your productivity and study!", "GENERAL_CHAT")

    # Check conversation context (short-term window)
    ctx = mem.get_conversation_context(count=5)
    assert len(ctx) == 2
    assert ctx[0]["text"] == "How is the weather today?"

    # Crucial assertion: long_term SQLite memory_records must NOT have this chat as a fact!
    facts = await mem.long_term.get_facts()
    assert not any("weather" in str(f.get("value", "")).lower() for f in facts)

    await mem.long_term.close()
