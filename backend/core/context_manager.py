from typing import Dict, Any, Optional
from memory.memory_manager import MemoryManager


class ContextManager:
    """Aggregates and formats session context, user goals, and active state."""

    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager

    async def build_context(self, user_input: str, request_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        summary = await self.memory.get_active_context_summary()
        recent_history = self.memory.get_conversation_context(count=4)

        merged_context = {
            "user_name": summary.get("user_name"),
            "goal": summary.get("goal"),
            "target_hours": summary.get("target_hours"),
            "today_study_minutes": summary.get("today_study_minutes"),
            "pending_tasks": summary.get("pending_tasks", []),
            "weak_topics": summary.get("weak_topics", []),
            "recent_turns": recent_history,
        }

        if request_context:
            merged_context.update(request_context)

        return merged_context
