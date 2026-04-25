from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.monitoring.metrics import track_promo_code_redemption
from app.models.promo_code import PromoCode
from app.models.promo_code_activation import PromoCodeActivation
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.promo_code import PromoCodeCreateRequest
from app.services.wallet_service import WalletService

DEFAULT_PROMO_CODE_TTL_DAYS = 30


class PromoCodeService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.wallet_service = WalletService(db)

    def create_promo_code(self, payload: PromoCodeCreateRequest) -> PromoCode:
        existing = self.db.execute(
            select(PromoCode).where(func.lower(PromoCode.code) == payload.code.lower())
        ).scalar_one_or_none()
        if existing is not None:
            raise ValueError("Promo code already exists.")

        expires_at = payload.expires_at
        if expires_at is None:
            expires_at = datetime.now(timezone.utc) + timedelta(
                days=DEFAULT_PROMO_CODE_TTL_DAYS
            )

        promo_code = PromoCode(
            code=payload.code.upper(),
            credit_amount=payload.credit_amount,
            max_activations=payload.max_activations,
            expires_at=expires_at,
        )
        self.db.add(promo_code)
        self.db.commit()
        self.db.refresh(promo_code)
        return promo_code

    def redeem_promo_code(self, user: User, code: str):
        promo_code = self.db.execute(
            select(PromoCode).where(func.lower(PromoCode.code) == code.lower())
        ).scalar_one_or_none()
        if promo_code is None:
            raise ValueError("Promo code not found.")
        if not promo_code.is_active:
            raise ValueError("Promo code is inactive.")
        if promo_code.activation_count >= promo_code.max_activations:
            raise ValueError("Promo code activation limit reached.")
        if promo_code.expires_at:
            expires_at = promo_code.expires_at
            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)
            if expires_at < datetime.now(timezone.utc):
                raise ValueError("Promo code has expired.")

        existing_activation = self.db.execute(
            select(PromoCodeActivation).where(
                PromoCodeActivation.promo_code_id == promo_code.id,
                PromoCodeActivation.user_id == user.id,
            )
        ).scalar_one_or_none()
        if existing_activation is not None:
            raise ValueError("Promo code already redeemed by this user.")

        wallet = self.wallet_service.get_wallet_for_user(user)
        wallet.balance += promo_code.credit_amount
        promo_code.activation_count += 1

        activation = PromoCodeActivation(
            promo_code_id=promo_code.id,
            user_id=user.id,
        )
        transaction = Transaction(
            wallet_id=wallet.id,
            amount=promo_code.credit_amount,
            transaction_type="promo_code",
            description=f"Promo code {promo_code.code} redeemed.",
        )
        self.db.add(activation)
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(wallet)
        track_promo_code_redemption(promo_code.credit_amount)
        return promo_code, wallet
