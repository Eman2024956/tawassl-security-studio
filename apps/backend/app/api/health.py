import time
from fastapi import APIRouter, Depends, status
import aiosqlite
from apps.backend.app.core.config import settings
from apps.backend.app.core.database import get_db

router = APIRouter(prefix="/api", tags=["Health & Status"])

START_TIME = time.time()


@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check(db: aiosqlite.Connection = Depends(get_db)):
    """Health endpoint returning system status, DB health, and configuration."""
    db_healthy = False
    try:
        async with db.execute("SELECT 1") as cursor:
            row = await cursor.fetchone()
            if row and row[0] == 1:
                db_healthy = True
    except Exception:
        db_healthy = False

    return {
        "status": "healthy" if db_healthy else "degraded",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "uptime_seconds": round(time.time() - START_TIME, 2),
        "database": {
            "connected": db_healthy,
            "engine": "SQLite",
            "path": str(settings.DATABASE_PATH),
        },
        "ai": {
            "default_provider": settings.DEFAULT_AI_PROVIDER,
            "default_model": settings.DEFAULT_MODEL_ID,
            "gemini_configured": bool(settings.GEMINI_API_KEY),
            "openai_configured": bool(settings.OPENAI_API_KEY),
        },
        "safety_defaults": {
            "max_steps": settings.DEFAULT_MAX_STEPS,
            "max_requests": settings.DEFAULT_MAX_REQUESTS,
            "max_tool_calls": settings.DEFAULT_MAX_TOOL_CALLS,
            "timeout_seconds": settings.DEFAULT_TIMEOUT_SECONDS,
            "max_output_bytes": settings.DEFAULT_MAX_OUTPUT_BYTES,
        }
    }
