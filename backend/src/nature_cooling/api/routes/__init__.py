"""Route modules, aggregated onto one router mounted at ``/api``."""

from fastapi import APIRouter

from nature_cooling.api.routes.assessments import router as assessments_router
from nature_cooling.api.routes.meta import router as meta_router
from nature_cooling.api.routes.methodology import router as methodology_router
from nature_cooling.api.routes.projects import router as projects_router

api_router = APIRouter()
api_router.include_router(assessments_router)
api_router.include_router(methodology_router)
api_router.include_router(meta_router)
api_router.include_router(projects_router)

__all__ = ["api_router"]
