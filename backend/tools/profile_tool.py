from typing import Dict, Any
from tools.base_tool import BaseTool
from memory.memory_manager import MemoryManager


class ProfileTool(BaseTool):
    """Tool for querying and updating user profile, preferences, and career goals."""

    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager

    @property
    def name(self) -> str:
        return "profile_tool"

    @property
    def description(self) -> str:
        return "Manages and retrieves user profile, active career objectives, and study targets."

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        action = params.get("action", "get_career_goal")
        profile = self.memory.profile.get_profile()

        if action == "get_career_goal":
            return {
                "success": True,
                "action": "career_goal",
                "user_name": profile.name,
                "primary_goal": profile.primary_goal,
                "target_daily_study_hours": profile.target_daily_study_hours,
                "subjects": profile.current_subjects,
                "message": f"Your primary goal is: {profile.primary_goal} (Target study: {profile.target_daily_study_hours} hrs/day)."
            }

        return {
            "success": True,
            "action": "user_profile",
            "profile": profile.model_dump()
        }
