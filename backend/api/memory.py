from fastapi import APIRouter, Depends
from core.jarvis_core import JarvisCore
from api.chat import get_jarvis_core

router = APIRouter(prefix="/memory", tags=["Memory"])


@router.get("")
async def get_memory_summary(core: JarvisCore = Depends(get_jarvis_core)):
    await core.initialize()
    summary = await core.memory.get_active_context_summary()
    history = core.memory.get_conversation_context(count=10)
    return {
        "success": True,
        "profile": summary,
        "recent_history": history
    }
