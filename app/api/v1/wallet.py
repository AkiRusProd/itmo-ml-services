from fastapi import APIRouter, Depends
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.wallet import (
    TransactionResponse,
    WalletResponse,
    WalletTopUpRequest,
    WalletTopUpResponse,
)
from app.services.wallet_service import WalletService


router = APIRouter(prefix="/wallet")


@router.get("", response_model=WalletResponse)
def read_wallet(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WalletResponse:
    wallet = WalletService(db).get_wallet_for_user(current_user)
    return WalletResponse.model_validate(wallet)


@router.get("/transactions", response_model=list[TransactionResponse])
def list_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[TransactionResponse]:
    transactions = WalletService(db).list_transactions_for_user(current_user)
    return [TransactionResponse.model_validate(item) for item in transactions]


@router.post("/top-up", response_model=WalletTopUpResponse)
def top_up_wallet(
    payload: WalletTopUpRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> WalletTopUpResponse:
    service = WalletService(db)
    try:
        wallet = service.top_up_wallet(current_user, payload.amount)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return WalletTopUpResponse(
        message="Wallet topped up successfully.",
        wallet_balance=wallet.balance,
        credited_amount=payload.amount,
    )
