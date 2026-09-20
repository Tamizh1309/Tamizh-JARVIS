"""Study Insights and analytics engine for Tamizh JARVIS."""
import math
from typing import Dict, Any, List
from datetime import datetime, timedelta
from memory.memory_manager import MemoryManager


class StudyInsightsEngine:
    """Computes evidence-driven study streaks, retention forecast, and session analysis."""

    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager

    @staticmethod
    def _ts(session: Dict) -> str:
        """Safely extract the date string (YYYY-MM-DD) from a session dict."""
        raw = session.get("created_at") or session.get("timestamp") or ""
        return raw[:10] if raw else ""

    async def calculate_insights(self) -> Dict[str, Any]:
        await self.memory.initialize()
        sessions = await self.memory.long_term.get_study_history(limit=50)
        profile = self.memory.profile.get_profile()

        today_str = datetime.now().strftime("%Y-%m-%d")

        # 1. Streak Calculation — collect unique study dates
        dated = [s for s in sessions if self._ts(s)]
        unique_dates = sorted(
            list({self._ts(s) for s in dated}),
            reverse=True
        )

        streak = 0
        if unique_dates:
            today_date = datetime.now().date()
            first_date = datetime.strptime(unique_dates[0], "%Y-%m-%d").date()

            if (today_date - first_date).days <= 1:
                streak = 1
                for i in range(len(unique_dates) - 1):
                    d1 = datetime.strptime(unique_dates[i], "%Y-%m-%d").date()
                    d2 = datetime.strptime(unique_dates[i + 1], "%Y-%m-%d").date()
                    if (d1 - d2).days == 1:
                        streak += 1
                    else:
                        break

        # 2. Total minutes this week
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        week_minutes = sum(
            s.get("duration_minutes", 0)
            for s in sessions
            if self._ts(s) >= week_ago
        )

        # 3. Average score
        scored = [s.get("score") for s in sessions if s.get("score") and s.get("score", 0) > 0]
        avg_score = round(sum(scored) / len(scored), 1) if scored else 85.0

        # 4. Spaced Repetition Retention Forecast (R = e^(-t/S))
        topic_last_seen: Dict[str, str] = {}
        for s in sessions:
            top = s.get("topic") or s.get("subject") or "General"
            ts = self._ts(s)
            if top not in topic_last_seen and ts:
                topic_last_seen[top] = ts

        retention_list = []
        for top, last_date_str in topic_last_seen.items():
            try:
                days_elapsed = (datetime.now().date() - datetime.strptime(last_date_str, "%Y-%m-%d").date()).days
            except ValueError:
                days_elapsed = 0
            retention_pct = round(math.exp(-days_elapsed / 7.0) * 100, 1)
            retention_list.append({
                "topic": top,
                "days_since_study": days_elapsed,
                "estimated_retention_pct": max(20.0, retention_pct),
                "needs_revision": retention_pct < 70.0
            })

        retention_list.sort(key=lambda x: x["estimated_retention_pct"])

        return {
            "study_streak_days": streak,
            "total_study_minutes_week": week_minutes,
            "total_study_hours_week": round(week_minutes / 60.0, 1),
            "average_session_score": avg_score,
            "total_sessions_recorded": len(sessions),
            "retention_forecast": retention_list[:5],
            "weak_topics": profile.weak_topics,
            "target_daily_study_hours": profile.target_daily_study_hours,
            "primary_goal": profile.primary_goal
        }
