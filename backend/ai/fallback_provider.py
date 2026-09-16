import json
import logging
import re
from typing import Optional
from ai.provider import AIProvider

logger = logging.getLogger("tamizh_jarvis.ai.fallback")


class FallbackProvider(AIProvider):
    """Deterministic intelligence engine used when external LLMs are unavailable or offline."""

    @property
    def name(self) -> str:
        return "fallback"

    async def is_available(self) -> bool:
        return True

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
    ) -> str:
        text = prompt.strip().lower()

        if json_mode:
            # Deterministic intent extraction
            intent = "GENERAL_CHAT"
            confidence = 0.85

            if any(w in text for w in ["next best", "what should i do", "what to do", "what should i study", "recommend"]):
                intent = "NEXT_BEST_ACTION"
            elif any(w in text for w in ["study", "gate", "syllabus", "subject", "revise", "revision"]):
                intent = "STUDY_PLAN"
            elif any(w in text for w in ["create task", "add task", "new task", "remind me to"]):
                intent = "TASK_CREATE"
            elif any(w in text for w in ["tasks", "list tasks", "my tasks", "pending tasks", "todo"]):
                intent = "TASK_LIST"
            elif any(w in text for w in ["briefing", "summary of today", "daily review", "status"]):
                intent = "DAILY_BRIEFING"
            elif any(w in text for w in ["dsa", "leetcode", "array", "tree", "graph", "algorithm"]):
                intent = "DSA_PRACTICE"
            elif any(w in text for w in ["code", "debug", "python", "javascript", "react", "bug"]):
                intent = "CODING_HELP"

            return json.dumps({
                "intent": intent,
                "confidence": confidence,
                "entities": self._extract_entities(prompt)
            })

        # Plain text generation fallback
        if "next best" in text or "what should i study" in text or "what to do" in text:
            return "Based on your study profile and priority algorithms, your Next Best Action is: Revise DBMS Transactions for 45 minutes."
        elif "hello" in text or "hi" in text or "hey" in text:
            return "Greetings. Tamizh JARVIS is online. What would you like to plan, study, or execute?"
        elif "task" in text:
            return "Task engine is ready. You can ask me to create, list, or update tasks."

        return f"Tamizh JARVIS processed your request: '{prompt}'. System is ready to assist your productivity and study goals."

    def _extract_entities(self, text: str) -> dict:
        entities = {}
        # Extract duration
        duration_match = re.search(r"(\d+)\s*(mins?|minutes?|hours?|hrs?)", text, re.IGNORECASE)
        if duration_match:
            entities["duration"] = duration_match.group(0)
        # Extract potential topic
        for topic in ["dbms", "os", "operating systems", "dsa", "algorithms", "computer networks", "toc", "compiler design"]:
            if topic in text.lower():
                entities["topic"] = topic.upper()
                break
        return entities
