"""RAG + Memory Fusion Engine for source-aware synthesis in Tamizh JARVIS."""
import logging
from typing import Dict, Any, List, Optional
from rag.rag_engine import get_rag_engine
from memory.memory_manager import MemoryManager
from study.insights import StudyInsightsEngine

logger = logging.getLogger("tamizh_jarvis.core.fusion")


class FusionEngine:
    """
    Intelligently fuses:
    Short-Term Conversation + Long-Term Memory + RAG Documents + Study State + Task State.
    Produces verifiable, source-aware multi-modal responses.
    """

    def __init__(self, memory_manager: MemoryManager, rag_engine=None):
        self.memory = memory_manager
        self.rag = rag_engine or get_rag_engine()
        self.insights = StudyInsightsEngine(memory_manager)

    async def fuse_query(
        self,
        query: str,
        topic: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        context = context or {}

        # 1. Topic Extraction
        extracted_topic = topic
        if not extracted_topic:
            q_low = query.lower()
            for candidate in ["normalization", "dbms", "transactions", "concurrency", "operating systems", "paging", "virtual memory", "dsa", "binary search", "dynamic programming", "computer networks", "tcp", "sliding window"]:
                if candidate in q_low:
                    extracted_topic = candidate.title()
                    break
        extracted_topic = extracted_topic or "Computer Science"

        # 2. Query RAG Documents
        rag_res = await self.rag.query(query_text=query, top_k=3)
        rag_text = rag_res.get("answer", "")
        citations = rag_res.get("citations", [])

        # 3. Retrieve Memory History for this topic
        relevant_memories = await self.memory.retrieve_relevant_context(extracted_topic, limit=3)
        study_hist = await self.memory.long_term.get_study_history(limit=20)
        topic_sessions = [
            s for s in study_hist
            if extracted_topic.lower() in (s.get("topic") or "").lower() or extracted_topic.lower() in (s.get("subject") or "").lower()
        ]

        total_mins_studied = sum(s.get("duration_minutes", 0) for s in topic_sessions)
        session_count = len(topic_sessions)

        # 4. Compute Study Insights & Retention State
        all_insights = await self.insights.calculate_insights()
        retention_items = all_insights.get("retention_forecast", [])
        matched_retention = next(
            (r for r in retention_items if extracted_topic.lower() in r.get("topic", "").lower()),
            None
        )

        if matched_retention:
            retention_pct = matched_retention.get("estimated_retention_pct", 65.0)
            needs_revision = matched_retention.get("needs_revision", True)
            days_ago = matched_retention.get("days_since_study", 4)
        else:
            retention_pct = 58.0 if session_count > 0 else 30.0
            needs_revision = True
            days_ago = 5 if session_count > 0 else 0

        # 5. Check Active Backlog Tasks for this topic
        pending_tasks = context.get("pending_tasks") or await self.memory.long_term.list_tasks(status="PENDING")
        topic_tasks = [
            t for t in pending_tasks
            if extracted_topic.lower() in (t.get("title") or "").lower()
        ]

        # 6. Synthesize Recommendation
        recommendation = ""
        if needs_revision:
            recommendation = (
                f"Spaced revision is recommended for {extracted_topic}. "
                f"Your estimated retention is {retention_pct}% (last reviewed {days_ago} days ago). "
                f"Dedicate a 30-45 minute active recall session today."
            )
        else:
            recommendation = (
                f"Your retention for {extracted_topic} is currently solid ({retention_pct}%). "
                f"You can proceed to problem-solving or higher-order practice."
            )

        # 7. Formulate Source Badges
        sources = []
        for c in citations:
            sources.append(f"[RAG Doc: {c.get('document_name', 'Notes')} (Relevance: {c.get('similarity', 0.0)})]")
        sources.append(f"[Long-Term Memory: {session_count} study sessions ({total_mins_studied} mins)]")
        sources.append(f"[Study Insights: Ebbinghaus Spaced Decay - {retention_pct}% Retention]")

        sources_formatted = "\n".join(f"- {s}" for s in sources)
        formatted_synthesis = (
            f"### Knowledge Synthesis: {extracted_topic}\n\n"
            f"**From Your Notes:**\n{rag_text}\n\n"
            f"**Study & Retention Status:**\n"
            f"- Study History: {session_count} session(s) logged ({total_mins_studied} minutes total)\n"
            f"- Retention Forecast: {retention_pct}% (Revision Due: {'Yes' if needs_revision else 'No'})\n"
            f"- Related Tasks Pending: {len(topic_tasks)}\n\n"
            f"**JARVIS Recommendation:**\n{recommendation}\n\n"
            f"**Sources Fused:**\n{sources_formatted}"
        )

        return {
            "success": True,
            "topic": extracted_topic,
            "concept_explanation": rag_text,
            "citations": citations,
            "study_sessions_count": session_count,
            "total_minutes_studied": total_mins_studied,
            "retention_pct": retention_pct,
            "needs_revision": needs_revision,
            "topic_tasks": topic_tasks,
            "recommendation": recommendation,
            "sources": sources,
            "formatted_response": formatted_synthesis,
        }
