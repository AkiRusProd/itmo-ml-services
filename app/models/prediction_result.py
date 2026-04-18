from sqlalchemy import ForeignKey, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class PredictionResult(TimestampMixin, Base):
    __tablename__ = "prediction_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    prediction_request_id: Mapped[int] = mapped_column(
        ForeignKey("prediction_requests.id"),
        unique=True,
        nullable=False,
        index=True,
    )
    prediction_value: Mapped[float] = mapped_column(Float, nullable=False)
    target_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False, default="v1")

    prediction_request = relationship("PredictionRequest", back_populates="result")
