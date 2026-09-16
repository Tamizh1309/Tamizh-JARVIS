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

        # 1. Career Goal
        if any(w in text for w in ["career goal", "my goal", "primary goal", "career roadmap", "my career"]):
            return "CAREER_GOAL", 0.95, entities

        # 2. Weak Topics
        if any(w in text for w in ["weak topic", "weak topics", "topics i am weak", "topics to improve"]):
            return "WEAK_TOPICS", 0.95, entities

        # 3. Next Best Action
        if any(w in text for w in ["next best", "what should i study", "what to do", "what should i do", "next action"]):
            return "NEXT_BEST_ACTION", 0.95, entities

        # 4. Task Create (check before Task Complete to allow 'create task: Complete Quiz')
        if re.search(r"\b(create\s+(?:a\s+)?task|add\s+(?:a\s+)?task|new\s+task)\b", text):
            title = re.sub(r"^(?:please\s+)?(?:create\s+(?:a\s+)?task|add\s+(?:a\s+)?task|new\s+task)\s*(?:to|:|for|-)?\s*", "", message, flags=re.IGNORECASE).strip()
            entities["title"] = title or "New Task"
            return "TASK_CREATE", 0.92, entities

        # 5. Task Complete / Update
        if re.search(r"^(?:please\s+)?(?:mark\s+as\s+done|complete|finish|resolve|done)\b", text):
            match = re.search(r"(?:complete|finish|resolve|done|mark\s+as\s+done)\s+(?:my\s+)?([a-z0-9_\-\s]+?)(?:\s+task)?$", text)
            if match:
                keyword = match.group(1).replace("task", "").strip()
                entities["target"] = keyword or "task"
            else:
                entities["target"] = "task"
            return "TASK_UPDATE", 0.92, entities

        # 6. Task List
        if any(w in text for w in ["tasks", "list tasks", "my tasks", "pending tasks", "todos", "todo", "show tasks"]):
            return "TASK_LIST", 0.90, entities

        # 7. Plan GATE Revision
        if any(w in text for w in ["plan my gate revision", "gate revision", "plan revision", "gate study plan", "revision plan"]):
            entities["type"] = "gate_revision_plan"
            return "STUDY_PLAN", 0.92, entities

        # 8. Algorithm Explanation & Coding Help
        if any(w in text for w in ["explain binary search", "binary search", "algorithm", "debug", "python", "leetcode", "complexity"]):
            if "binary search" in text:
                entities["topic"] = "binary search"
            else:
                entities["topic"] = text
            return "CODING_HELP", 0.90, entities

        # 9. Daily Briefing
        if any(w in text for w in ["briefing", "summary of today", "daily review", "how is today going", "progress"]):
            return "DAILY_BRIEFING", 0.90, entities

        # 10. General Study Planning
        if any(w in text for w in ["study", "gate", "revise", "revision", "syllabus"]):
            for topic in ["dbms", "os", "cn", "dsa", "toc", "algorithms"]:
                if topic in text:
                    entities["topic"] = topic.upper()
            return "STUDY_PLAN", 0.88, entities

        # 11. LLM fallback classification if available
        if self.ai.name != "fallback":
            try:
                system_prompt = (
                    "You are Tamizh JARVIS Intent Router. "
                    "Classify user input into ONE intent: "
                    "[GENERAL_CHAT, NEXT_BEST_ACTION, STUDY_PLAN, TASK_CREATE, TASK_LIST, "
                    "TASK_UPDATE, WEAK_TOPICS, CAREER_GOAL, CODING_HELP, DAILY_BRIEFING]. "
                    "Respond with JSON {intent, confidence, entities}."
                )
                ai_res = await self.ai.generate(prompt=message, system_prompt=system_prompt, json_mode=True)
                import json
                parsed = json.loads(ai_res)
                return parsed.get("intent", "GENERAL_CHAT"), float(parsed.get("confidence", 0.8)), parsed.get("entities", {})
            except Exception:
                pass

        return "GENERAL_CHAT", 0.80, entities
