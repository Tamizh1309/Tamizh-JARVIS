from typing import Dict, Any, Optional
from memory.memory_manager import MemoryManager
from core.conversational_context import get_context_resolver


class ContextManager:
    """Aggregates and formats session context, user goals, and active state."""

    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager
        self.resolver = get_context_resolver()

    async def build_context(self, user_input: str, request_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        summary = await self.memory.get_active_context_summary()
        recent_history = self.memory.get_conversation_context(count=4)
        study_hist = await self.memory.long_term.get_study_history(limit=5)

        # Entity resolution for anaphora / coreferences
        _, resolved_entities = self.resolver.resolve_references(user_input)

        merged_context = {
            "user_name": summary.get("user_name"),
            "goal": summary.get("goal"),
            "target_hours": summary.get("target_hours"),
            "today_study_minutes": summary.get("today_study_minutes"),
            "pending_tasks": summary.get("pending_tasks", []),
            "weak_topics": summary.get("weak_topics", []),
            "study_history": study_hist,
            "recent_turns": recent_history,
            "resolved_entities": resolved_entities,
            "active_entities": self.resolver.state.to_dict(),
        }

        if request_context:
            merged_context.update(request_context)

        return merged_context
