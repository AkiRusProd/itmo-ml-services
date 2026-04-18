from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.user import User
from app.models.wallet import Wallet


class WalletService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_wallet_for_user(self, user: User) -> Wallet:
        statement = select(Wallet).where(Wallet.user_id == user.id)
        wallet = self.db.execute(statement).scalar_one_or_none()
        if wallet is None:
            wallet = Wallet(user_id=user.id, balance=0)
            self.db.add(wallet)
            self.db.commit()
            self.db.refresh(wallet)
        return wallet

    def list_transactions_for_user(self, user: User) -> list[Transaction]:
        wallet = self.get_wallet_for_user(user)
        statement = (
            select(Transaction)
            .where(Transaction.wallet_id == wallet.id)
            .order_by(Transaction.created_at.desc())
        )
        return list(self.db.execute(statement).scalars().all())
