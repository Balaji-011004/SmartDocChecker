"""
SmartDocChecker API — Application entrypoint.

This file creates the FastAPI app, attaches middleware, and includes
all sub-routers.  Run with:
    uvicorn main:app --reload
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import settings
from api.router import api_router
from db.session import engine, SessionLocal
from db.base import Base

# ── Import models so Base.metadata knows about them ──
from models.user import User
from models.document import Document
from models.contradiction import Contradiction
from models.clause import Clause
from models.comparison import ComparisonSession
from models.cross_contradiction import CrossContradiction

# ── Logging ──
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Rate Limiter ──
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT_DEFAULT])


# ── Lifespan: startup & shutdown logic ──
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create tables, warm models, seed admin."""
    logger.info("Creating database tables (if they don't exist)…")
    Base.metadata.create_all(bind=engine)

    from core.hashing import hash_password

    db = SessionLocal()
    try:
        # ── Model Warming ──
        logger.info("Warming AI models…")
        from services.embedding_service import _load_sbert_model
        from services.nli_service import _load_nli_model
        _load_sbert_model()
        _load_nli_model()
        logger.info("AI models warmed and ready.")

        admin = db.query(User).filter(User.email == "admin@smartdoc.com").first()
        if not admin:
            import os
            admin_password = os.environ.get("ADMIN_PASSWORD", "Admin123!")
            admin = User(
                name="Admin",
                email="admin@smartdoc.com",
                hashed_password=hash_password(admin_password),
            )
            db.add(admin)
            db.commit()
            logger.info("Seeded default admin user: admin@smartdoc.com")
            if admin_password == "Admin123!":
                logger.warning(
                    "⚠  Admin seeded with DEFAULT password. "
                    "Set ADMIN_PASSWORD env var for production!"
                )
        else:
            logger.info("Admin user already exists, skipping seed.")
    finally:
        db.close()

    logger.info(f"✓ {settings.APP_NAME} v{settings.APP_VERSION} ready")
    yield
    logger.info("Shutting down SmartDocChecker API…")


# ── FastAPI app ──
app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise-grade contradiction detection API",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    # Disable interactive API docs in production
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# ── Rate Limiting Middleware ──
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


# ── Security Headers Middleware ──
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    # Prevent caching of authenticated responses
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


# ── Include all API routes ──
app.include_router(api_router)

