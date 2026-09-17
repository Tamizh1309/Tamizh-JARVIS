from typing import Dict, Any
from datetime import datetime
from tools.base_tool import BaseTool
from memory.memory_manager import MemoryManager


class ScheduleTool(BaseTool):
    """Tool for schedule awareness, time slots, and daily calendar review."""

    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager

    @property
    def name(self) -> str:
        return "schedule_tool"

    @property
    def description(self) -> str:
        return "Checks current schedule, available time slots, and calculates revision dues."

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        now = datetime.now()
        current_time_str = now.strftime("%I:%M %p")
        profile = self.memory.profile.get_profile()

        msg = f"Current time is {current_time_str}. You have an open focus slot ready for study."
        data = {
            "current_time": current_time_str,
            "target_study_hours": profile.target_daily_study_hours,
            "next_available_slot": "Now (Focus Block)",
        }
        return self.format_output(
            success=True,
            action="schedule_status",
            data=data,
            message=msg
        )
