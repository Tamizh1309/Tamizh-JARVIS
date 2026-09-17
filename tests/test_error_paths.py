import pytest
import pytest_asyncio
from core.jarvis_core import JarvisCore
from memory.memory_manager import MemoryManager
from security.risk_classifier import RiskClassifier, RiskLevel
from security.action_validator import ActionValidator


@pytest_asyncio.fixture
async def agent(tmp_path):
    db_file = str(tmp_path / "error_test.db")
    memory = MemoryManager(db_path=db_file)
    await memory.initialize()
    core = JarvisCore(memory_manager=memory)
    await core.initialize()
    yield core
    await memory.long_term.close()


@pytest.mark.asyncio
async def test_empty_message_handling(agent):
    """Empty or whitespace-only messages must return clean structured response, not an exception."""
    res = await agent.handle("")
    assert res["success"] is False
    assert res["action"] == "EMPTY_MESSAGE"
    assert "Empty message received" in res["response"]

    res2 = await agent.handle("   ")
    assert res2["success"] is False
    assert res2["action"] == "EMPTY_MESSAGE"


@pytest.mark.asyncio
async def test_missing_tool_error_handling(agent):
    """If planner requests a missing tool, JarvisCore returns a controlled error without throwing."""
    agent.tools.pop("schedule_tool", None)
    res = await agent.handle("Check my schedule")
    assert res["success"] is False
    assert res["action"] == "MISSING_TOOL"
    assert "not registered" in res["response"]
    assert res["data"]["requested_tool"] == "schedule_tool"


@pytest.mark.asyncio
async def test_hazardous_parameter_validation():
    """ActionValidator must block hazardous injection parameters."""
    valid, err = ActionValidator.validate("task_tool", "create", {"title": "Normal task"})
    assert valid is True

    valid_bad, err_bad = ActionValidator.validate("task_tool", "create", {"title": "Task; rm -rf /"})
    assert valid_bad is False
    assert "Potentially hazardous sequence" in err_bad


@pytest.mark.asyncio
async def test_prohibited_critical_action_blocked(agent):
    """Direct destructive terminal / shell execution is strictly blocked."""
    risk = RiskClassifier.classify("os_tool", "format_disk")
    assert risk == RiskLevel.CRITICAL

    auth, reason, level = agent.security.evaluate("shell_tool", "exec_cmd", {"cmd": "whoami"})
    assert auth is False
    assert level == RiskLevel.CRITICAL
    assert "strictly prohibited" in reason


@pytest.mark.asyncio
async def test_high_risk_action_requires_confirmation(agent):
    """High risk action like task deletion requires user confirmation."""
    auth, reason, level = agent.security.evaluate(
        tool_name="task_tool",
        action="delete",
        params={"task_id": 1},
        user_confirmed=False
    )
    assert auth is False
    assert level == RiskLevel.HIGH
    assert "requires explicit user approval" in reason

    # With confirmation, it is authorized
    auth_confirmed, _, _ = agent.security.evaluate(
        tool_name="task_tool",
        action="delete",
        params={"task_id": 1},
        user_confirmed=True
    )
    assert auth_confirmed is True


@pytest.mark.asyncio
async def test_coding_tool_missing_code_graceful_handling():
    """Debug and review without code snippets must return guidance gracefully without error."""
    from tools.coding_tool import CodingTool
    tool = CodingTool()

    debug_res = await tool.execute({"action": "debug"})
    assert debug_res["success"] is True
    assert debug_res["data"]["code_provided"] is False
    assert "No code snippet was provided" in debug_res["message"]

    review_res = await tool.execute({"action": "review"})
    assert review_res["success"] is True
    assert review_res["data"]["code_provided"] is False
    assert "No code snippet was provided" in review_res["message"]


@pytest.mark.asyncio
async def test_invalid_task_id_handling(agent):
    """Attempting to complete or delete an invalid task ID returns controlled response."""
    res = await agent.tools["task_tool"].execute({"action": "complete", "task_id": 99999})
    assert res["success"] is False
    assert "not found" in res["message"].lower()

    del_res = await agent.tools["task_tool"].execute({"action": "delete", "task_id": 99999})
    assert del_res["success"] is False
    assert "not found" in del_res["message"].lower()


@pytest.mark.asyncio
async def test_malformed_ai_response_falls_back_cleanly():
    """If an AI provider returns malformed JSON, coding tool gracefully falls back to AST inspection."""
    from tools.coding_tool import CodingTool
    from ai.provider import AIProvider

    class MalformedAI(AIProvider):
        @property
        def name(self): return "malformed"
        async def is_available(self): return True
        async def generate(self, prompt, system_prompt=None, json_mode=False):
            return "This is not valid JSON at all!"

    tool = CodingTool(ai_provider=MalformedAI())
    res = await tool.execute({
        "action": "debug",
        "code": "def foo():\n    return 42",
        "language": "python"
    })
    assert res["success"] is True
    assert res["data"]["code_provided"] is True
    assert "Static AST" in res["data"]["analysis_type"]
