from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import CurrentUserResponse
from app.services.wallet_service import WalletService
from app.db.session import get_db
from sqlalchemy.orm import Session


router = APIRouter(prefix="/users")


@router.get("/me", response_model=CurrentUserResponse)
def read_current_user(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CurrentUserResponse:
    wallet = WalletService(db).get_wallet_for_user(current_user)
    return CurrentUserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        wallet_balance=wallet.balance,
    )
