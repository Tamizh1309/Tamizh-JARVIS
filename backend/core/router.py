import re
from typing import Dict, Any, Tuple
from ai.provider import AIProvider


class IntentRouter:
    """
    Classifies user queries into deterministic intent categories with structured entity extraction.
    Supports all 21 core intent types required by Tamizh JARVIS with precise precedence rules.
    """

    def __init__(self, ai_provider: AIProvider):
        self.ai = ai_provider

    async def route(self, message: str, context: Dict[str, Any] = None) -> Tuple[str, float, Dict[str, Any]]:
        text = message.strip().lower()
        entities: Dict[str, Any] = {}

        # 1. REMINDER (Must be checked first)
        if re.search(r"\b(create\s+(?:a\s+)?reminder|set\s+(?:a\s+)?reminder|remind\s+me)\b", text):
            match = re.search(r"(?:create\s+(?:a\s+)?reminder|set\s+(?:a\s+)?reminder|remind\s+me\s+(?:to)?)\s*(.+)", text)
            if match:
                entities["reminder_text"] = match.group(1).strip()
            return "REMINDER", 0.95, entities

        # 2. TASK CREATE (High precedence: user is creating a task)
        if re.search(r"\b(create\s+(?:a\s+)?task|add\s+(?:a\s+)?task|new\s+task)\b", text):
            title = re.sub(r"^(?:please\s+)?(?:create\s+(?:a\s+)?task|add\s+(?:a\s+)?task|new\s+task)\s*(?:to|:|for|-)?\s*", "", message, flags=re.IGNORECASE).strip()
            entities["title"] = title or "New Task"
            return "TASK_CREATE", 0.95, entities

        # 3. TASK COMPLETE (User is finishing a task)
        if re.search(r"\b(complete|finish|mark\s+as\s+done|resolve|done)\b", text):
            match = re.search(r"(?:complete|finish|resolve|done|mark\s+as\s+done)\s+(?:my\s+)?([a-z0-9_\-\s]+?)(?:\s+task)?$", text)
            if match:
                keyword = match.group(1).replace("task", "").strip()
                entities["target"] = keyword or "task"
            else:
                entities["target"] = "task"
            return "TASK_COMPLETE", 0.95, entities

        # 4. TASK UPDATE
        if any(w in text for w in ["update task", "change task priority", "postpone task", "modify task"]):
            return "TASK_UPDATE", 0.92, entities

        # 5. TASK LIST
        if any(w in text for w in ["list tasks", "my tasks", "pending tasks", "list my pending tasks", "show tasks", "todos", "all tasks"]) or text == "tasks" or text == "todo":
            return "TASK_LIST", 0.92, entities

        # 6. NEXT BEST ACTION
        if any(w in text for w in ["next best", "what should i study now", "what should i study", "what to do now", "what should i do", "next action", "recommend next action"]):
            return "NEXT_BEST_ACTION", 0.95, entities

        # 7. GATE REVISION
        if any(w in text for w in ["plan my gate revision", "gate revision", "plan revision", "gate revision plan", "revise gate"]):
            entities["type"] = "gate_revision_plan"
            return "GATE_REVISION", 0.94, entities

        # 8. GATE PREPARATION
        if any(w in text for w in ["gate preparation", "prepare for gate", "gate exam", "gate 2026", "gate 2027", "gate syllabus"]):
            return "GATE_PREPARATION", 0.92, entities

        # 9. STUDY PLAN (Check before DSA / general schedule so 'plan my study schedule' routes here)
        if any(w in text for w in ["study plan", "plan study", "plan my study", "study schedule", "what to study", "plan my study schedule"]):
            for topic in ["dbms", "os", "cn", "dsa", "toc", "algorithms"]:
                if topic in text:
                    entities["topic"] = topic.upper()
            return "STUDY_PLAN", 0.92, entities

        # 10. DSA PRACTICE
        if any(w in text for w in ["dsa practice", "leetcode", "practice dsa", "coding problem", "leetcode problem", "practice problems"]):
            return "DSA_PRACTICE", 0.92, entities

        # 11. DEBUG CODE
        if any(w in text for w in ["debug this", "debug code", "fix this error", "fix my code", "debug python", "traceback"]):
            return "DEBUG_CODE", 0.92, entities

        # 12. CODE REVIEW
        if any(w in text for w in ["code review", "review code", "review my code", "critique my code", "refactor code"]):
            return "CODE_REVIEW", 0.92, entities

        # 13. CODING HELP & ALGORITHM EXPLANATION
        if any(w in text for w in ["explain binary search", "binary search", "how does binary search work", "explain algorithm", "coding help"]):
            if "binary search" in text:
                entities["topic"] = "binary search"
            else:
                entities["topic"] = text
            return "CODING_HELP", 0.92, entities

        # 14. MISTAKE ANALYSIS & WEAK TOPICS
        if any(w in text for w in ["mistake analysis", "my mistakes", "weak topic", "weak topics", "topics i am weak", "what are my weak"]):
            return "MISTAKE_ANALYSIS", 0.95, entities

        # 15. PROGRESS ANALYSIS & DAILY BRIEFING
        if any(w in text for w in ["progress analysis", "briefing", "daily briefing", "summary of today", "daily review", "how much did i study", "progress report"]):
            return "PROGRESS_ANALYSIS", 0.92, entities

        # 16. RESUME
        if any(w in text for w in ["resume", "cv", "ats score", "ats check", "check my resume"]):
            return "RESUME", 0.95, entities

        # 17. INTERVIEW
        if any(w in text for w in ["mock interview", "interview prep", "interview questions", "technical interview"]):
            return "INTERVIEW", 0.95, entities

        # 18. PLACEMENT
        if any(w in text for w in ["placement", "campus placement", "placement prep", "placement drive"]):
            return "PLACEMENT", 0.95, entities

        # 19. CAREER & GOAL
        if any(w in text for w in ["career goal", "my career", "what is my goal", "my goal", "primary goal", "career roadmap", "career plan"]):
            orig_match = re.search(r"(?:my\s+goal\s+is\s+to\s+(?:become\s+a\s+)?|set\s+my\s+goal\s+to\s+)(.+)", message, re.IGNORECASE)
            if orig_match:
                entities["goal"] = orig_match.group(1).strip()
                entities["action"] = "set_goal"
            return "CAREER", 0.95, entities

        # 20. SCHEDULE
        if any(w in text for w in ["schedule", "timetable", "time table", "daily routine", "check schedule", "my schedule"]):
            return "SCHEDULE", 0.90, entities

        # Fallback study keyword
        if "study" in text:
            return "STUDY_PLAN", 0.85, entities

        # 21. AI Fallback for nuanced queries
        if self.ai.name != "fallback":
            try:
                system_prompt = (
                    "You are Tamizh JARVIS Intent Router. Classify the user input into ONE intent: "
                    "[GENERAL_CHAT, TASK_CREATE, TASK_LIST, TASK_UPDATE, TASK_COMPLETE, STUDY_PLAN, "
                    "NEXT_BEST_ACTION, GATE_PREPARATION, GATE_REVISION, DSA_PRACTICE, PROGRESS_ANALYSIS, "
                    "MISTAKE_ANALYSIS, CODING_HELP, DEBUG_CODE, CODE_REVIEW, CAREER, PLACEMENT, "
                    "INTERVIEW, RESUME, SCHEDULE, REMINDER]. "
                    "Respond with JSON {intent, confidence, entities}."
                )
                ai_res = await self.ai.generate(prompt=message, system_prompt=system_prompt, json_mode=True)
                import json
                parsed = json.loads(ai_res)
                return parsed.get("intent", "GENERAL_CHAT"), float(parsed.get("confidence", 0.8)), parsed.get("entities", {})
            except Exception:
                pass

        return "GENERAL_CHAT", 0.85, entities
