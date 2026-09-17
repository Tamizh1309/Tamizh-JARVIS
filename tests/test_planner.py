from core.planner import Planner


def test_planner_next_best_action():
    plan = Planner.create_plan("NEXT_BEST_ACTION", {}, {})
    assert plan.tool_name == "study_tool"
    assert plan.action == "recommend"


def test_planner_task_create():
    plan = Planner.create_plan("TASK_CREATE", {"title": "Solve 3 LeetCode problems", "priority": "HIGH"}, {})
    assert plan.tool_name == "task_tool"
    assert plan.action == "create"
    assert plan.params["title"] == "Solve 3 LeetCode problems"
    assert plan.params["priority"] == "HIGH"


def test_planner_task_complete():
    plan = Planner.create_plan("TASK_COMPLETE", {"target": "dsa"}, {})
    assert plan.tool_name == "task_tool"
    assert plan.action == "complete"
    assert plan.params["keyword"] == "dsa"


def test_planner_task_list():
    plan = Planner.create_plan("TASK_LIST", {}, {})
    assert plan.tool_name == "task_tool"
    assert plan.action == "list"


def test_planner_gate_revision():
    plan = Planner.create_plan("GATE_REVISION", {}, {})
    assert plan.tool_name == "study_tool"
    assert plan.action == "plan_revision"


def test_planner_career():
    plan = Planner.create_plan("CAREER", {"goal": "Software Engineer", "action": "set_goal"}, {})
    assert plan.tool_name == "profile_tool"
    assert plan.action == "set_goal"
    assert plan.params["goal"] == "Software Engineer"


def test_planner_coding_help():
    plan = Planner.create_plan("CODING_HELP", {"topic": "binary search"}, {})
    assert plan.tool_name == "coding_tool"
    assert plan.action == "explain"


def test_planner_general_chat():
    plan = Planner.create_plan("GENERAL_CHAT", {}, {})
    assert plan.tool_name is None
    assert plan.action == "respond"
