"""Voice assistant pipeline API routes for Tamizh JARVIS."""
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from core.jarvis_core import JarvisCore
from api.chat import get_jarvis_core

router = APIRouter()


class VoiceTranscribeRequest(BaseModel):
    transcript: Optional[str] = None
    audio_data: Optional[str] = None  # Base64 audio if provided
    context: Optional[Dict[str, Any]] = None


@router.post("/transcribe")
async def process_voice_command(
    request: VoiceTranscribeRequest,
    core: JarvisCore = Depends(get_jarvis_core)
):
    """Processes speech input via JARVIS Core and returns text plus TTS configuration."""
    text = (request.transcript or "").strip()
    if not text:
        return {
            "success": False,
            "error": "No audible speech or transcript detected. Please speak into the microphone.",
            "transcript": "",
            "response": "I could not hear any speech input. Please verify your microphone and speak again.",
            "tts_config": None
        }

    # Process through JARVIS Core pipeline
    core_result = await core.handle(message=text, context=request.context)

    return {
        "success": core_result.get("success", True),
        "transcript": text,
        "response": core_result.get("response", ""),
        "intent": core_result.get("intent", "GENERAL_CHAT"),
        "toolUsed": core_result.get("toolUsed", "none"),
        "data": core_result.get("data", {}),
        "tts_config": {
            "text": core_result.get("response", ""),
            "voice": "JARVIS-Neural",
            "rate": 1.0,
            "pitch": 1.0
        }
    }
