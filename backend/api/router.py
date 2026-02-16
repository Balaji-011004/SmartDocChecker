"""
Master API router — aggregates all sub-routers.
"""
from fastapi import APIRouter

from api.auth import router as auth_router
from api.documents import router as documents_router
from api.results import router as results_router
from api.dashboard import router as dashboard_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(documents_router)
api_router.include_router(results_router)
api_router.include_router(dashboard_router)
