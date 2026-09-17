from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from core.jarvis_core import JarvisCore
from api.chat import get_jarvis_core

router = APIRouter(prefix="/tasks", tags=["Tasks"])


class CreateTaskRequest(BaseModel):
    title: str = Field(..., description="Title of the task")
    description: Optional[str] = ""
    priority: Optional[str] = "MEDIUM"
    due_at: Optional[str] = None
    category: Optional[str] = "GENERAL"
    source: Optional[str] = "USER"


class UpdateTaskRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_at: Optional[str] = None
    category: Optional[str] = None


@router.get("")
async def list_tasks(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    limit: Optional[int] = Query(None),
    core: JarvisCore = Depends(get_jarvis_core)
):
    await core.initialize()
    tasks = await core.memory.long_term.list_tasks(status=status, category=category, limit=limit)
    return {"success": True, "count": len(tasks), "tasks": tasks}


@router.post("")
async def create_task(req: CreateTaskRequest, core: JarvisCore = Depends(get_jarvis_core)):
    await core.initialize()
    task_id = await core.memory.long_term.create_task(
        title=req.title,
        description=req.description,
        priority=req.priority,
        due_at=req.due_at,
        category=req.category,
        source=req.source,
    )
    return {
        "success": True,
        "task_id": task_id,
        "title": req.title,
        "priority": req.priority,
        "status": "PENDING",
        "category": req.category,
    }


@router.patch("/{task_id}")
@router.put("/{task_id}")
async def update_task(task_id: int, req: UpdateTaskRequest, core: JarvisCore = Depends(get_jarvis_core)):
    await core.initialize()
    updates = {k: v for k, v in req.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="No fields provided to update.")
    success = await core.memory.long_term.update_task(task_id, updates)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found or not modified.")
    task = await core.memory.long_term.get_task(task_id)
    return {"success": True, "task": task}


@router.post("/{task_id}/complete")
async def complete_task(task_id: int, core: JarvisCore = Depends(get_jarvis_core)):
    await core.initialize()
    success = await core.memory.long_term.complete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found.")
    task = await core.memory.long_term.get_task(task_id)
    return {"success": True, "message": "Task marked as COMPLETED.", "task": task}


@router.delete("/{task_id}")
async def delete_task(task_id: int, core: JarvisCore = Depends(get_jarvis_core)):
    await core.initialize()
    success = await core.memory.long_term.delete_task(task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found.")
    return {"success": True, "message": f"Task #{task_id} deleted successfully."}
