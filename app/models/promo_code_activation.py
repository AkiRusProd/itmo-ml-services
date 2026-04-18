from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class PromoCodeActivation(TimestampMixin, Base):
    __tablename__ = "promo_code_activations"
    __table_args__ = (
        UniqueConstraint("promo_code_id", "user_id", name="uq_promo_code_activations_promo_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    promo_code_id: Mapped[int] = mapped_column(ForeignKey("promo_codes.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)

    promo_code = relationship("PromoCode", back_populates="activations")
    user = relationship("User")
