from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from core.jarvis_core import JarvisCore

router = APIRouter(prefix="/chat", tags=["Chat"])

# Single persistent instance of JarvisCore for conversational state
_core_instance: Optional[JarvisCore] = None


def get_jarvis_core() -> JarvisCore:
    global _core_instance
    if _core_instance is None:
        _core_instance = JarvisCore()
    return _core_instance


class ChatRequest(BaseModel):
    message: str = Field(..., description="User query or command for JARVIS")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Session context or extra parameters")


class ChatResponse(BaseModel):
    success: bool
    intent: str
    action: str
    response: str
    data: Dict[str, Any] = Field(default_factory=dict)
    toolUsed: str
    memoryUpdated: bool


@router.post("", response_model=ChatResponse)
async def chat_with_jarvis(request: ChatRequest, core: JarvisCore = Depends(get_jarvis_core)):
    result = await core.handle(
        message=request.message,
        context=request.context,
    )
    return ChatResponse(**result)
