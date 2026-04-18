from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.api.v1.predictions import router as predictions_router
from app.api.v1.users import router as users_router
from app.api.v1.wallet import router as wallet_router
from app.core.config import get_settings
from app.db.session import init_db


settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="ML service for apartment price prediction.",
    lifespan=lifespan,
)

app.include_router(auth_router, prefix="/api/v1", tags=["auth"])
app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(predictions_router, prefix="/api/v1", tags=["predictions"])
app.include_router(users_router, prefix="/api/v1", tags=["users"])
app.include_router(wallet_router, prefix="/api/v1", tags=["wallet"])


@app.get("/", tags=["root"])
def read_root() -> dict[str, str]:
    return {
        "message": settings.app_name,
        "docs_url": "/docs",
    }
