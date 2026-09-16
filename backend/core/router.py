import re
from typing import Dict, Any, Tuple
from ai.provider import AIProvider


class IntentRouter:
    """Classifies user queries into extensible intent categories."""

    def __init__(self, ai_provider: AIProvider):
        self.ai = ai_provider

    async def route(self, message: str, context: Dict[str, Any] = None) -> Tuple[str, float, Dict[str, Any]]:
        text = message.strip().lower()
        entities = {}

        # 1. High-precision deterministic rules
        if any(w in text for w in ["next best", "what should i study", "what to do", "what should i do", "next action"]):
            return "NEXT_BEST_ACTION", 0.95, entities

        if any(w in text for w in ["create task", "add task", "new task"]):
            # Extract task title if possible
            title = re.sub(r"^(create task|add task|new task)\s*(:|to|-)?\s*", "", message, flags=re.IGNORECASE).strip()
            entities["title"] = title or "New Task"
            return "TASK_CREATE", 0.90, entities

        if any(w in text for w in ["tasks", "list tasks", "my tasks", "pending tasks", "todos", "todo"]):
            return "TASK_LIST", 0.90, entities

        if any(w in text for w in ["briefing", "summary of today", "daily review", "how is today going", "progress"]):
            return "DAILY_BRIEFING", 0.90, entities

        if any(w in text for w in ["gate", "study plan", "revise", "revision", "syllabus", "weak topic"]):
            for topic in ["dbms", "os", "cn", "dsa", "toc", "algorithms"]:
                if topic in text:
                    entities["topic"] = topic.upper()
            return "STUDY_PLAN", 0.88, entities

        if any(w in text for w in ["dsa", "leetcode", "binary search", "linked list", "trees", "graph", "dynamic programming"]):
            return "DSA_PRACTICE", 0.88, entities

        if any(w in text for w in ["code", "debug", "python", "javascript", "react", "algorithm", "function"]):
            return "CODING_HELP", 0.85, entities

        # 2. If provider is available and not pure fallback, query AI provider in json_mode
        if self.ai.name != "fallback":
            try:
                system_prompt = "You are Tamizh JARVIS Intent Router. Classify the user input into ONE intent: [GENERAL_CHAT, NEXT_BEST_ACTION, STUDY_PLAN, TASK_CREATE, TASK_LIST, DAILY_BRIEFING, DSA_PRACTICE, CODING_HELP]. Respond with JSON {intent, confidence, entities}."
                ai_res = await self.ai.generate(prompt=message, system_prompt=system_prompt, json_mode=True)
                import json
                parsed = json.loads(ai_res)
                return parsed.get("intent", "GENERAL_CHAT"), float(parsed.get("confidence", 0.8)), parsed.get("entities", {})
            except Exception:
                pass

        return "GENERAL_CHAT", 0.75, entities
