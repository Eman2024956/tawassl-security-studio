from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.backend.app.core.config import settings
from apps.backend.app.core.database import init_db
from apps.backend.app.core.security import SecurityMiddleware
from apps.backend.app.api.health import router as health_router
from apps.backend.app.api.projects import router as projects_router
from apps.backend.app.api.targets import router as targets_router
from apps.backend.app.api.assessments import router as assessments_router
from apps.backend.app.api.approvals import router as approvals_router
from apps.backend.app.api.catalog import router as catalog_router
from apps.backend.app.api.findings import router as findings_router
from apps.backend.app.api.reports import router as reports_router

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("tawassl.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure directories and database exist
    logger.info("Initializing Tawassl Security Studio backend...")
    await init_db()
    yield
    # Shutdown
    logger.info("Shutting down Tawassl Security Studio backend.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Local-first AI workspace for vulnerability discovery and assessment.",
    lifespan=lifespan
)

# 1. Custom Security Middleware (Host, Origin, CSRF, Secure Headers)
app.add_middleware(SecurityMiddleware)

# 2. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# 3. Include API Routers
app.include_router(health_router)
app.include_router(projects_router)
app.include_router(targets_router)
app.include_router(assessments_router)
app.include_router(approvals_router)
app.include_router(catalog_router)
app.include_router(findings_router)
app.include_router(reports_router)


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/api/health"
    }
