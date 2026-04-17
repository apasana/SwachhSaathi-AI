from fastapi import APIRouter

from database.mongo import ping_database
from models.schemas import HealthResponse
from utils.config import settings


router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="ok" if ping_database() else "degraded", service=settings.APP_NAME)
