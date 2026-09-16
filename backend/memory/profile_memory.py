from typing import Dict, Any, List
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
    """Manages long-term user preferences, profile, and active goals."""

    def __init__(self):
        self._profile = UserProfile()

    def get_profile(self) -> UserProfile:
        return self._profile

    def update_profile(self, updates: Dict[str, Any]) -> UserProfile:
        current_data = self._profile.model_dump()
        current_data.update(updates)
        self._profile = UserProfile(**current_data)
        return self._profile

    def add_weak_topic(self, topic: str):
        if topic not in self._profile.weak_topics:
            self._profile.weak_topics.append(topic)

    def remove_weak_topic(self, topic: str):
        if topic in self._profile.weak_topics:
            self._profile.weak_topics.remove(topic)
