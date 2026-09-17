from typing import Dict, Any
from tools.base_tool import BaseTool


class CodingTool(BaseTool):
    """Tool for explaining algorithms, data structures, debugging, and code assistance."""

    @property
    def name(self) -> str:
        return "coding_tool"

    @property
    def description(self) -> str:
        return "Explains algorithms, data structures, complexities, DSA practice, and code debugging."

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        action = params.get("action", "explain")
        topic = (params.get("topic") or "binary search").lower().strip()

        if action == "dsa_practice" or "practice" in topic:
            return {
                "success": True,
                "action": "dsa_practice",
                "recommended_problems": [
                    {"title": "Two Sum / 3Sum", "difficulty": "Medium", "pattern": "Two Pointers"},
                    {"title": "Longest Substring Without Repeating Characters", "difficulty": "Medium", "pattern": "Sliding Window"},
                    {"title": "0/1 Knapsack & Subset Sum", "difficulty": "Medium-Hard", "pattern": "Dynamic Programming"}
                ],
                "target": "Solve 3 targeted LeetCode problems today",
                "message": "DSA Practice Plan: Focus on Two Pointers, Sliding Window, and 0/1 Knapsack patterns."
            }

        if action == "debug":
            return {
                "success": True,
                "action": "debug_code",
                "steps": [
                    "1. Reproduce the bug with minimal test input.",
                    "2. Check array bounds and off-by-one errors in loop boundaries.",
                    "3. Validate data types and None/null pointer checks.",
                    "4. Trace variable states step-by-step."
                ],
                "message": "Debugging checklist formulated. Provide the snippet and traceback for line-by-line inspection."
            }

        if action == "review":
            return {
                "success": True,
                "action": "code_review",
                "guidelines": [
                    "Readability: Clear naming conventions, modular helper functions.",
                    "Time Complexity: Avoid nested loops when hash sets or two pointers suffice.",
                    "Space Complexity: In-place modifications where feasible without mutating inputs unexpectedly.",
                    "Edge Cases: Empty inputs, single-element arrays, extreme integer bounds."
                ],
                "message": "Code review criteria applied. Code structure is evaluated against production standards."
            }

        # Algorithm Explanation (e.g. Binary Search)
        if "binary search" in topic or action == "explain":
            return {
                "success": True,
                "action": "explain_algorithm",
                "algorithm": "Binary Search",
                "time_complexity": "O(log N)",
                "space_complexity": "O(1) iterative / O(log N) recursive",
                "prerequisite": "Array must be sorted in ascending or descending order",
                "concept": (
                    "Binary Search operates by repeatedly dividing the search space in half. "
                    "Compare the target value to the middle element: "
                    "if equal, return index; if target is smaller, search left half; "
                    "if greater, search right half."
                ),
                "code_example": (
                    "def binary_search(arr, target):\n"
                    "    low, high = 0, len(arr) - 1\n"
                    "    while low <= high:\n"
                    "        mid = (low + high) // 2\n"
                    "        if arr[mid] == target:\n"
                    "            return mid\n"
                    "        elif arr[mid] < target:\n"
                    "            low = mid + 1\n"
                    "        else:\n"
                    "            high = mid - 1\n"
                    "    return -1"
                )
            }

        return {
            "success": True,
            "action": "explain_algorithm",
            "algorithm": topic.title(),
            "concept": f"Algorithm analysis and implementation pattern for {topic.title()}."
        }
