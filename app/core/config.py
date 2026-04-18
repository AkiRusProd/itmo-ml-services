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
    )
