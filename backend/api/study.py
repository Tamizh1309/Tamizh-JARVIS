from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from core.jarvis_core import JarvisCore
from api.chat import get_jarvis_core

router = APIRouter(prefix="/study", tags=["Study"])


class LogStudySessionRequest(BaseModel):
    subject: str = Field(..., min_length=1, description="Subject name")
    topic: str = Field(..., min_length=1, description="Topic studied")
    duration: int = Field(..., gt=0, description="Duration in minutes (must be > 0)")
    notes: Optional[str] = ""
    session_type: Optional[str] = "STUDY"
    score: Optional[float] = Field(0.0, ge=0.0, le=100.0, description="Score 0.0 to 100.0")
    timestamp: Optional[str] = None


@router.get("/next-action")
async def get_next_best_action(core: JarvisCore = Depends(get_jarvis_core)) -> Dict[str, Any]:
    """Returns the computed Next Best Action based on real priorities, tasks, and schedule."""
    await core.initialize()
    active_context = await core.context_manager.build_context("next best action")
    nba = core.decision_engine.compute_next_best_action(active_context)
    return {
        "success": True,
        "action": nba.get("action"),
        "title": nba.get("title"),
        "duration_minutes": nba.get("duration_minutes", 45),
        "priority": nba.get("priority", "HIGH"),
        "reason": nba.get("reason"),
        "description": nba.get("description"),
        "score_breakdown": nba.get("score_breakdown", {}),
    }


@router.get("/briefing")
async def get_daily_briefing(core: JarvisCore = Depends(get_jarvis_core)) -> Dict[str, Any]:
    """Returns the structured daily briefing calculated dynamically from SQLite."""
    await core.initialize()
    progress_tool = core.tools["progress_tool"]
    briefing = await progress_tool.execute({"action": "briefing"})
    return briefing


@router.get("/history")
async def get_study_history(limit: int = Query(10, gt=0, description="Number of sessions to retrieve"), core: JarvisCore = Depends(get_jarvis_core)) -> Dict[str, Any]:
    """Returns historical study sessions."""
    if limit <= 0:
        raise HTTPException(status_code=400, detail="Limit must be a positive integer.")
    await core.initialize()
    study_tool = core.tools["study_tool"]
    return await study_tool.execute({"action": "history", "limit": limit})


@router.get("/weak-topics")
async def get_weak_topics(core: JarvisCore = Depends(get_jarvis_core)) -> Dict[str, Any]:
    """Returns tracked weak topics requiring reinforcement."""
    await core.initialize()
    study_tool = core.tools["study_tool"]
    return await study_tool.execute({"action": "weak_topics"})


@router.post("/session")
async def log_study_session(req: LogStudySessionRequest, core: JarvisCore = Depends(get_jarvis_core)) -> Dict[str, Any]:
    """Logs a completed study session directly into SQLite."""
    if not req.subject.strip():
        raise HTTPException(status_code=400, detail="Subject cannot be empty.")
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic cannot be empty.")
    if req.duration <= 0:
        raise HTTPException(status_code=400, detail="Duration must be greater than 0.")
    if req.score < 0.0 or req.score > 100.0:
        raise HTTPException(status_code=422, detail="Score must be between 0.0 and 100.0.")

    await core.initialize()
    study_tool = core.tools["study_tool"]
    return await study_tool.execute({
        "action": "log_session",
        "subject": req.subject,
        "topic": req.topic,
        "duration": req.duration,
        "notes": req.notes,
        "session_type": req.session_type,
        "score": req.score,
        "timestamp": req.timestamp
    })
