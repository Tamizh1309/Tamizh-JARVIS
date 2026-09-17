from typing import Dict, Any, List
from tools.base_tool import BaseTool
from memory.memory_manager import MemoryManager


class StudyTool(BaseTool):
    """Tool for GATE preparation, revision planning, and study session logging."""

    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager

    @property
    def name(self) -> str:
        return "study_tool"

    @property
    def description(self) -> str:
        return "Provides subject revision recommendations, tracks weak topics, and logs study sessions."

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        action = params.get("action", "recommend")
        profile = self.memory.profile.get_profile()

        # 1. Log Study Session
        if action == "log_session":
            subject = params.get("subject", "Computer Science")
            topic = params.get("topic", "General Revision")
            duration = int(params.get("duration", 45))
            notes = params.get("notes", "")
            session_id = await self.memory.long_term.log_study_session(subject, topic, duration, notes=notes)
            return {
                "success": True,
                "action": "session_logged",
                "session_id": session_id,
                "subject": subject,
                "topic": topic,
                "duration": duration,
                "message": f"Logged {duration} minutes for topic '{topic}' in {subject}."
            }

        # 2. History
        elif action == "history":
            history = await self.memory.long_term.get_study_history(limit=10)
            return {
                "success": True,
                "action": "study_history",
                "count": len(history),
                "sessions": history
            }

        # 3. Weak Topics & Mistake Analysis
        elif action in ["weak_topics", "mistake_analysis"]:
            weak_records = await self.memory.long_term.list_memory_by_category("MISTAKES")
            recorded_mistakes = [r.get("value") for r in weak_records]
            return {
                "success": True,
                "action": "weak_topics",
                "count": len(profile.weak_topics),
                "weak_topics": profile.weak_topics,
                "recorded_mistakes": recorded_mistakes,
                "message": f"Identified {len(profile.weak_topics)} weak topics requiring priority reinforcement."
            }

        # 4. Plan Revision
        elif action == "plan_revision":
            target_topic = profile.weak_topics[0] if profile.weak_topics else "DBMS Transactions"
            return {
                "success": True,
                "action": "gate_revision_plan",
                "target_exam": "GATE Computer Science 2026",
                "subjects": profile.current_subjects,
                "priority_topics": profile.weak_topics,
                "daily_target_hours": profile.target_daily_study_hours,
                "slot_duration_minutes": profile.preferred_study_slot_mins,
                "recommendation": (
                    "Structured GATE CS Revision Plan:\n"
                    f"1. Slot 1 (45 mins): {target_topic} (Weak Topic Priority)\n"
                    "2. Slot 2 (45 mins): Dynamic Programming Problem Solving (DSA Mastery)\n"
                    "3. Slot 3 (45 mins): TCP Congestion Control & Sliding Window (Computer Networks)\n"
                    "4. Slot 4 (30 mins): Practice Previous Year Questions (PYQs)"
                )
            }

        # 5. GATE Prep Strategy
        elif action == "gate_prep":
            return {
                "success": True,
                "action": "gate_preparation",
                "target_exam": "GATE Computer Science 2026",
                "high_weightage_subjects": [
                    "Data Structures & Algorithms (15-18 marks)",
                    "Operating Systems (8-10 marks)",
                    "Database Management Systems (7-9 marks)",
                    "Computer Networks (7-9 marks)",
                    "Theory of Computation & Compiler Design (12-14 marks)"
                ],
                "recommended_focus": profile.weak_topics[0] if profile.weak_topics else "DSA",
                "message": "GATE CS Roadmap active. Prioritize high-weightage subjects and daily PYQ practice."
            }

        # Default: recommend next study action
        target_topic = profile.weak_topics[0] if profile.weak_topics else "DBMS Transactions"
        return {
            "success": True,
            "action": "REVISION_SESSION",
            "subject": "Database Management Systems",
            "topic": target_topic,
            "duration_minutes": profile.preferred_study_slot_mins,
            "priority": "HIGH",
            "reason": "Revision interval is due and recent performance indicates this weak topic needs reinforcement.",
            "recommendation": f"Revise {target_topic} for {profile.preferred_study_slot_mins} minutes."
        }
