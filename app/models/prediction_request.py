from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class PredictionRequest(TimestampMixin, Base):
    __tablename__ = "prediction_requests"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="created")
    input_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    cost_credits: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    task_id: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship("User")
    result = relationship(
        "PredictionResult",
        back_populates="prediction_request",
        uselist=False,
        cascade="all, delete-orphan",
    )
