from typing import Dict, Any
from tools.base_tool import BaseTool
from memory.memory_manager import MemoryManager


class TaskTool(BaseTool):
    """Tool for managing user tasks, deadlines, and daily task summaries."""

    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager

    @property
    def name(self) -> str:
        return "task_tool"

    @property
    def description(self) -> str:
        return "Creates, lists, updates, and reviews pending and completed tasks."

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        action = params.get("action", "list")

        if action == "create":
            title = params.get("title")
            if not title:
                return {"success": False, "error": "Task title is required."}
            desc = params.get("description", "")
            priority = params.get("priority", "MEDIUM")
            task_id = await self.memory.long_term.create_task(title=title, description=desc, priority=priority)
            return {
                "success": True,
                "action": "task_created",
                "task_id": task_id,
                "title": title,
                "priority": priority,
                "message": f"Task '{title}' created successfully."
            }

        elif action == "update":
            task_id = params.get("task_id")
            status = params.get("status", "COMPLETED")
            if not task_id:
                return {"success": False, "error": "Task ID is required."}
            updated = await self.memory.long_term.update_task_status(int(task_id), status)
            return {
                "success": updated,
                "action": "task_updated",
                "task_id": task_id,
                "status": status,
                "message": f"Task {task_id} updated to {status}." if updated else "Task not found."
            }

        # Default: list tasks
        status_filter = params.get("status")
        tasks = await self.memory.long_term.list_tasks(status=status_filter)
        return {
            "success": True,
            "action": "task_list",
            "count": len(tasks),
            "tasks": tasks
        }
