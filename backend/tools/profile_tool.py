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

        if action in ["set_goal", "update_goal"]:
            new_goal = params.get("goal")
            if not new_goal:
                return {"success": False, "error": "Goal text is required."}
            await self.memory.profile.set_goal(new_goal)
            return {
                "success": True,
                "action": "goal_updated",
                "primary_goal": new_goal,
                "message": f"Career goal successfully updated to: \"{new_goal}\"."
            }

        if action in ["get_career_goal", "career_goal"]:
            profile = self.memory.profile.get_profile()
            return {
                "success": True,
                "action": "career_goal",
                "user_name": profile.name,
                "primary_goal": profile.primary_goal,
                "target_daily_study_hours": profile.target_daily_study_hours,
                "subjects": profile.current_subjects,
                "message": f"Your primary goal is: {profile.primary_goal} (Target study: {profile.target_daily_study_hours} hrs/day)."
            }

        if action in ["placement", "interview", "resume"]:
            profile = self.memory.profile.get_profile()
            return {
                "success": True,
                "action": action,
                "user_name": profile.name,
                "primary_goal": profile.primary_goal,
                "recommendation": (
                    f"Career & Placement Strategy for {profile.name}:\n"
                    "1. Resume: Quantify metrics (e.g. latency reduced, users served).\n"
                    "2. Core DSA: Target Top 100 Liked LeetCode questions.\n"
                    "3. System Design: Review distributed caches, database indexing, and microservices."
                )
            }

        profile = self.memory.profile.get_profile()
        return {
            "success": True,
            "action": "user_profile",
            "profile": profile.model_dump()
        }
