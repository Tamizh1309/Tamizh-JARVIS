from typing import Dict, Any


class ResponseManager:
    """Formats clear, polite, and actionable user responses."""

    @staticmethod
    def format_response(
        intent: str,
        tool_result: Dict[str, Any] = None,
        raw_ai_text: str = None,
        context: Dict[str, Any] = None
    ) -> str:
        if tool_result:
            action = tool_result.get("action")

            if action == "REVISION_SESSION":
                topic = tool_result.get("topic", "Computer Science Core")
                duration = tool_result.get("duration_minutes", 45)
                return f"Next Best Action: Revise {topic} for {duration} minutes. {tool_result.get('reason', '')}"

            if action == "career_goal":
                return (
                    f"Your primary career goal is: {tool_result.get('primary_goal')}. "
                    f"Daily target is {tool_result.get('target_daily_study_hours')} hours."
                )

            if action == "weak_topics":
                topics = tool_result.get("weak_topics", [])
                if not topics:
                    return "You currently have no recorded weak topics. Excellent work!"
                return "Your current weak topics requiring priority revision are:\n" + "\n".join([f"• {t}" for t in topics])

            if action == "gate_revision_plan":
                return tool_result.get("recommendation", "GATE revision plan prepared.")

            if action == "explain_algorithm":
                algo = tool_result.get("algorithm", "Algorithm")
                tc = tool_result.get("time_complexity", "O(log N)")
                concept = tool_result.get("concept", "")
                code = tool_result.get("code_example", "")
                res = f"### {algo} Analysis\n\n**Time Complexity:** {tc}\n\n**Concept:**\n{concept}"
                if code:
                    res += f"\n\n**Implementation:**\n```python\n{code}\n```"
                return res

            if action == "task_created":
                return f"Created task: \"{tool_result.get('title')}\" [Priority: {tool_result.get('priority')}]."

            if action == "task_updated":
                if tool_result.get("success"):
                    return f"Successfully marked task '{tool_result.get('title')}' as COMPLETED."
                return tool_result.get("message", "Task update could not be completed.")

            if action == "task_list":
                tasks = tool_result.get("tasks", [])
                if not tasks:
                    return "You have no active tasks currently in your backlog."
                titles = [f"• [{t.get('priority', 'MED')}] {t.get('title')} ({t.get('status')})" for t in tasks]
                return "Your Pending Tasks:\n" + "\n".join(titles)

            if action == "daily_briefing":
                return tool_result.get("message", "Daily briefing loaded.")

            if action == "schedule_status":
                return tool_result.get("message", "Schedule updated.")

        if raw_ai_text:
            return raw_ai_text.strip()

        return "Tamizh JARVIS processed your request. How else can I assist your study or tasks today?"
