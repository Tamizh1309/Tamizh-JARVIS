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

        elif action in ["update", "complete"]:
            task_id = params.get("task_id")
            keyword = params.get("keyword") or params.get("target")
            status = params.get("status", "COMPLETED")

            if not task_id and keyword:
                # Search pending tasks for matching keyword (e.g., 'dsa')
                pending = await self.memory.long_term.list_tasks(status="PENDING")
                matched = next((t for t in pending if keyword.lower() in t.get("title", "").lower()), None)
                if matched:
                    task_id = matched["id"]
                    task_title = matched["title"]
                else:
                    return {
                        "success": False,
                        "action": "task_updated",
                        "message": f"No pending task found matching keyword '{keyword}'."
                    }
            else:
                task_title = f"Task #{task_id}"

            if not task_id:
                return {"success": False, "error": "Task ID or search keyword is required."}

            updated = await self.memory.long_term.update_task_status(int(task_id), status)
            return {
                "success": updated,
                "action": "task_updated",
                "task_id": task_id,
                "title": task_title,
                "status": status,
                "message": f"Task '{task_title}' updated to {status}." if updated else "Task not found."
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
