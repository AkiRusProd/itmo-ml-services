from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.wallet import TransactionResponse, WalletResponse
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
