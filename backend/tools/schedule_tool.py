"""ScheduleTool for intelligent timetable management and evening/daily routine planning."""
from typing import Dict, Any, Optional
from datetime import datetime
from tools.base_tool import BaseTool
from memory.memory_manager import MemoryManager


class ScheduleTool(BaseTool):
    """Tool for schedule awareness, time slots, and personalized daily/evening planning."""

    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager

    @property
    def name(self) -> str:
        return "schedule_tool"

    @property
    def description(self) -> str:
        return "Checks current schedule, available time slots, and generates structured evening/daily focus plans."

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        now = datetime.now()
        current_time_str = now.strftime("%I:%M %p")
        current_hour = now.hour
        today_date = now.strftime("%Y-%m-%d")

        profile = self.memory.profile.get_profile()
        target_hours = profile.target_daily_study_hours
        weak_topics = profile.weak_topics
        goal = profile.primary_goal

        # Retrieve real tasks and study history
        pending_tasks = await self.memory.long_term.list_tasks(status="PENDING")
        urgent_tasks = [t for t in pending_tasks if t.get("priority") == "HIGH"]
        study_history = await self.memory.long_term.get_study_history(limit=10)
        today_minutes = sum(s.get("duration", 0) for s in study_history if s.get("timestamp", "").startswith(today_date))
        today_hours = round(today_minutes / 60.0, 1)
        remaining_hours = max(0.0, round(target_hours - today_hours, 1))

        action_type = params.get("plan_type", "general")
        is_evening = "evening" in action_type.lower() or current_hour >= 17

        # Synthesize structured time blocks based on evidence
        blocks = []
        if urgent_tasks:
            top_task = urgent_tasks[0]
            blocks.append({
                "time_slot": "Block 1 (Immediate Focus: 45m)",
                "activity": f"Complete Urgent Task: '{top_task['title']}'",
                "category": top_task.get("category", "Task"),
                "priority": "HIGH"
            })
        elif pending_tasks:
            top_task = pending_tasks[0]
            blocks.append({
                "time_slot": "Block 1 (Action Item: 30m)",
                "activity": f"Address Backlog Task: '{top_task['title']}'",
                "category": top_task.get("category", "Task"),
                "priority": "MEDIUM"
            })

        # Block 2: Study or Revision
        if weak_topics:
            target_topic = weak_topics[0]
            blocks.append({
                "time_slot": "Block 2 (Core Study Session: 50m)",
                "activity": f"Revise High-Yield Weak Topic: '{target_topic}'",
                "category": "GATE / Engineering Focus",
                "goal_alignment": goal
            })
        else:
            blocks.append({
                "time_slot": "Block 2 (Core Study Session: 45m)",
                "activity": f"Practice Core Problems towards {goal}",
                "category": "Core Competency"
            })

        # Block 3: Light Review & Wind Down
        blocks.append({
            "time_slot": "Block 3 (Consolidation: 20m)",
            "activity": "Log completed study minutes, mistake notebook review, and tomorrow's preparation.",
            "category": "Review"
        })

        # Format user response
        title_header = "Evening Focus Plan" if is_evening else "Daily Productivity & Study Plan"
        plan_lines = [
            f"Current time is {current_time_str}. === {title_header} ===",
            f"Target Goal: {goal} | Logged Today: {today_hours}h / {target_hours}h (Remaining: {remaining_hours}h)",
            f"Active Backlog: {len(pending_tasks)} pending tasks ({len(urgent_tasks)} high priority)\n"
        ]
        for b in blocks:
            plan_lines.append(f"• {b['time_slot']}\n  -> {b['activity']}")

        msg = "\n".join(plan_lines)

        data = {
            "current_time": current_time_str,
            "target_daily_study_hours": target_hours,
            "logged_today_hours": today_hours,
            "remaining_study_hours": remaining_hours,
            "pending_tasks_count": len(pending_tasks),
            "urgent_tasks_count": len(urgent_tasks),
            "schedule_blocks": blocks,
        }

        return self.format_output(
            success=True,
            action="planned_schedule",
            data=data,
            message=msg
        )
