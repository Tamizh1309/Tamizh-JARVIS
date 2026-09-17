from typing import Dict, Any, Optional
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
        return "Creates, lists, updates, completes, and deletes tasks."

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        action = params.get("action", "list")

        # 1. CREATE TASK
        if action == "create":
            title = params.get("title")
            if not title:
                return {"success": False, "error": "Task title is required."}
            desc = params.get("description", "")
            priority = params.get("priority", "MEDIUM")
            due_at = params.get("due_at")
            category = params.get("category", "GENERAL")
            source = params.get("source", "USER")

            task_id = await self.memory.long_term.create_task(
                title=title,
                description=desc,
                priority=priority,
                due_at=due_at,
                category=category,
                source=source,
            )
            return {
                "success": True,
                "action": "task_created",
                "task_id": task_id,
                "title": title,
                "priority": priority,
                "category": category,
                "message": f"Task '{title}' created successfully [Priority: {priority}]."
            }

        # 2. COMPLETE / UPDATE TASK
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
                task = await self.memory.long_term.get_task(int(task_id)) if task_id else None
                task_title = task["title"] if task else f"Task #{task_id}"

            if not task_id:
                return {"success": False, "error": "Task ID or search keyword is required."}

            if action == "complete" or status == "COMPLETED":
                updated = await self.memory.long_term.complete_task(int(task_id))
            else:
                updates = {k: v for k, v in params.items() if k in ["title", "description", "status", "priority", "due_at", "category"]}
                updated = await self.memory.long_term.update_task(int(task_id), updates)

            return {
                "success": updated,
                "action": "task_updated",
                "task_id": task_id,
                "title": task_title,
                "status": status,
                "message": f"Task '{task_title}' updated to {status}." if updated else "Task not found."
            }

        # 3. DELETE TASK
        elif action == "delete":
            task_id = params.get("task_id")
            if not task_id:
                return {"success": False, "error": "Task ID is required for deletion."}
            deleted = await self.memory.long_term.delete_task(int(task_id))
            return {
                "success": deleted,
                "action": "task_deleted",
                "task_id": task_id,
                "message": f"Task #{task_id} deleted successfully." if deleted else "Task not found."
            }

        # 4. REMINDER CREATION
        elif action == "reminder":
            reminder_text = params.get("reminder_text", "Reminder")
            task_id = await self.memory.long_term.create_task(
                title=f"Reminder: {reminder_text}",
                description="User set reminder.",
                priority="HIGH",
                category="REMINDER",
                source="USER"
            )
            return {
                "success": True,
                "action": "reminder_created",
                "task_id": task_id,
                "title": f"Reminder: {reminder_text}",
                "message": f"Reminder set: \"{reminder_text}\""
            }

        # 5. Default: LIST TASKS
        status_filter = params.get("status")
        category_filter = params.get("category")
        tasks = await self.memory.long_term.list_tasks(status=status_filter, category=category_filter)
        return {
            "success": True,
            "action": "task_list",
            "count": len(tasks),
            "tasks": tasks
        }
