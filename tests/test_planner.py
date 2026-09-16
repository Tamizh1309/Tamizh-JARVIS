from core.planner import Planner


def test_planner_next_best_action():
    plan = Planner.create_plan("NEXT_BEST_ACTION", {}, {})
    assert plan.tool_name == "study_tool"
    assert plan.action == "recommend"


def test_planner_task_create():
    plan = Planner.create_plan("TASK_CREATE", {"title": "Solve Graph Problems", "priority": "HIGH"}, {})
    assert plan.tool_name == "task_tool"
    assert plan.action == "create"
    assert plan.params["title"] == "Solve Graph Problems"
    assert plan.params["priority"] == "HIGH"


def test_planner_daily_briefing():
    plan = Planner.create_plan("DAILY_BRIEFING", {}, {})
    assert plan.tool_name == "progress_tool"
    assert plan.action == "daily_briefing"


def test_planner_general_chat():
    plan = Planner.create_plan("GENERAL_CHAT", {}, {})
    assert plan.tool_name is None
