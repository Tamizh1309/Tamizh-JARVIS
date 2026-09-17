from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel, Field
from core.jarvis_core import JarvisCore
from api.chat import get_jarvis_core

router = APIRouter(prefix="/memory", tags=["Memory"])


class MemoryRecordRequest(BaseModel):
    category: str = Field(..., description="Category like USER_PROFILE, GOALS, PREFERENCES, etc.")
    key: str = Field(..., description="Unique key identifier")
    value: Any = Field(..., description="Value to store")
    metadata: Optional[Dict[str, Any]] = None


@router.get("")
async def get_memory_summary(core: JarvisCore = Depends(get_jarvis_core)):
    """Returns aggregated profile, goals, active tasks summary, and conversational context."""
    await core.initialize()
    summary = await core.memory.get_active_context_summary()
    history = core.memory.get_conversation_context(count=10)
    return {
        "success": True,
        "profile": summary,
        "recent_history": history
    }


@router.get("/search")
async def search_memory(
    q: str = Query(..., description="Search query"),
    category: Optional[str] = Query(None),
    core: JarvisCore = Depends(get_jarvis_core)
):
    """Searches memory records by key or value."""
    await core.initialize()
    records = await core.memory.search(q, category=category)
    return {"success": True, "count": len(records), "records": records}


@router.post("")
async def set_memory_record(req: MemoryRecordRequest, core: JarvisCore = Depends(get_jarvis_core)):
    """Creates or updates a memory record in SQLite."""
    await core.initialize()
    success = await core.memory.create(req.category, req.key, req.value, req.metadata)
    return {"success": success, "category": req.category, "key": req.key}


@router.delete("/{category}/{key}")
async def delete_memory_record(category: str, key: str, core: JarvisCore = Depends(get_jarvis_core)):
    """Deletes a memory record."""
    await core.initialize()
    deleted = await core.memory.delete(category, key)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory record not found.")
    return {"success": True, "message": f"Memory record '{category}:{key}' deleted."}
