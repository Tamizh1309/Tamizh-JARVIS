import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config.settings import get_settings
from api.health import router as health_router
from api.chat import router as chat_router, get_jarvis_core
from api.study import router as study_router
from api.tasks import router as tasks_router
from api.memory import router as memory_router

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("tamizh_jarvis")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("Initializing %s v%s in %s mode...", settings.APP_NAME, settings.APP_VERSION, settings.APP_ENV)
    core = get_jarvis_core()
    await core.initialize()
    logger.info("Tamizh JARVIS Core, Storage, and Memory subsystems fully initialized.")
    yield
    logger.info("Shutting down %s...", settings.APP_NAME)
    try:
        await core.memory.long_term.close()
    except Exception:
        pass


settings = get_settings()
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Personal agentic AI assistant for productivity, study, coding, and career growth.",
    lifespan=lifespan,
)

# Parse allowed CORS origins safely without wildcards for credentials
raw_origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
if not raw_origins:
    raw_origins = ["http://localhost:5173", "http://127.0.0.1:5173", "https://tamizh1309.github.io"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=raw_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("Unhandled error processing %s: %s", request.url.path, str(exc), exc_info=True)
    # Never expose raw stack traces in production (Section 18)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error occurred.",
            "detail": str(exc) if settings.APP_ENV == "development" else "An unexpected error occurred. Please try again.",
        },
    )


# Register API Routers
app.include_router(health_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(study_router, prefix="/api")
app.include_router(tasks_router, prefix="/api")
app.include_router(memory_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "service": settings.APP_NAME,
        "tagline": "Think. Plan. Execute. Learn.",
        "status": "online",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
