import pytest
from core.jarvis_core import JarvisCore
from core.planner import Planner
from tools.base_tool import BaseTool

ALL_INTENTS = [
    "GENERAL_CHAT",
    "TASK_CREATE",
    "TASK_LIST",
    "TASK_UPDATE",
    "TASK_COMPLETE",
    "REMINDER",
    "STUDY_PLAN",
    "NEXT_BEST_ACTION",
    "GATE_PREPARATION",
    "GATE_REVISION",
    "DSA_PRACTICE",
    "CODING_HELP",
    "DEBUG_CODE",
    "CODE_REVIEW",
    "MISTAKE_ANALYSIS",
    "PROGRESS_ANALYSIS",
    "CAREER",
    "PLACEMENT",
    "INTERVIEW",
    "RESUME",
    "SCHEDULE",
]


@pytest.fixture
def jarvis():
    return JarvisCore()


def test_every_intent_routes_to_registered_tool_or_ai(jarvis):
    """
    Phase 5 Requirement 4 & 13:
    Every planner result must satisfy:
    if plan.tool_name is not None:
        plan.tool_name MUST exist in JarvisCore.tools
    There must be NO disconnected routes.
    """
    sample_entities = {
        "title": "Solve LeetCode",
        "priority": "HIGH",
        "target": "dsa",
        "topic": "binary search",
        "goal": "Principal Engineer",
        "action": "set_goal",
        "reminder_text": "Study networking",
        "type": "gate_revision_plan",
    }
    sample_context = {"user_name": "Tamizharasan"}

    disconnected_routes = []

    for intent in ALL_INTENTS:
        plan = Planner.create_plan(intent, sample_entities, sample_context)

        if plan.tool_name is not None:
            if plan.tool_name not in jarvis.tools:
                disconnected_routes.append((intent, plan.tool_name))
            else:
                tool = jarvis.tools[plan.tool_name]
                assert isinstance(tool, BaseTool), f"Tool {plan.tool_name} must inherit from BaseTool"
                assert tool.name == plan.tool_name

    assert len(disconnected_routes) == 0, f"Found disconnected routes: {disconnected_routes}"


def test_required_tool_registry_complete(jarvis):
    """Phase 5 Requirement 2: Audit required tool registry."""
    required_tools = [
        "task_tool",
        "study_tool",
        "schedule_tool",
        "progress_tool",
        "profile_tool",
        "coding_tool",
    ]
    for rt in required_tools:
        assert rt in jarvis.tools, f"Required tool '{rt}' is missing from JarvisCore registry"
        tool = jarvis.get_tool(rt)
        assert tool is not None
        assert tool.name == rt
        assert tool.description is not None and len(tool.description) > 0


def test_validate_tool_registry_method(jarvis):
    """Verifies JarvisCore's built-in registry validator."""
    assert jarvis.validate_tool_registry() is True


def test_unregistered_tool_detection():
    """Verifies that an unknown tool planned is detected and handled cleanly."""
    jarvis = JarvisCore()
    # Temporarily remove a tool
    saved_tool = jarvis.tools.pop("coding_tool")
    try:
        plan = Planner.create_plan("CODING_HELP", {"topic": "binary search"}, {})
        assert plan.tool_name == "coding_tool"
        assert plan.tool_name not in jarvis.tools
    finally:
        jarvis.tools["coding_tool"] = saved_tool
