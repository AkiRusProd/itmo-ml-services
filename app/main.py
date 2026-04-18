from fastapi import FastAPI

from app.api.v1.health import router as health_router
from app.api.v1.predictions import router as predictions_router
from app.core.config import get_settings


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="ML service for apartment price prediction.",
)

app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(predictions_router, prefix="/api/v1", tags=["predictions"])


@app.get("/", tags=["root"])
def read_root() -> dict[str, str]:
    return {
        "message": settings.app_name,
        "docs_url": "/docs",
    }

