from typing import Dict, Any, List
from tools.base_tool import BaseTool
from memory.memory_manager import MemoryManager


class StudyTool(BaseTool):
    """Tool for dynamic GATE preparation, spaced repetition revision planning, and study session logging."""

    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager

    @property
    def name(self) -> str:
        return "study_tool"

    @property
    def description(self) -> str:
        return "Provides subject revision recommendations, tracks weak topics, and logs study sessions."

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        context = context or {}
        action_raw = params.get("action", "recommend")
        action = action_raw.lower().strip() if isinstance(action_raw, str) else "recommend"
        profile = self.memory.profile.get_profile()

        # 1. LOG STUDY SESSION
        if action in ["log_session", "record_session"]:
            subject = params.get("subject", "Computer Science")
            topic = params.get("topic", "General Revision")
            duration = int(params.get("duration", 45))
            notes = params.get("notes", "")
            session_type = params.get("session_type", "STUDY")
            score = float(params.get("score", 0.0))
            timestamp = params.get("timestamp")

            session_id = await self.memory.long_term.log_study_session(
                subject, topic, duration, notes=notes, session_type=session_type, score=score, timestamp=timestamp
            )
            await self.memory.create("STUDY", f"session_{session_id}", {
                "subject": subject,
                "topic": topic,
                "duration": duration,
                "notes": notes,
                "session_type": session_type,
                "score": score,
                "timestamp": timestamp,
            })
            data = {
                "session_id": session_id,
                "subject": subject,
                "topic": topic,
                "duration": duration,
                "notes": notes,
                "session_type": session_type,
                "score": score,
                "timestamp": timestamp,
            }
            msg = f"Logged {duration} minutes for topic '{topic}' in {subject}."
            return self.format_output(success=True, action="session_logged", data=data, message=msg)

        # 2. STUDY HISTORY
        elif action in ["history", "study_history"]:
            limit = int(params.get("limit", 10))
            history = await self.memory.long_term.get_study_history(limit=limit)
            data = {
                "count": len(history),
                "sessions": history
            }
            msg = f"Retrieved {len(history)} recent study sessions."
            return self.format_output(success=True, action="study_history", data=data, message=msg)

        # 3. WEAK TOPICS & MISTAKE ANALYSIS
        elif action in ["weak_topics", "mistake_analysis"]:
            data = {
                "weak_topics": profile.weak_topics,
                "count": len(profile.weak_topics),
                "high_priority": profile.weak_topics[0] if profile.weak_topics else None,
                "reinforcement_strategy": "Spaced repetition with active recall (30m problem solving + 15m formula derivation)."
            }
            msg = f"Tracked {len(profile.weak_topics)} weak topics requiring reinforcement: {', '.join(profile.weak_topics)}."
            return self.format_output(success=True, action="weak_topics", data=data, message=msg)

        # 4. GATE REVISION PLAN
        elif action in ["gate_revision_plan", "revision", "plan_revision"]:
            recent_sessions = await self.memory.long_term.get_study_history(limit=5)
            studied_topics = [s.get("topic") for s in recent_sessions]

            # Spaced repetition: select weak topic not recently studied
            selected_topic = profile.weak_topics[0] if profile.weak_topics else "Database Management Systems"
            for wt in profile.weak_topics:
                if wt not in studied_topics:
                    selected_topic = wt
                    break

            modules = [
                f"Block 1 (45m): {selected_topic} Core Principles & Formula Derivation",
                "Block 2 (30m): Solve 10 Previous Year Questions (PYQs) under timed constraints",
                "Block 3 (15m): Mistake consolidation and formula notebook update"
            ]
            plan = {
                "target_exam": "GATE CS 2026",
                "target_goal": profile.primary_goal,
                "focus_topic": selected_topic,
                "estimated_duration_minutes": 90,
                "modules": modules,
                "reason": f"Prioritized '{selected_topic}' because it is in your active weak topics list and revision is due."
            }
            msg = (
                f"Personalized GATE Revision Plan for {profile.primary_goal}:\n"
                f"Focus Topic: {selected_topic} (Spaced repetition interval due)\n"
                f"Schedule: 90 Minutes across 3 targeted blocks."
            )
            return self.format_output(success=True, action="gate_revision_plan", data=plan, message=msg)

        # 5. GATE PREPARATION ROADMAP
        elif action in ["gate_preparation", "roadmap"]:
            roadmap = {
                "exam": "GATE CS 2026",
                "user_name": profile.name,
                "primary_goal": profile.primary_goal,
                "target_daily_hours": profile.target_daily_study_hours,
                "core_subjects": profile.current_subjects,
                "phase": "Core Subject Mastery & PYQ Solving",
            }
            msg = f"GATE CS Preparation Roadmap loaded for {profile.name}. Target daily commitment: {profile.target_daily_study_hours} hours."
            return self.format_output(success=True, action="gate_preparation", data=roadmap, message=msg)

        # 6. DYNAMIC RECOMMENDATION
        else:
            recent_sessions = await self.memory.long_term.get_study_history(limit=5)
            studied_topics = [s.get("topic") for s in recent_sessions]

            # Pick from weak topics or subjects
            candidate = None
            for wt in profile.weak_topics:
                if wt not in studied_topics:
                    candidate = wt
                    break
            if not candidate:
                candidate = profile.current_subjects[0] if profile.current_subjects else "Database Management Systems"

            data = {
                "topic": candidate,
                "recommended_minutes": profile.preferred_study_slot_mins,
                "reason": f"Spaced repetition due for '{candidate}' based on recent session history."
            }
            msg = f"Recommended Study Session: Focus on '{candidate}' for {profile.preferred_study_slot_mins} minutes."
            return self.format_output(success=True, action="study_recommendation", data=data, message=msg)
