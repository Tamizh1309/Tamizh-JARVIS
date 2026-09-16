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

            if action == "task_created":
                return f"Created task: \"{tool_result.get('title')}\" [Priority: {tool_result.get('priority')}]."

            if action == "task_list":
                tasks = tool_result.get("tasks", [])
                if not tasks:
                    return "You have no active tasks currently in your backlog."
                titles = [f"• [{t.get('priority', 'MED')}] {t.get('title')} ({t.get('status')})" for t in tasks[:5]]
                return "Active Tasks:\n" + "\n".join(titles)

            if action == "daily_briefing":
                return tool_result.get("message", "Daily briefing loaded.")

            if action == "schedule_status":
                return tool_result.get("message", "Schedule updated.")

        if raw_ai_text:
            return raw_ai_text.strip()

        return "Tamizh JARVIS processed your request. How else can I assist your study or tasks today?"
