import pytest
from ai.fallback_provider import FallbackProvider
from core.router import IntentRouter


@pytest.fixture
def router():
    return IntentRouter(FallbackProvider())


@pytest.mark.asyncio
async def test_router_all_21_intents(router):
    cases = [
        ("Hello JARVIS, good morning", "GENERAL_CHAT"),
        ("create a task to solve 3 LeetCode problems today", "TASK_CREATE"),
        ("list my pending tasks", "TASK_LIST"),
        ("update task priority to high", "TASK_UPDATE"),
        ("complete my dsa task", "TASK_COMPLETE"),
        ("plan my study schedule for today", "STUDY_PLAN"),
        ("What should I study now?", "NEXT_BEST_ACTION"),
        ("gate preparation strategy and syllabus", "GATE_PREPARATION"),
        ("plan my gate revision", "GATE_REVISION"),
        ("practice dsa problems for arrays", "DSA_PRACTICE"),
        ("show my progress analysis and study hours", "PROGRESS_ANALYSIS"),
        ("what are my weak topics and mistake analysis?", "MISTAKE_ANALYSIS"),
        ("explain binary search algorithm", "CODING_HELP"),
        ("debug this python traceback error", "DEBUG_CODE"),
        ("code review this pull request", "CODE_REVIEW"),
        ("what is my career goal?", "CAREER"),
        ("campus placement drive preparation tips", "PLACEMENT"),
        ("mock interview technical questions", "INTERVIEW"),
        ("check my resume ats score", "RESUME"),
        ("check my daily schedule and timetable", "SCHEDULE"),
        ("remind me to review DBMS transactions at 6 PM", "REMINDER"),
    ]

    for query, expected_intent in cases:
        intent, conf, entities = await router.route(query)
        assert intent == expected_intent, f"Query '{query}' expected '{expected_intent}', got '{intent}'"
        assert conf >= 0.8
