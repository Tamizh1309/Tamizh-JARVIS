from typing import Optional, Dict, Any, List
from memory.profile_memory import ProfileMemory
from memory.conversation_memory import ConversationMemory
from memory.long_term_memory import LongTermMemory


class MemoryManager:
    """Coordinates profile, conversational context, and persistent storage across the 14 memory domains."""

    def __init__(self, db_path: Optional[str] = None):
        self.long_term = LongTermMemory(db_path=db_path)
        self.profile = ProfileMemory(long_term=self.long_term)
        self.conversation = ConversationMemory()

    async def initialize(self):
        await self.long_term.init_db()
        await self.profile.load()

    def get_user_profile(self) -> dict:
        return self.profile.get_profile().model_dump()

    def get_conversation_context(self, count: int = 5) -> List[Dict[str, Any]]:
        return self.conversation.get_recent(count=count)

    def record_interaction(self, sender: str, text: str, intent: str = None, metadata: dict = None):
        self.conversation.add_turn(sender, text, intent, metadata)

    async def get_active_context_summary(self) -> dict:
        await self.initialize()
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

    # --- Direct CRUD and Search Interface (Phase 4 Section 6) ---

    async def create(self, category: str, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        await self.initialize()
        return await self.long_term.create_memory(category, key, value, metadata)

    async def read(self, category: str, key: str) -> Optional[Dict[str, Any]]:
        await self.initialize()
        return await self.long_term.read_memory(category, key)

    async def update(self, category: str, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        await self.initialize()
        return await self.long_term.update_memory(category, key, value, metadata)

    async def delete(self, category: str, key: str) -> bool:
        await self.initialize()
        return await self.long_term.delete_memory(category, key)

    async def search(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        await self.initialize()
        return await self.long_term.search_memory(query, category)
