import pytest
from tools.coding_tool import CodingTool
from ai.fallback_provider import FallbackProvider


@pytest.mark.asyncio
async def test_personalized_dsa_plan():
    tool = CodingTool(FallbackProvider())
    context = {
        "weak_topics": ["Dynamic Programming", "Graphs"],
        "solved_problems": ["0/1 Knapsack & Subset Sum"],
        "preferred_language": "Python"
    }

    res = await tool.execute({"action": "dsa_practice"}, context=context)
    assert res["success"] is True
    assert res["action"] == "dsa_practice"
    assert res["data"]["focus_area"] == "Dp"
    problems = res["data"]["recommended_problems"]
    assert len(problems) >= 1
    # Solved problem should be filtered out
    assert not any(p["title"] == "0/1 Knapsack & Subset Sum" for p in problems)


@pytest.mark.asyncio
async def test_debug_with_supplied_code():
    tool = CodingTool(FallbackProvider())
    buggy_code = """
def find_target(arr, target):
    for i in range(len(arr)):
        if arr[i] == target:
            return i
    return -1
"""
    res = await tool.execute({
        "action": "debug",
        "code": buggy_code,
        "error": "IndexError: list index out of range",
        "language": "python"
    })
    assert res["success"] is True
    assert res["data"]["code_provided"] is True
    assert "problem_summary" in res["data"]
    assert "likely_cause" in res["data"]
    assert "complexity" in res["data"]


@pytest.mark.asyncio
async def test_code_review_with_supplied_code():
    tool = CodingTool(FallbackProvider())
    sample_code = """
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []
"""
    res = await tool.execute({
        "action": "review",
        "code": sample_code,
        "language": "python"
    })
    assert res["success"] is True
    assert res["data"]["code_provided"] is True
    assert "readability" in res["data"]
    assert "time_complexity" in res["data"]
    assert "space_complexity" in res["data"]
    assert "edge_cases" in res["data"]
    assert "security_concerns" in res["data"]
    assert "improvements" in res["data"]


@pytest.mark.asyncio
async def test_coding_explanation():
    tool = CodingTool(FallbackProvider())
    res = await tool.execute({"action": "explain", "topic": "binary search"})
    assert res["success"] is True
    assert res["action"] == "explain_algorithm"
    assert "Binary Search" in res["data"]["algorithm"]
    assert "O(log N)" in res["data"]["time_complexity"]
    assert "code_example" in res["data"]
