"""Coding workspace API endpoints for AST analysis, debugging, and optimization."""
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from core.jarvis_core import JarvisCore
from api.chat import get_jarvis_core

router = APIRouter()


class CodingWorkspaceRequest(BaseModel):
    action: str  # explain, debug, review, optimize, dsa_practice
    code: Optional[str] = ""
    language: Optional[str] = "python"
    error: Optional[str] = ""
    topic: Optional[str] = ""


@router.post("/workspace")
async def execute_coding_workspace(
    request: CodingWorkspaceRequest,
    core: JarvisCore = Depends(get_jarvis_core)
):
    """Executes code analysis, debugging, or optimization in the coding workspace."""
    action = request.action.lower().strip()
    valid_actions = ["explain", "debug", "review", "optimize", "dsa_practice"]
    if action not in valid_actions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid coding workspace action '{action}'. Valid actions: {', '.join(valid_actions)}"
        )

    tool = core.get_tool("coding_tool")
    if not tool:
        raise HTTPException(status_code=500, detail="CodingTool is not registered in JARVIS Core.")

    params = {
        "action": action,
        "code": request.code,
        "language": request.language,
        "error": request.error,
        "topic": request.topic
    }

    result = await tool.execute(params)
    return result
