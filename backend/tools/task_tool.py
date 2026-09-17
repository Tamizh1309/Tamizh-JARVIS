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
        action_raw = params.get("action", "list")
        action = action_raw.lower().strip() if isinstance(action_raw, str) else "list"

        # 1. CREATE TASK
        if action in ["create", "task_create", "add"]:
            title = params.get("title")
            if not title:
                return self.format_output(
                    success=False,
                    action="task_created",
                    data={"error": "Task title is required."},
                    message="Task creation failed: Title is required."
                )
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
            data = {
                "task_id": task_id,
                "title": title,
                "priority": priority,
                "status": "PENDING",
                "category": category,
            }
            msg = f"Task '{title}' created successfully [Priority: {priority}]."
            return self.format_output(
                success=True,
                action="task_created",
                data=data,
                message=msg
            )

        # 2. COMPLETE / UPDATE TASK
        elif action in ["update", "complete", "task_update", "task_complete"]:
            task_id = params.get("task_id")
            keyword = params.get("keyword") or params.get("target")
            status = params.get("status", "COMPLETED")

            if not task_id and keyword:
                pending = await self.memory.long_term.list_tasks(status="PENDING")
                matched = next((t for t in pending if keyword.lower() in t.get("title", "").lower()), None)
                if matched:
                    task_id = matched["id"]
                    task_title = matched["title"]
                else:
                    return self.format_output(
                        success=False,
                        action="task_updated",
                        data={"keyword": keyword},
                        message=f"No pending task found matching keyword '{keyword}'."
                    )
            else:
                task = await self.memory.long_term.get_task(int(task_id)) if task_id else None
                task_title = task["title"] if task else f"Task #{task_id}"

            if not task_id:
                return self.format_output(
                    success=False,
                    action="task_updated",
                    data={"error": "Task ID or search keyword is required."},
                    message="Task ID or search keyword is required."
                )

            if action in ["complete", "task_complete"] or status == "COMPLETED":
                updated = await self.memory.long_term.complete_task(int(task_id))
            else:
                updates = {k: v for k, v in params.items() if k in ["title", "description", "status", "priority", "due_at", "category"]}
                updated = await self.memory.long_term.update_task(int(task_id), updates)

            data = {
                "task_id": task_id,
                "title": task_title,
                "status": status,
            }
            msg = f"Task '{task_title}' updated to {status}." if updated else "Task not found."
            return self.format_output(
                success=bool(updated),
                action="task_updated",
                data=data,
                message=msg
            )

        # 3. DELETE TASK
        elif action in ["delete", "task_delete"]:
            task_id = params.get("task_id")
            if not task_id:
                return self.format_output(
                    success=False,
                    action="task_deleted",
                    data={"error": "Task ID is required for deletion."},
                    message="Task ID is required for deletion."
                )
            deleted = await self.memory.long_term.delete_task(int(task_id))
            data = {"task_id": task_id, "deleted": deleted}
            msg = f"Task #{task_id} deleted successfully." if deleted else "Task not found."
            return self.format_output(
                success=bool(deleted),
                action="task_deleted",
                data=data,
                message=msg
            )

        # 4. REMINDER CREATION
        elif action in ["reminder", "create_reminder"]:
            reminder_text = params.get("reminder_text", "Reminder")
            task_id = await self.memory.long_term.create_task(
                title=f"Reminder: {reminder_text}",
                description="User set reminder.",
                priority="HIGH",
                category="REMINDER",
                source="USER"
            )
            data = {
                "task_id": task_id,
                "title": f"Reminder: {reminder_text}",
                "status": "PENDING"
            }
            msg = f"Reminder set: '{reminder_text}'"
            return self.format_output(
                success=True,
                action="reminder_created",
                data=data,
                message=msg
            )

        # 5. LIST TASKS (Default)
        status_filter = params.get("status")
        category_filter = params.get("category")
        tasks = await self.memory.long_term.list_tasks(status=status_filter, category=category_filter)
        data = {
            "count": len(tasks),
            "tasks": tasks
        }
        msg = f"Found {len(tasks)} tasks matching criteria."
        return self.format_output(
            success=True,
            action="task_list",
            data=data,
            message=msg
        )
