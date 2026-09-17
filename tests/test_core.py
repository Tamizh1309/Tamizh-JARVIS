import pytest
from core.jarvis_core import JarvisCore
from memory.memory_manager import MemoryManager
from ai.fallback_provider import FallbackProvider


@pytest.mark.asyncio
async def test_jarvis_core_normal_request(tmp_path):
    db_file = str(tmp_path / "test_core.db")
    memory = MemoryManager(db_path=db_file)
    core = JarvisCore(memory_manager=memory)

    res = await core.handle("Hello JARVIS")
    assert res["success"] is True
    assert res["intent"] == "GENERAL_CHAT"
    assert "response" in res
    assert res["toolUsed"] == "none"
    assert res["memoryUpdated"] is True
    await memory.long_term.close()


@pytest.mark.asyncio
async def test_jarvis_core_empty_and_invalid_request(tmp_path):
    db_file = str(tmp_path / "test_core_err.db")
    memory = MemoryManager(db_path=db_file)
    core = JarvisCore(memory_manager=memory)

    # Empty message
    res = await core.handle("")
    assert res["success"] is False
    assert res["action"] == "EMPTY_MESSAGE"
    assert res["memoryUpdated"] is False

    # Whitespace only
    res_space = await core.handle("    ")
    assert res_space["success"] is False
    assert res_space["action"] == "EMPTY_MESSAGE"
    await memory.long_term.close()


@pytest.mark.asyncio
async def test_jarvis_core_missing_tool_handled_safely(tmp_path):
    db_file = str(tmp_path / "test_core_tool.db")
    memory = MemoryManager(db_path=db_file)
    core = JarvisCore(memory_manager=memory)

    # Remove schedule_tool to test missing tool handler
    core.tools.pop("schedule_tool", None)
    res = await core.handle("What is my schedule for today?")
    assert res["success"] is False
    assert res["action"] == "MISSING_TOOL"
    assert "not registered" in res["response"]
    await memory.long_term.close()


@pytest.mark.asyncio
async def test_jarvis_core_stable_response_schema(tmp_path):
    db_file = str(tmp_path / "test_core_schema.db")
    memory = MemoryManager(db_path=db_file)
    core = JarvisCore(memory_manager=memory)

    res = await core.handle("Explain binary search")
    required_keys = ["success", "intent", "action", "response", "data", "toolUsed", "memoryUpdated"]
    for k in required_keys:
        assert k in res, f"Key '{k}' missing from JarvisCore response schema"
    assert isinstance(res["success"], bool)
    assert isinstance(res["data"], dict)
    await memory.long_term.close()


@pytest.mark.asyncio
async def test_jarvis_core_ai_unavailable_graceful_fallback(tmp_path):
    db_file = str(tmp_path / "test_core_fallback.db")
    memory = MemoryManager(db_path=db_file)
    fallback_ai = FallbackProvider()
    core = JarvisCore(ai_provider=fallback_ai, memory_manager=memory)

    res = await core.handle("Explain binary search")
    assert res["success"] is True
    assert "Binary Search" in res["response"]
    assert "O(log N)" in res["response"]
    await memory.long_term.close()
