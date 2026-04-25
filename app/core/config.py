import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_version: str
    model_path: Path
    database_url: str
    redis_url: str
    cors_origins: tuple[str, ...]
    celery_task_always_eager: bool
    jwt_secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", "Apartment Price Service"),
        app_version=os.getenv("APP_VERSION", "0.1.0"),
        model_path=Path(
            os.getenv(
                "MODEL_PATH",
                str(BASE_DIR / "artifacts" / "apartment_price_model.joblib"),
            )
        ),
        database_url=os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'app.db'}"),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        cors_origins=tuple(
            origin.strip()
            for origin in os.getenv(
                "CORS_ORIGINS",
                "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3001",
            ).split(",")
            if origin.strip()
        ),
        celery_task_always_eager=os.getenv(
            "CELERY_TASK_ALWAYS_EAGER",
            "false",
        ).lower()
        in {"1", "true", "yes"},
        jwt_secret_key=os.getenv("JWT_SECRET_KEY", "change-me-for-production"),
        jwt_algorithm=os.getenv("JWT_ALGORITHM", "HS256"),
        access_token_expire_minutes=int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
        ),
    )
