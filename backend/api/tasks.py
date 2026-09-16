from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from core.jarvis_core import JarvisCore
from api.chat import get_jarvis_core

router = APIRouter(prefix="/tasks", tags=["Tasks"])


class CreateTaskRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    priority: Optional[str] = "MEDIUM"


@router.get("")
async def list_tasks(status: Optional[str] = Query(None), core: JarvisCore = Depends(get_jarvis_core)):
    await core.initialize()
    tasks = await core.memory.long_term.list_tasks(status=status)
    return {"success": True, "count": len(tasks), "tasks": tasks}


@router.post("")
async def create_task(req: CreateTaskRequest, core: JarvisCore = Depends(get_jarvis_core)):
    await core.initialize()
    task_id = await core.memory.long_term.create_task(
        title=req.title,
        description=req.description,
        priority=req.priority
    )
    return {
        "success": True,
        "task_id": task_id,
        "title": req.title,
        "priority": req.priority,
        "status": "PENDING"
    }
