from core.decision_engine import DecisionEngine


def test_decision_engine_high_priority_task():
    context = {
        "pending_tasks": [
            {"id": 1, "title": "Submit Assignment", "priority": "HIGH", "status": "PENDING"},
            {"id": 2, "title": "Read Article", "priority": "LOW", "status": "PENDING"}
        ],
        "weak_topics": ["Dynamic Programming"],
        "today_study_minutes": 60,
        "available_time": 45,
        "goal": "Software Engineer"
    }

    nba = DecisionEngine.compute_next_best_action(context)
    assert nba["success"] is True
    assert nba["action"] == "EXECUTE_HIGH_PRIORITY_TASK"
    assert nba["title"] == "Submit Assignment"
    assert nba["priority"] == "HIGH"
    assert nba["duration_minutes"] == 45
    assert "Urgent" in nba["reason"]


def test_decision_engine_weak_topic_spaced_revision():
    context = {
        "pending_tasks": [
            {"id": 2, "title": "Optional Cleanup", "priority": "LOW", "status": "PENDING"}
        ],
        "weak_topics": ["TCP Congestion Control"],
        "study_history": [],
        "today_study_minutes": 30,
        "available_time": 45,
        "goal": "GATE CS"
    }

    nba = DecisionEngine.compute_next_best_action(context)
    assert nba["success"] is True
    assert nba["action"] == "REVISION_SESSION"
    assert "TCP Congestion Control" in nba["title"]
    assert nba["priority"] == "HIGH"
    assert "spaced revision" in nba["reason"].lower()


def test_decision_engine_dsa_goal_alignment():
    context = {
        "pending_tasks": [],
        "weak_topics": [],
        "study_history": [],
        "today_study_minutes": 0,
        "available_time": 45,
        "goal": "Software Engineer at Top Tech"
    }

    nba = DecisionEngine.compute_next_best_action(context)
    assert nba["success"] is True
    assert nba["action"] == "DSA_PRACTICE"
    assert "DSA" in nba["title"]
    assert "Software Engineering" in nba["reason"]


def test_decision_engine_output_schema_conformance():
    context = {
        "pending_tasks": [],
        "weak_topics": [],
        "study_history": [],
        "today_study_minutes": 100,
        "available_time": 30,
        "goal": "General"
    }

    nba = DecisionEngine.compute_next_best_action(context)
    assert nba["success"] is True
    assert isinstance(nba["title"], str)
    assert isinstance(nba["reason"], str)
    assert nba["priority"] in ["LOW", "MEDIUM", "HIGH"]
    assert isinstance(nba["duration_minutes"], int)
    assert isinstance(nba["action"], str)
