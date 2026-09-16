from typing import Optional, Dict, Any, List
from memory.profile_memory import ProfileMemory
from memory.conversation_memory import ConversationMemory
from memory.long_term_memory import LongTermMemory


class MemoryManager:
    """Coordinates profile, conversational context, and persistent storage."""

    def __init__(self, db_path: Optional[str] = None):
        self.profile = ProfileMemory()
        self.conversation = ConversationMemory()
        self.long_term = LongTermMemory(db_path=db_path)

    async def initialize(self):
        await self.long_term.init_db()

    def get_user_profile(self) -> dict:
        return self.profile.get_profile().model_dump()

    def get_conversation_context(self, count: int = 5) -> List[Dict[str, Any]]:
        return self.conversation.get_recent(count=count)

    def record_interaction(self, sender: str, text: str, intent: str = None, metadata: dict = None):
        self.conversation.add_turn(sender, text, intent, metadata)

    async def get_active_context_summary(self) -> dict:
        profile = self.profile.get_profile()
        tasks = await self.long_term.list_tasks(status="PENDING")
        today_mins = await self.long_term.get_today_study_minutes()

        return {
            "user_name": profile.name,
            "goal": profile.primary_goal,
            "target_hours": profile.target_daily_study_hours,
            "today_study_minutes": today_mins,
            "pending_tasks_count": len(tasks),
            "pending_tasks": tasks[:5],
            "weak_topics": profile.weak_topics,
        }
