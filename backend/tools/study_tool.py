from typing import Dict, Any, List
from tools.base_tool import BaseTool
from memory.memory_manager import MemoryManager


class StudyTool(BaseTool):
    """Tool for GATE preparation, dynamic revision planning, and study session logging."""

    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager

    @property
    def name(self) -> str:
        return "study_tool"

    @property
    def description(self) -> str:
        return "Provides subject revision recommendations, tracks weak topics, and logs study sessions."

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        action_raw = params.get("action", "recommend")
        action = action_raw.lower().strip() if isinstance(action_raw, str) else "recommend"
        profile = self.memory.profile.get_profile()

        # 1. LOG STUDY SESSION
        if action in ["log_session", "record_session"]:
            subject = params.get("subject", "Computer Science")
            topic = params.get("topic", "General Revision")
            duration = int(params.get("duration", 45))
            notes = params.get("notes", "")
            session_id = await self.memory.long_term.log_study_session(subject, topic, duration, notes=notes)
            data = {
                "session_id": session_id,
                "subject": subject,
                "topic": topic,
                "duration": duration,
                "notes": notes
            }
            msg = f"Logged {duration} minutes for topic '{topic}' in {subject}."
            return self.format_output(
                success=True,
                action="session_logged",
                data=data,
                message=msg
            )

        # 2. STUDY HISTORY
        elif action in ["history", "study_history"]:
            limit = int(params.get("limit", 10))
            history = await self.memory.long_term.get_study_history(limit=limit)
            data = {
                "count": len(history),
                "sessions": history
            }
            msg = f"Retrieved {len(history)} recent study sessions."
            return self.format_output(
                success=True,
                action="study_history",
                data=data,
                message=msg
            )

        # 3. WEAK TOPICS & MISTAKE ANALYSIS
        elif action in ["weak_topics", "mistake_analysis"]:
            weak_records = await self.memory.long_term.list_memory_by_category("MISTAKES")
            recorded_mistakes = [r.get("value") for r in weak_records]
            data = {
                "count": len(profile.weak_topics),
                "weak_topics": profile.weak_topics,
                "recorded_mistakes": recorded_mistakes
            }
            msg = f"Identified {len(profile.weak_topics)} weak topics requiring priority reinforcement."
            return self.format_output(
                success=True,
                action="weak_topics",
                data=data,
                message=msg
            )

        # 4. PLAN REVISION
        elif action in ["plan_revision", "revision_plan"]:
            target_topic = profile.weak_topics[0] if profile.weak_topics else "DBMS Transactions"
            rec_lines = [
                "Structured GATE CS Revision Plan:",
                f"1. Slot 1 ({profile.preferred_study_slot_mins} mins): {target_topic} (Weak Topic Reinforcement)",
                "2. Slot 2 (45 mins): Dynamic Programming Problem Solving (DSA Mastery)",
                "3. Slot 3 (45 mins): TCP Congestion Control & Sliding Window (Computer Networks)",
                "4. Slot 4 (30 mins): Practice Previous Year Questions (PYQs)"
            ]
            recommendation = "\n".join(rec_lines)
            data = {
                "target_exam": "GATE Computer Science 2026",
                "subjects": profile.current_subjects,
                "priority_topics": profile.weak_topics,
                "daily_target_hours": profile.target_daily_study_hours,
                "slot_duration_minutes": profile.preferred_study_slot_mins,
                "recommendation": recommendation
            }
            return self.format_output(
                success=True,
                action="gate_revision_plan",
                data=data,
                message=recommendation
            )

        # 5. GATE PREPARATION STRATEGY
        elif action in ["gate_prep", "gate_preparation"]:
            high_weightage = [
                "Data Structures & Algorithms (15-18 marks)",
                "Operating Systems (8-10 marks)",
                "Database Management Systems (7-9 marks)",
                "Computer Networks (7-9 marks)",
                "Theory of Computation & Compiler Design (12-14 marks)"
            ]
            focus = profile.weak_topics[0] if profile.weak_topics else "Data Structures & Algorithms"
            msg = f"GATE CS Roadmap active. Prioritize high-weightage subjects and daily PYQ practice. Recommended focus: {focus}."
            data = {
                "target_exam": "GATE Computer Science 2026",
                "high_weightage_subjects": high_weightage,
                "recommended_focus": focus
            }
            return self.format_output(
                success=True,
                action="gate_preparation",
                data=data,
                message=msg
            )

        # 6. NEXT BEST ACTION / DYNAMIC RECOMMENDATION
        history = await self.memory.long_term.get_study_history(limit=5)
        recent_topics = [s.get("topic", "").lower() for s in history]

        candidate_topic = "DBMS Transactions & Concurrency Control"
        candidate_subject = "Database Management Systems"

        for wt in profile.weak_topics:
            if not any(wt.lower() in rt for rt in recent_topics):
                candidate_topic = wt
                if "dp" in wt.lower() or "dynamic programming" in wt.lower():
                    candidate_subject = "Data Structures & Algorithms"
                elif "tcp" in wt.lower() or "network" in wt.lower():
                    candidate_subject = "Computer Networks"
                elif "os" in wt.lower() or "deadlock" in wt.lower():
                    candidate_subject = "Operating Systems"
                else:
                    candidate_subject = "Database Management Systems"
                break

        msg = f"Next Best Action: Revise {candidate_topic} in {candidate_subject} for {profile.preferred_study_slot_mins} minutes."
        data = {
            "subject": candidate_subject,
            "topic": candidate_topic,
            "duration_minutes": profile.preferred_study_slot_mins,
            "priority": "HIGH",
            "reason": "Revision interval is due based on recent performance and current weak topics.",
            "recommendation": f"Revise {candidate_topic} for {profile.preferred_study_slot_mins} minutes."
        }
        return self.format_output(
            success=True,
            action="REVISION_SESSION",
            data=data,
            message=msg
        )
