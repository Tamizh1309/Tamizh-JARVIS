from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    name: str = "Tamizharasan"
    primary_goal: str = "GATE CS 2026 & Software Engineering Mastery"
    target_daily_study_hours: float = 3.5
    current_subjects: List[str] = Field(
        default_factory=lambda: [
            "Database Management Systems",
            "Operating Systems",
            "Data Structures & Algorithms",
            "Computer Networks",
            "Theory of Computation",
        ]
    )
    weak_topics: List[str] = Field(
        default_factory=lambda: [
            "DBMS Transactions & Concurrency Control",
            "Dynamic Programming",
            "TCP Congestion Control",
        ]
    )
    preferred_study_slot_mins: int = 45


class ProfileMemory:
    """Manages user profile, preferences, and active goals with SQLite persistence."""

    def __init__(self, long_term=None):
        self._profile = UserProfile()
        self.long_term = long_term

    async def load(self):
        """Loads profile from persistent storage if available."""
        if self.long_term:
            record = await self.long_term.read_memory("USER_PROFILE", "main")
            if record and isinstance(record.get("value"), dict):
                try:
                    self._profile = UserProfile(**record["value"])
                except Exception:
                    pass
            # Also check if GOALS record exists
            goal_rec = await self.long_term.read_memory("GOALS", "primary_goal")
            if goal_rec and isinstance(goal_rec.get("value"), str):
                self._profile.primary_goal = goal_rec["value"]

    def get_profile(self) -> UserProfile:
        return self._profile

    async def update_profile(self, updates: Dict[str, Any]) -> UserProfile:
        current_data = self._profile.model_dump()
        current_data.update(updates)
        self._profile = UserProfile(**current_data)
        if self.long_term:
            await self.long_term.create_memory("USER_PROFILE", "main", self._profile.model_dump())
            if "primary_goal" in updates:
                await self.long_term.create_memory("GOALS", "primary_goal", updates["primary_goal"])
        return self._profile

    async def set_goal(self, goal: str) -> UserProfile:
        self._profile.primary_goal = goal.strip()
        if self.long_term:
            await self.long_term.create_memory("GOALS", "primary_goal", self._profile.primary_goal)
            await self.long_term.create_memory("USER_PROFILE", "main", self._profile.model_dump())
        return self._profile

    async def add_weak_topic(self, topic: str):
        if topic not in self._profile.weak_topics:
            self._profile.weak_topics.append(topic)
            if self.long_term:
                await self.long_term.create_memory("USER_PROFILE", "main", self._profile.model_dump())
                await self.long_term.create_memory("TOPIC_MASTERY", f"weak_{topic}", {"topic": topic, "status": "WEAK"})

    async def remove_weak_topic(self, topic: str):
        if topic in self._profile.weak_topics:
            self._profile.weak_topics.remove(topic)
            if self.long_term:
                await self.long_term.create_memory("USER_PROFILE", "main", self._profile.model_dump())
                await self.long_term.delete_memory("TOPIC_MASTERY", f"weak_{topic}")
