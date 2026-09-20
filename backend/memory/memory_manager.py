from typing import Optional, Dict, Any, List
from memory.profile_memory import ProfileMemory
from memory.conversation_memory import ConversationMemory
from memory.long_term_memory import LongTermMemory

VALID_MEMORY_DOMAINS = {
    "USER_PROFILE",
    "PROFILE",
    "GOAL",
    "GOALS",
    "PREFERENCE",
    "TASK",
    "STUDY",
    "ACHIEVEMENT",
    "MISTAKE",
    "REVISION",
    "CONVERSATION_CONTEXT"
}


class MemoryManager:
    """Coordinates profile, conversational context, and persistent storage across the core memory domains."""

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
        """Stores short-term conversation context in memory without polluting long-term SQLite database."""
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
            "current_subjects": profile.current_subjects,
        }

    # --- Domain-Classified CRUD & Search Interface ---

    async def create(self, category: str, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        await self.initialize()
        domain = category.upper().strip()
        return await self.long_term.create_memory(domain, key, value, metadata)

    async def read(self, category: str, key: str) -> Optional[Dict[str, Any]]:
        await self.initialize()
        domain = category.upper().strip()
        return await self.long_term.read_memory(domain, key)

    async def update(self, category: str, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        await self.initialize()
        domain = category.upper().strip()
        return await self.long_term.update_memory(domain, key, value, metadata)

    async def delete(self, category: str, key: str) -> bool:
        await self.initialize()
        domain = category.upper().strip()
        return await self.long_term.delete_memory(domain, key)

    async def search(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        await self.initialize()
        domain = category.upper().strip() if category else None
        return await self.long_term.search_memory(query, domain)

    async def list_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        await self.initialize()
        domain = domain.upper().strip()
        return await self.long_term.list_memory_by_category(domain)

    async def get_relevant_memories(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves long-term memories ranked by relevance to user query.
        Incorporates category alignment, keyword token overlap, recency, and importance.
        """
        import re
        await self.initialize()
        q_lower = query.lower()
        q_tokens = set(re.findall(r"\b[a-zA-Z0-9_\-]{2,}\b", q_lower))

        # Detect primary target category based on query intent
        boosted_categories = set()
        if any(w in q_lower for w in ["goal", "target", "aim", "career", "aspire"]):
            boosted_categories.update(["GOAL", "USER_PROFILE"])
        if any(w in q_lower for w in ["study", "revise", "revision", "exam", "gate", "course", "topic"]):
            boosted_categories.update(["STUDY", "MISTAKE", "REVISION"])
        if any(w in q_lower for w in ["prefer", "like", "favorite", "language"]):
            boosted_categories.add("PREFERENCE")
        if any(w in q_lower for w in ["achieve", "score", "rank", "won"]):
            boosted_categories.add("ACHIEVEMENT")

        all_facts = []
        for cat in ["USER_PROFILE", "GOAL", "PREFERENCE", "TASK", "STUDY", "ACHIEVEMENT", "MISTAKE", "REVISION"]:
            facts = await self.long_term.list_memory_by_category(cat)
            all_facts.extend(facts)

        scored = []
        for fact in all_facts:
            cat = fact.get("category", "").upper()
            key = fact.get("key", "").lower()
            val = str(fact.get("value", "")).lower()

            fact_tokens = set(re.findall(r"\b[a-zA-Z0-9_\-]{2,}\b", f"{key} {val}"))
            overlap = len(q_tokens & fact_tokens)

            cat_boost = 2.0 if cat in boosted_categories else 0.5
            # If query specifically targets a category and fact matches that category
            if boosted_categories and cat not in boosted_categories and overlap == 0:
                continue

            score = (overlap * 1.5) + cat_boost
            if score > 0.6:
                fact_copy = dict(fact)
                fact_copy["relevance_score"] = round(score, 2)
                scored.append(fact_copy)

        scored.sort(key=lambda x: x["relevance_score"], reverse=True)
        return scored[:limit]
