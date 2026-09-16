from typing import Dict, Any, Optional


class TaskPlan:
    def __init__(self, tool_name: Optional[str], action: str, params: Dict[str, Any]):
        self.tool_name = tool_name
        self.action = action
        self.params = params


class Planner:
    """Decomposes intent into actionable tool execution plans."""

    @staticmethod
    def create_plan(intent: str, entities: Dict[str, Any], context: Dict[str, Any]) -> TaskPlan:
        if intent == "NEXT_BEST_ACTION":
            return TaskPlan(
                tool_name="study_tool",
                action="recommend",
                params={"type": "next_best_action"}
            )

        elif intent == "TASK_CREATE":
            return TaskPlan(
                tool_name="task_tool",
                action="create",
                params={
                    "action": "create",
                    "title": entities.get("title", "New Task"),
                    "priority": entities.get("priority", "MEDIUM")
                }
            )

        elif intent == "TASK_LIST":
            return TaskPlan(
                tool_name="task_tool",
                action="list",
                params={"action": "list"}
            )

        elif intent == "DAILY_BRIEFING":
            return TaskPlan(
                tool_name="progress_tool",
                action="daily_briefing",
                params={"action": "briefing"}
            )

        elif intent == "STUDY_PLAN":
            return TaskPlan(
                tool_name="study_tool",
                action="recommend",
                params={"action": "recommend", "topic": entities.get("topic")}
            )

        # General conversation does not require a tool invocation
        return TaskPlan(
            tool_name=None,
            action="respond",
            params={}
        )
