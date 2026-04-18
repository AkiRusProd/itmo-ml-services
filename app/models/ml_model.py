from sqlalchemy import Boolean, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin


class MLModel(TimestampMixin, Base):
    __tablename__ = "ml_models"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    artifact_path: Mapped[str] = mapped_column(String(255), nullable=False)
    target_name: Mapped[str] = mapped_column(String(100), nullable=False)
    features_json: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
