from typing import Dict, Any
from tools.base_tool import BaseTool


class CodingTool(BaseTool):
    """Tool for explaining algorithms, data structures, and code assistance."""

    @property
    def name(self) -> str:
        return "coding_tool"

    @property
    def description(self) -> str:
        return "Explains algorithms, data structures, complexities, and code patterns."

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        action = params.get("action", "explain")
        topic = (params.get("topic") or "binary search").lower().strip()

        if "binary search" in topic:
            return {
                "success": True,
                "action": "explain_algorithm",
                "algorithm": "Binary Search",
                "time_complexity": "O(log N)",
                "space_complexity": "O(1) iterative / O(log N) recursive",
                "prerequisite": "Array must be sorted",
                "concept": (
                    "Binary Search operates by repeatedly dividing the search space in half. "
                    "Compare the target value to the middle element of the array: "
                    "if equal, return index; if target is smaller, narrow to left half; "
                    "if greater, narrow to right half."
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
