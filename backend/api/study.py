from typing import Dict, Any
from fastapi import APIRouter, Depends
from core.jarvis_core import JarvisCore
from api.chat import get_jarvis_core

router = APIRouter(prefix="/study", tags=["Study"])


@router.get("/next-action")
async def get_next_best_action(core: JarvisCore = Depends(get_jarvis_core)) -> Dict[str, Any]:
    """Returns the computed Next Best Action based on priorities and schedule."""
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
    }


@router.get("/briefing")
async def get_daily_briefing(core: JarvisCore = Depends(get_jarvis_core)) -> Dict[str, Any]:
    """Returns the structured daily briefing metrics."""
    await core.initialize()
    progress_tool = core.tools["progress_tool"]
    briefing = await progress_tool.execute({"action": "briefing"})
    return briefing
