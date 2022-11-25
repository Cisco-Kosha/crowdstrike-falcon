from fastapi import APIRouter

from app.api.api_v1.endpoints import detections

api_router = APIRouter()

api_router.include_router(detections.router, prefix="/detections", tags=["detections"])
