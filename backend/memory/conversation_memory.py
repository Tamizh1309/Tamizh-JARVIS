from typing import List, Dict, Any
from datetime import datetime


class ConversationMemory:
    """Sliding short-term conversation context."""

    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self.history: List[Dict[str, Any]] = []

    def add_turn(self, sender: str, text: str, intent: str = None, metadata: dict = None):
        self.history.append({
            "sender": sender,
            "text": text,
            "intent": intent,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        })
        if len(self.history) > self.max_turns * 2:
            self.history = self.history[-(self.max_turns * 2):]

    def get_recent(self, count: int = 6) -> List[Dict[str, Any]]:
        return self.history[-count:]

    def clear(self):
        self.history = []
