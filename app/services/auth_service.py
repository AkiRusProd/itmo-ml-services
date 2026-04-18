from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.transaction import Transaction
from app.models.user import User
from app.models.wallet import Wallet
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_user_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return self.db.execute(statement).scalar_one_or_none()

    def register_user(self, payload: RegisterRequest) -> User:
        existing_user = self.get_user_by_email(payload.email)
        if existing_user is not None:
            raise ValueError("User with this email already exists.")

        user = User(
            email=payload.email,
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password),
        )
        self.db.add(user)
        self.db.flush()

        wallet = Wallet(user_id=user.id, balance=100)
        self.db.add(wallet)
        self.db.flush()

        transaction = Transaction(
            wallet_id=wallet.id,
            amount=100,
            transaction_type="bonus",
            description="Welcome bonus on registration.",
        )
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate_user(self, payload: LoginRequest) -> TokenResponse:
        user = self.get_user_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise ValueError("Invalid email or password.")
        return TokenResponse(access_token=create_access_token(str(user.id)))
