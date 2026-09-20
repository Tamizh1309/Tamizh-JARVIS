from typing import Dict, Any


class ResponseManager:
    """Formats clear, polite, and actionable user responses with clean UTF-8 text."""

    @staticmethod
    def format_response(
        intent: str,
        tool_result: Dict[str, Any] = None,
        raw_ai_text: str = None,
        context: Dict[str, Any] = None
    ) -> str:
        if tool_result:
            action = tool_result.get("action")

            # Next Best Action & Decision Engine Actions
            if intent == "NEXT_BEST_ACTION" or action in [
                "REVISION_SESSION",
                "EXECUTE_HIGH_PRIORITY_TASK",
                "FOCUS_STUDY",
                "DAILY_REVIEW",
                "DSA_PRACTICE",
                "EXECUTE_TASK",
            ]:
                title = tool_result.get("title") or tool_result.get("topic") or "Core Study Session"
                if action == "REVISION_SESSION" and not title.lower().startswith("revise"):
                    title = f"Revise {title}"
                duration = tool_result.get("duration_minutes", 45)
                reason = tool_result.get("reason", "")
                return f"Next Best Action: {title} ({duration} mins). {reason}".strip()

            if action == "career_goal":
                return (
                    f"Your primary career goal is: {tool_result.get('primary_goal')}. "
                    f"Daily target is {tool_result.get('target_daily_study_hours')} hours."
                )

            if action == "goal_updated":
                return tool_result.get("message", "Career goal updated successfully.")

            if action in ["placement", "interview", "resume"]:
                return tool_result.get("recommendation", f"Guidance for {action} prepared.")

            if action == "weak_topics":
                topics = tool_result.get("weak_topics", [])
                if not topics:
                    return "You currently have no recorded weak topics. Excellent work!"
                return "Your current weak topics requiring priority revision are:\n" + "\n".join([f"  {t}" for t in topics])

            if action in ["gate_revision_plan", "plan_revision"]:
                return tool_result.get("message") or tool_result.get("recommendation", "GATE revision plan prepared.")

            if action in ["study_recommendation", "recommend"]:
                topic = tool_result.get("topic", "Computer Science")
                mins = tool_result.get("recommended_minutes", 45)
                reason = tool_result.get("reason", "")
                return f"Study Recommendation: Revise {topic} for {mins} minutes. {reason}".strip()

            if action == "gate_preparation":
                return tool_result.get("message", "GATE 2026 preparation roadmap ready.")

            if action == "dsa_practice":
                probs = tool_result.get("recommended_problems", [])
                lines = [f"  {p['title']} [{p['difficulty']}] - Pattern: {p['pattern']}" for p in probs]
                return "DSA Practice Plan:\n" + "\n".join(lines)

            if action == "debug_code":
                return tool_result.get("message", "Debugging guidance ready.")

            if action == "code_review":
                return tool_result.get("message", "Code review criteria applied.")

            if action == "explain_algorithm":
                algo = tool_result.get("algorithm", "Algorithm")
                tc = tool_result.get("time_complexity", "O(log N)")
                concept = tool_result.get("concept", "")
                code = tool_result.get("code_example", "")
                res = f"### {algo} Analysis\n\n**Time Complexity:** {tc}\n\n**Concept:**\n{concept}"
                if code:
                    res += f"\n\n**Implementation:**\n```python\n{code}\n```"
                return res

            if action == "session_logged":
                return f"Logged study session: {tool_result.get('duration')} minutes on '{tool_result.get('topic')}' in {tool_result.get('subject')}."

            if action == "task_created":
                return f"Created task: \"{tool_result.get('title')}\" [Priority: {tool_result.get('priority')}]."

            if action == "task_updated":
                if tool_result.get("success"):
                    return f"Successfully marked task '{tool_result.get('title')}' as COMPLETED."
                return tool_result.get("message", "Task update could not be completed.")

            if action == "task_deleted":
                return tool_result.get("message", "Task deleted successfully.")

            if action == "reminder_created":
                return tool_result.get("message", "Reminder scheduled.")

            if action == "task_list":
                tasks = tool_result.get("tasks", [])
                if not tasks:
                    return "You have no active tasks currently in your backlog."
                titles = [f"  [{t.get('priority', 'MED')}] {t.get('title')} ({t.get('status')})" for t in tasks]
                return "Your Pending Tasks:\n" + "\n".join(titles)

            if action == "daily_briefing":
                return tool_result.get("message", "Daily briefing loaded.")

            if action in ["schedule_status", "planned_schedule"]:
                return tool_result.get("message", "Schedule updated.")

            if action == "rag_query":
                return tool_result.get("message", "Document query completed.")

        if raw_ai_text:
            return raw_ai_text.strip()

        return "Tamizh JARVIS processed your request. How else can I assist your study or tasks today?"
