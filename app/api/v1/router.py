from fastapi import APIRouter
from app.api.v1.endpoints import health, test_ai

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(test_ai.router, prefix="/ai", tags=["AI Integration"])
