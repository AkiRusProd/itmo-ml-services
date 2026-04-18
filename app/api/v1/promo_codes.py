from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_admin, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.promo_code import (
    PromoCodeCreateRequest,
    PromoCodeRedeemRequest,
    PromoCodeRedeemResponse,
    PromoCodeResponse,
)
from app.services.promo_code_service import PromoCodeService


router = APIRouter(prefix="/promo-codes")


@router.post("", response_model=PromoCodeResponse, status_code=status.HTTP_201_CREATED)
def create_promo_code(
    payload: PromoCodeCreateRequest,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> PromoCodeResponse:
    service = PromoCodeService(db)
    try:
        promo_code = service.create_promo_code(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return PromoCodeResponse.model_validate(promo_code)


@router.post("/redeem", response_model=PromoCodeRedeemResponse)
def redeem_promo_code(
    payload: PromoCodeRedeemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PromoCodeRedeemResponse:
    service = PromoCodeService(db)
    try:
        promo_code, wallet = service.redeem_promo_code(current_user, payload.code)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return PromoCodeRedeemResponse(
        message="Promo code redeemed successfully.",
        code=promo_code.code,
        credited_amount=promo_code.credit_amount,
        wallet_balance=wallet.balance,
    )
