import pytest
import pytest_asyncio
from memory.memory_manager import MemoryManager
from tools.study_tool import StudyTool
from tools.progress_tool import ProgressTool


@pytest_asyncio.fixture
async def memory_mgr(tmp_path):
    db_file = str(tmp_path / "study_test.db")
    mgr = MemoryManager(db_path=db_file)
    await mgr.initialize()
    yield mgr
    await mgr.long_term.close()


@pytest.mark.asyncio
async def test_study_engine_data_flow(memory_mgr):
    study_tool = StudyTool(memory_mgr)
    progress_tool = ProgressTool(memory_mgr)

    # 1. Check initial weak topics
    weak_res = await study_tool.execute({"action": "weak_topics"})
    assert weak_res["success"] is True
    assert len(weak_res["weak_topics"]) >= 2
    assert "DBMS Transactions & Concurrency Control" in weak_res["weak_topics"]

    # 2. Log multiple real study sessions
    await study_tool.execute({
        "action": "log_session",
        "subject": "Operating Systems",
        "topic": "Process Synchronization & Semaphores",
        "duration": 60
    })
    await study_tool.execute({
        "action": "log_session",
        "subject": "Computer Networks",
        "topic": "TCP Congestion Control",
        "duration": 30
    })

    # 3. Check today study minutes
    today_mins = await memory_mgr.long_term.get_today_study_minutes()
    assert today_mins == 90

    # 4. Check dynamic calculation in progress tool
    briefing = await progress_tool.execute({"action": "briefing"})
    assert briefing["today_study_hours"] == 1.5
    # 1.5h of 3.5h target is ~42%
    assert briefing["completion_percentage"] == int((1.5 / 3.5) * 100)

    # 5. History contains both sessions in reverse chronological order
    hist = await study_tool.execute({"action": "history"})
    assert len(hist["sessions"]) == 2
    assert hist["sessions"][0]["topic"] == "TCP Congestion Control"
    assert hist["sessions"][1]["topic"] == "Process Synchronization & Semaphores"
