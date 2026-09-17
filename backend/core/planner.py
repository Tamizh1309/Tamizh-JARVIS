from typing import Dict, Any, Optional


class TaskPlan:
    def __init__(self, tool_name: Optional[str], action: str, params: Dict[str, Any]):
        self.tool_name = tool_name
        self.action = action
        self.params = params


class Planner:
    """Decomposes intent into actionable tool execution plans for all 21 system intents."""

    @staticmethod
    def create_plan(intent: str, entities: Dict[str, Any], context: Dict[str, Any]) -> TaskPlan:
        # 1. Next Best Action
        if intent == "NEXT_BEST_ACTION":
            return TaskPlan(
                tool_name="study_tool",
                action="recommend",
                params={"action": "recommend", "type": "next_best_action"}
            )

        # 2. Career & Goals
        elif intent == "CAREER":
            if entities.get("action") == "set_goal" or entities.get("goal"):
                return TaskPlan(
                    tool_name="profile_tool",
                    action="set_goal",
                    params={"action": "set_goal", "goal": entities.get("goal")}
                )
            return TaskPlan(
                tool_name="profile_tool",
                action="get_career_goal",
                params={"action": "get_career_goal"}
            )

        # 3. Placement, Interview, Resume
        elif intent in ["PLACEMENT", "INTERVIEW", "RESUME"]:
            return TaskPlan(
                tool_name="profile_tool",
                action=intent.lower(),
                params={"action": intent.lower()}
            )

        # 4. Mistake Analysis & Weak Topics
        elif intent == "MISTAKE_ANALYSIS":
            return TaskPlan(
                tool_name="study_tool",
                action="mistake_analysis",
                params={"action": "mistake_analysis"}
            )

        # 5. Progress Analysis & Daily Briefing
        elif intent == "PROGRESS_ANALYSIS":
            return TaskPlan(
                tool_name="progress_tool",
                action="daily_briefing",
                params={"action": "briefing"}
            )

        # 6. Task Complete
        elif intent == "TASK_COMPLETE":
            return TaskPlan(
                tool_name="task_tool",
                action="complete",
                params={
                    "action": "complete",
                    "keyword": entities.get("target"),
                    "task_id": entities.get("task_id"),
                    "status": "COMPLETED"
                }
            )

        # 7. Task Create
        elif intent == "TASK_CREATE":
            return TaskPlan(
                tool_name="task_tool",
                action="create",
                params={
                    "action": "create",
                    "title": entities.get("title", "New Task"),
                    "priority": entities.get("priority", "MEDIUM"),
                    "due_at": entities.get("due_at"),
                    "category": entities.get("category", "GENERAL")
                }
            )

        # 8. Task Update
        elif intent == "TASK_UPDATE":
            return TaskPlan(
                tool_name="task_tool",
                action="update",
                params={
                    "action": "update",
                    "keyword": entities.get("target"),
                    "task_id": entities.get("task_id"),
                    "status": entities.get("status", "COMPLETED")
                }
            )

        # 9. Task List
        elif intent == "TASK_LIST":
            return TaskPlan(
                tool_name="task_tool",
                action="list",
                params={"action": "list", "status": entities.get("status")}
            )

        # 10. Reminder
        elif intent == "REMINDER":
            return TaskPlan(
                tool_name="task_tool",
                action="reminder",
                params={"action": "reminder", "reminder_text": entities.get("reminder_text", "Reminder")}
            )

        # 11. GATE Revision
        elif intent == "GATE_REVISION":
            return TaskPlan(
                tool_name="study_tool",
                action="plan_revision",
                params={"action": "plan_revision", "type": "gate_revision_plan"}
            )

        # 12. GATE Preparation
        elif intent == "GATE_PREPARATION":
            return TaskPlan(
                tool_name="study_tool",
                action="gate_prep",
                params={"action": "gate_prep"}
            )

        # 13. Study Plan
        elif intent == "STUDY_PLAN":
            if entities.get("type") == "gate_revision_plan":
                return TaskPlan(
                    tool_name="study_tool",
                    action="plan_revision",
                    params={"action": "plan_revision"}
                )
            return TaskPlan(
                tool_name="study_tool",
                action="recommend",
                params={"action": "recommend", "topic": entities.get("topic")}
            )

        # 14. DSA Practice
        elif intent == "DSA_PRACTICE":
            return TaskPlan(
                tool_name="coding_tool",
                action="dsa_practice",
                params={"action": "dsa_practice"}
            )

        # 15. Coding Help & Algorithm Explanation
        elif intent == "CODING_HELP":
            return TaskPlan(
                tool_name="coding_tool",
                action="explain",
                params={"action": "explain", "topic": entities.get("topic", "binary search")}
            )

        # 16. Debug Code
        elif intent == "DEBUG_CODE":
            return TaskPlan(
                tool_name="coding_tool",
                action="debug",
                params={"action": "debug"}
            )

        # 17. Code Review
        elif intent == "CODE_REVIEW":
            return TaskPlan(
                tool_name="coding_tool",
                action="review",
                params={"action": "review"}
            )

        # 18. Schedule
        elif intent == "SCHEDULE":
            return TaskPlan(
                tool_name="schedule_tool",
                action="check_schedule",
                params={"action": "check_schedule"}
            )

        # General Conversation / Fallback
        return TaskPlan(
            tool_name=None,
            action="respond",
            params={}
        )
