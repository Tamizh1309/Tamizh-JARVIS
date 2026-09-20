"""Personalized Study Decision Agent for Tamizh JARVIS."""
import logging
from typing import Dict, Any, List, Optional
from memory.memory_manager import MemoryManager
from study.insights import StudyInsightsEngine
from rag.rag_engine import get_rag_engine

logger = logging.getLogger("tamizh_jarvis.study.personalized_agent")


class PersonalizedStudyAgent:
    """
    Synthesizes multi-source evidence:
    study history + weak topics + retention curves + target exam +
    available time + pending tasks + recent mistakes + RAG notes.
    Produces the structured Next Best Study Action.
    """

    def __init__(self, memory_manager: MemoryManager, rag_engine=None):
        self.memory = memory_manager
        self.insights = StudyInsightsEngine(memory_manager)
        self.rag = rag_engine or get_rag_engine()

    async def decide_next_study_action(
        self,
        available_time: int = 45,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        context = context or {}
        await self.memory.initialize()

        profile = self.memory.profile.get_profile()
        target_exam = profile.primary_goal or "GATE 2026"
        target_hours = profile.target_daily_study_hours or 3.5
        target_mins = int(target_hours * 60)

        # 1. Gather Multi-Source Evidence
        study_hist = await self.memory.long_term.get_study_history(limit=25)
        today_mins = await self.memory.long_term.get_today_study_minutes()
        pending_tasks = await self.memory.long_term.list_tasks(status="PENDING")
        mistakes = await self.memory.long_term.list_memory_by_category("MISTAKE")
        insights_data = await self.insights.calculate_insights()
        retention_forecast = insights_data.get("retention_forecast", [])
        weak_topics = profile.weak_topics or ["DBMS Normalization", "Dynamic Programming", "TCP Congestion Control"]

        # 2. Get Available RAG Documents
        indexed_docs = self.rag.vector_store.list_documents() if hasattr(self.rag, "vector_store") else []
        doc_names = [d.get("filename", "") for d in indexed_docs]

        # 3. Candidate Generation
        candidates: List[Dict[str, Any]] = []

        # Candidate A: Retention Overdue Topics (< 70% retention)
        overdue_retention = [r for r in retention_forecast if r.get("needs_revision")]
        if overdue_retention:
            top_overdue = overdue_retention[0]
            top_name = top_overdue.get("topic", "DBMS")
            matched_doc = next((d for d in doc_names if top_name.lower() in d.lower()), doc_names[0] if doc_names else "Syllabus Notes")
            candidates.append({
                "score": 96.0,
                "topic": top_name,
                "reason": f"Spaced retention has decayed to {top_overdue.get('estimated_retention_pct')}%. Immediate revision prevents forgetting curve cliff.",
                "duration": min(available_time, 45),
                "difficulty": "MEDIUM",
                "priority": "HIGH",
                "source_document": matched_doc,
                "revision_status": "OVERDUE",
                "action": "SPACED_REVISION",
                "action_plan": [
                    f"Review notes for {top_name} ({matched_doc})",
                    "Do 10 minutes of active recall on key definitions and anomalies",
                    "Solve 2 previous year GATE questions"
                ]
            })

        # Candidate B: Critical Weak Topic Recovery
        if weak_topics:
            top_weak = weak_topics[0]
            matched_doc = next((d for d in doc_names if top_weak.lower() in d.lower()), "GATE_Core_Curriculum.pdf")
            candidates.append({
                "score": 91.0,
                "topic": top_weak,
                "reason": f"Topic '{top_weak}' is flagged as a high-friction area in your student profile.",
                "duration": min(available_time, 60),
                "difficulty": "HARD",
                "priority": "HIGH",
                "source_document": matched_doc,
                "revision_status": "DUE_SOON",
                "action": "WEAK_TOPIC_MASTERY",
                "action_plan": [
                    f"Inspect foundational theory for {top_weak}",
                    "Identify error patterns from previous test attempts",
                    "Complete 3 guided practice problems"
                ]
            })

        # Candidate C: High-Priority Study Task in Backlog
        study_tasks = [t for t in pending_tasks if t.get("category") == "STUDY" or "study" in t.get("title", "").lower()]
        if study_tasks:
            top_task = study_tasks[0]
            candidates.append({
                "score": 88.0,
                "topic": top_task.get("title"),
                "reason": f"Directly addresses pending milestone in your study backlog: '{top_task.get('title')}'.",
                "duration": min(available_time, 45),
                "difficulty": "MEDIUM",
                "priority": top_task.get("priority", "HIGH"),
                "source_document": "Task Backlog",
                "revision_status": "IN_PROGRESS",
                "action": "EXECUTE_STUDY_TASK",
                "action_plan": [
                    f"Begin task #{top_task.get('id')}: {top_task.get('title')}",
                    "Set 30 minute uninterrupted focus timer",
                    "Mark task complete upon milestone verification"
                ]
            })

        # Candidate D: Target Completion Consolidation
        if today_mins >= target_mins:
            candidates.append({
                "score": 85.0,
                "topic": f"{target_exam} Consolidation & Flashcard Review",
                "reason": f"Daily target of {target_hours}h reached ({today_mins}m logged today). Light consolidation recommended.",
                "duration": min(available_time, 20),
                "difficulty": "EASY",
                "priority": "LOW",
                "source_document": "Self-Reflection Journal",
                "revision_status": "ON_TRACK",
                "action": "LIGHT_REVIEW",
                "action_plan": [
                    "Quick 15-minute formula sheet review",
                    "Verify today's completed milestones",
                    "Prepare tomorrow's morning topic schedule"
                ]
            })

        # Fallback Candidate: Core Syllabus Deep Work
        default_topic = "Algorithms & Data Structures"
        candidates.append({
            "score": 75.0,
            "topic": default_topic,
            "reason": f"Steady progress toward your {target_exam} target ({today_mins}m completed of {target_mins}m target).",
            "duration": min(available_time, 45),
            "difficulty": "MEDIUM",
            "priority": "MEDIUM",
            "source_document": "GATE_Core_Curriculum.pdf",
            "revision_status": "ON_TRACK",
            "action": "CORE_SYLLABUS_STUDY",
            "action_plan": [
                f"Study 1 key concept in {default_topic}",
                "Work through standard proof and complexity bounds",
                "Log session to update daily study streak"
            ]
        })

        candidates.sort(key=lambda x: x["score"], reverse=True)
        top = candidates[0]

        return {
            "success": True,
            "topic": top["topic"],
            "reason": top["reason"],
            "duration": top["duration"],
            "duration_minutes": top["duration"],
            "difficulty": top["difficulty"],
            "priority": top["priority"],
            "source_document": top["source_document"],
            "revision_status": top["revision_status"],
            "action": top["action"],
            "action_plan": top["action_plan"],
            "composite_score": top["score"],
            "target_exam": target_exam,
            "today_study_minutes": today_mins,
            "target_daily_minutes": target_mins,
        }
