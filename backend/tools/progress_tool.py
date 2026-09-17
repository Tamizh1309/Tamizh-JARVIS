from typing import Dict, Any
from tools.base_tool import BaseTool
from memory.memory_manager import MemoryManager


class ProgressTool(BaseTool):
    """Tool for analyzing study progress, task completion metrics, and daily briefing."""

    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager

    @property
    def name(self) -> str:
        return "progress_tool"

    @property
    def description(self) -> str:
        return "Aggregates daily progress, completion rates, and study metrics."

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        profile = self.memory.profile.get_profile()
        today_mins = await self.memory.long_term.get_today_study_minutes()
        today_hours = round(today_mins / 60.0, 1)
        target_hours = profile.target_daily_study_hours
        percentage = min(100, int((today_hours / target_hours) * 100)) if target_hours > 0 else 0

        pending_tasks = await self.memory.long_term.list_tasks(status="PENDING")

        msg = f"Daily Briefing: {len(pending_tasks)} pending tasks, {today_hours}h / {target_hours}h studied ({percentage}% complete)."
        data = {
            "pending_tasks_count": len(pending_tasks),
            "today_study_hours": today_hours,
            "target_study_hours": target_hours,
            "completion_percentage": percentage,
        }
        return self.format_output(
            success=True,
            action="daily_briefing",
            data=data,
            message=msg
        )
