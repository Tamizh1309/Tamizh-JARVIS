from fastapi import APIRouter
from pydantic import BaseModel
from config.settings import get_settings

router = APIRouter(prefix="/health", tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str
    ai_provider: str


@router.get("", response_model=HealthResponse)
async def check_health():
    settings = get_settings()
    # Determine configured provider
    active_provider = settings.DEFAULT_AI_PROVIDER
    if active_provider == "auto":
        active_provider = "gemini" if settings.GEMINI_API_KEY else "fallback"

    return HealthResponse(
        status="ok",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        ai_provider=active_provider,
    )
