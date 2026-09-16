from typing import Dict, Any


class DecisionEngine:
    """Computes the Next Best Action using deterministic rules and context."""

    @staticmethod
    def compute_next_best_action(context: Dict[str, Any]) -> Dict[str, Any]:
        pending_tasks = context.get("pending_tasks", [])
        weak_topics = context.get("weak_topics", [])
        today_mins = context.get("today_study_minutes", 0)

        # 1. If high priority pending task exists, prioritize it
        high_priority_tasks = [t for t in pending_tasks if t.get("priority") == "HIGH"]
        if high_priority_tasks:
            top_task = high_priority_tasks[0]
            return {
                "action": "EXECUTE_HIGH_PRIORITY_TASK",
                "title": top_task.get("title"),
                "duration_minutes": 45,
                "priority": "HIGH",
                "reason": f"High priority task pending in your backlog: '{top_task.get('title')}'.",
                "description": top_task.get("description", "Execute pending high priority milestone.")
            }

        # 2. If weak topics need reinforcement
        if weak_topics:
            topic = weak_topics[0]
            return {
                "action": "REVISION_SESSION",
                "title": f"Revise {topic}",
                "duration_minutes": 45,
                "priority": "HIGH",
                "reason": f"Revision interval is due based on recent performance in '{topic}' and your GATE roadmap.",
                "description": f"Dedicated 45-minute focus session on {topic}."
            }

        # 3. Standard daily progress milestone
        return {
            "action": "FOCUS_STUDY",
            "title": "GATE Computer Science Core Revision",
            "duration_minutes": 30,
            "priority": "MEDIUM",
            "reason": f"You have completed {today_mins} minutes today. Keep the momentum going.",
            "description": "Standard review session for Computer Science core concepts."
        }
