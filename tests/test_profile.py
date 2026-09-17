import pytest
from core.jarvis_core import JarvisCore
from memory.memory_manager import MemoryManager
from tools.profile_tool import ProfileTool


@pytest.mark.asyncio
async def test_career_goal_persistence_and_retrieval(tmp_path):
    db_file = str(tmp_path / "test_profile_goal.db")

    # Instance 1: Set career goal
    mem1 = MemoryManager(db_path=db_file)
    core1 = JarvisCore(memory_manager=mem1)
    res_set = await core1.handle("My goal is to become a Distributed Systems Engineer")
    assert res_set["success"] is True
    assert res_set["intent"] == "CAREER"
    assert "Distributed Systems Engineer" in res_set["response"]
    await mem1.long_term.close()

    # Instance 2: Simulate restart with new memory & core instance
    mem2 = MemoryManager(db_path=db_file)
    core2 = JarvisCore(memory_manager=mem2)
    res_get = await core2.handle("What is my career goal?")
    assert res_get["success"] is True
    assert res_get["intent"] == "CAREER"
    assert "Distributed Systems Engineer" in res_get["response"]
    assert res_get["data"]["primary_goal"] == "Distributed Systems Engineer"
    await mem2.long_term.close()


@pytest.mark.asyncio
async def test_profile_tool_placement_and_interview_uses_stored_data(tmp_path):
    db_file = str(tmp_path / "test_profile_tools.db")
    mem = MemoryManager(db_path=db_file)
    await mem.initialize()
    await mem.profile.set_goal("Senior Backend Architect")
    tool = ProfileTool(mem)

    # Placement roadmap
    place_res = await tool.execute({"action": "placement"})
    assert place_res["success"] is True
    assert "Senior Backend Architect" in place_res["data"]["primary_goal"]

    # Interview prep
    int_res = await tool.execute({"action": "interview"})
    assert int_res["success"] is True
    assert len(int_res["data"]["sample_questions"]) >= 2
    assert "Senior Backend Architect" in int_res["message"]

    await mem.long_term.close()


@pytest.mark.asyncio
async def test_profile_tool_resume_analysis_real_input(tmp_path):
    db_file = str(tmp_path / "test_resume.db")
    mem = MemoryManager(db_path=db_file)
    await mem.initialize()
    tool = ProfileTool(mem)

    # 1. Missing resume content returns helpful guidance
    no_content_res = await tool.execute({"action": "resume"})
    assert no_content_res["success"] is True
    assert no_content_res["data"]["resume_provided"] is False
    assert "No resume content was provided" in no_content_res["message"]

    # 2. Supplied resume content undergoes metric and action verb analysis
    resume_sample = """
    Software Engineer with experience in backend microservices.
    - Architected REST APIs serving 5000 requests per minute with 35% latency reduction.
    - Implemented Redis caching layers reducing database load by 40%.
    - Engineered automated CI/CD deployment pipelines on Docker.
    """
    analyzed_res = await tool.execute({"action": "resume", "resume_text": resume_sample})
    assert analyzed_res["success"] is True
    assert analyzed_res["data"]["resume_provided"] is True
    assert analyzed_res["data"]["ats_score"] > 60
    assert len(analyzed_res["data"]["action_verbs_detected"]) >= 2
    assert len(analyzed_res["data"]["metrics_detected"]) >= 2

    await mem.long_term.close()
