import re
from typing import Dict, Any, Tuple
from ai.provider import AIProvider


class IntentRouter:
    """
    Classifies user queries into deterministic intent categories with structured entity extraction.
    Supports all 21 core intent types with real entity extraction for code, resumes, and tasks.
    """

    def __init__(self, ai_provider: AIProvider):
        self.ai = ai_provider

    async def route(self, message: str, context: Dict[str, Any] = None) -> Tuple[str, float, Dict[str, Any]]:
        text = message.strip().lower()
        entities: Dict[str, Any] = {}

        # 1. REMINDER
        if re.search(r"\b(create\s+(?:a\s+)?reminder|set\s+(?:a\s+)?reminder|remind\s+me)\b", text):
            match = re.search(r"(?:create\s+(?:a\s+)?reminder|set\s+(?:a\s+)?reminder|remind\s+me\s+(?:to)?)\s*(.+)", message, re.IGNORECASE)
            if match:
                entities["reminder_text"] = match.group(1).strip()
            return "REMINDER", 0.95, entities

        # 2. TASK CREATE (Extract priority, due_at, category, and clean title)
        if re.search(r"\b(create\s+(?:a\s+)?task|add\s+(?:a\s+)?task|new\s+task)\b", text):
            # Extract priority
            if "high priority" in text or "urgent" in text:
                entities["priority"] = "HIGH"
            elif "low priority" in text:
                entities["priority"] = "LOW"
            elif "medium priority" in text:
                entities["priority"] = "MEDIUM"

            # Extract due date
            if "tomorrow" in text:
                entities["due_at"] = "tomorrow"
            elif "today" in text:
                entities["due_at"] = "today"
            date_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
            if date_match:
                entities["due_at"] = date_match.group(1)

            # Extract category
            for cat in ["DBMS", "OS", "DSA", "CN", "TOC", "GATE", "CODING"]:
                if cat.lower() in text:
                    entities["category"] = cat
                    break

            # Clean Title
            raw_title = re.sub(r"^(?:please\s+)?(?:create\s+(?:a\s+)?(?:high\s+priority\s+|low\s+priority\s+|medium\s+priority\s+)?task|add\s+(?:a\s+)?task|new\s+task)\s*(?:to|:|for|-)?\s*", "", message, flags=re.IGNORECASE).strip()
            # Remove trailing time words if clean
            cleaned_title = re.sub(r"\s+(?:tomorrow|today|tonight)$", "", raw_title, flags=re.IGNORECASE).strip()
            entities["title"] = cleaned_title or raw_title or "New Task"
            return "TASK_CREATE", 0.95, entities

        # 3. TASK COMPLETE
        if re.search(r"\b(complete|finish|mark\s+as\s+done|mark.*as\s+(?:complete|done)|resolve|done)\b", text):
            m_mark = re.search(r"mark\s+(?:my\s+)?([a-z0-9_\-\s]+?)(?:\s+task)?\s+as\s+(?:complete|done)", text)
            if m_mark:
                keyword = m_mark.group(1).replace("task", "").strip()
                entities["target"] = keyword or "task"
            else:
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
        if any(w in text for w in ["list tasks", "my tasks", "pending tasks", "list my pending tasks", "show tasks", "todos", "all tasks"]) or text in ["tasks", "todo"]:
            return "TASK_LIST", 0.92, entities

        # 6. NEXT BEST ACTION (Extract available time duration if specified)
        if any(w in text for w in ["next best", "what should i study now", "what should i study", "what to do now", "what should i do", "next action", "recommend next action"]):
            dur_match = re.search(r"(?:for\s+)?(\d+)\s*(?:minutes|mins|m)\b", text)
            if dur_match:
                entities["available_time"] = int(dur_match.group(1))
            else:
                hr_match = re.search(r"(?:for\s+)?(\d+)\s*(?:hour|hours|h)\b", text)
                if hr_match:
                    entities["available_time"] = int(hr_match.group(1)) * 60
            return "NEXT_BEST_ACTION", 0.95, entities

        # 7. GATE REVISION
        if any(w in text for w in ["plan my gate revision", "gate revision", "plan revision", "gate revision plan", "revise gate"]):
            entities["type"] = "gate_revision_plan"
            return "GATE_REVISION", 0.94, entities

        # 8. GATE PREPARATION
        if any(w in text for w in ["gate preparation", "prepare for gate", "gate exam", "gate 2026", "gate 2027", "gate syllabus"]):
            return "GATE_PREPARATION", 0.92, entities

        # 9. STUDY PLAN
        if any(w in text for w in ["study plan", "plan study", "plan my study", "study schedule", "what to study", "plan my study schedule"]):
            for topic in ["dbms", "os", "cn", "dsa", "toc", "algorithms"]:
                if topic in text:
                    entities["topic"] = topic.upper()
            return "STUDY_PLAN", 0.92, entities

        # 10. DSA PRACTICE
        if any(w in text for w in ["dsa practice", "leetcode", "practice dsa", "coding problem", "leetcode problem", "practice problems", "give me dsa practice"]):
            return "DSA_PRACTICE", 0.92, entities

        # 11. DEBUG CODE (Extract language, code, and error)
        if any(w in text for w in ["debug this", "debug code", "fix this error", "fix my code", "debug python", "traceback"]) or "debug" in text:
            # Language detection
            if "javascript" in text or " js" in text:
                entities["language"] = "javascript"
            elif "cpp" in text or "c++" in text:
                entities["language"] = "cpp"
            elif "java" in text:
                entities["language"] = "java"
            else:
                entities["language"] = "python"

            code_block = re.search(r"```(?:[a-z0-9]+)?\s*([\s\S]+?)```", message)
            if code_block:
                entities["code"] = code_block.group(1).strip()
            elif ":" in message:
                parts = message.split(":", 1)
                after = parts[1].strip()
                if len(after) > 5:
                    entities["code"] = after

            # Error detection
            err_match = re.search(r"(?:error|traceback|exception)[:\s]+([a-zA-Z0-9_]+Error:?.*)", message, re.IGNORECASE)
            if err_match:
                entities["error"] = err_match.group(1).strip()

            return "DEBUG_CODE", 0.92, entities

        # 12. CODE REVIEW (Extract language, code snippet)
        if any(w in text for w in ["code review", "review code", "review my code", "critique my code", "refactor code"]) or "review this code" in text or text.startswith("review"):
            if "javascript" in text or " js" in text:
                entities["language"] = "javascript"
            elif "cpp" in text or "c++" in text:
                entities["language"] = "cpp"
            elif "java" in text:
                entities["language"] = "java"
            else:
                entities["language"] = "python"

            code_block = re.search(r"```(?:[a-z0-9]+)?\s*([\s\S]+?)```", message)
            if code_block:
                entities["code"] = code_block.group(1).strip()
            elif ":" in message:
                parts = message.split(":", 1)
                after = parts[1].strip()
                if len(after) > 5:
                    entities["code"] = after
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

        # 16. RESUME (Extract resume text if present)
        if any(w in text for w in ["resume", "cv", "ats score", "ats check", "check my resume"]):
            if ":" in message:
                parts = message.split(":", 1)
                after = parts[1].strip()
                if len(after) > 15:
                    entities["resume_text"] = after
            return "RESUME", 0.95, entities

        # 17. INTERVIEW
        if any(w in text for w in ["mock interview", "interview prep", "interview questions", "technical interview"]):
            return "INTERVIEW", 0.95, entities

        # 18. PLACEMENT
        if any(w in text for w in ["placement", "campus placement", "placement roadmap", "software engineer placement"]):
            return "PLACEMENT", 0.95, entities

        # 19. CAREER & GOALS
        if any(w in text for w in ["career goal", "my goal is", "target role", "set goal", "what is my goal", "what is my career goal"]):
            match = re.search(r"(?:my\s+(?:career\s+)?goal\s+is\s+(?:to\s+become\s+)?|set\s+(?:my\s+)?(?:career\s+)?goal\s+(?:to|as)?\s*)(.+)", message, re.IGNORECASE)
            if match:
                goal_val = match.group(1).strip().rstrip(".")
                goal_val = re.sub(r"^(?:a|an)\s+", "", goal_val, flags=re.IGNORECASE).strip()
                entities["goal"] = goal_val
                entities["action"] = "set_goal"
            return "CAREER", 0.95, entities

        # 20. SCHEDULE
        if any(w in text for w in ["schedule", "timetable", "today's timetable", "my routine", "calendar"]):
            return "SCHEDULE", 0.95, entities

                # 20. STUDY LOGGING
        if re.search(r"\b(?:log|record)\s+(\d+)\s*(?:minutes|mins|m)\b", text) or (text.startswith("log ") and any(w in text for w in ["study", "minutes", "mins", "hour"])):
            dur_match = re.search(r"(\d+)\s*(?:minutes|mins|m)\b", text)
            duration_val = int(dur_match.group(1)) if dur_match else 45
            entities["duration"] = duration_val

            topic_match = re.search(r"(?:minutes|mins|m)\s*(?:of)?\s*(.+?)(?:\s+study|\s+revision|\.|$)", text)
            if topic_match and len(topic_match.group(1).strip()) > 1:
                topic_clean = topic_match.group(1).strip().title()
                entities["topic"] = topic_clean
            else:
                entities["topic"] = "Core Study Block"

            t_low = entities["topic"].lower()
            if "dbms" in t_low or "database" in t_low:
                entities["subject"] = "Database Management Systems"
            elif "os" in t_low or "operating" in t_low:
                entities["subject"] = "Operating Systems"
            elif "network" in t_low or "cn" in t_low:
                entities["subject"] = "Computer Networks"
            elif "dsa" in t_low or "algo" in t_low:
                entities["subject"] = "Data Structures & Algorithms"
            else:
                entities["subject"] = "Computer Science"

            return "STUDY_LOG", 0.95, entities

        # 21. GENERAL CHAT (Default)
        return "GENERAL_CHAT", 0.85, entities
