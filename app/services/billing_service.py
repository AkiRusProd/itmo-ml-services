from sqlalchemy.orm import Session

from app.monitoring.metrics import track_credits_charged
from app.models.transaction import Transaction
from app.models.user import User
from app.models.wallet import Wallet


class BillingService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def ensure_sufficient_balance(self, wallet: Wallet, amount: int) -> None:
        if wallet.balance < amount:
            raise ValueError("Insufficient credits for prediction.")

    def charge_prediction(self, user: User, amount: int, prediction_request_id: int) -> Wallet:
        wallet = user.wallet
        if wallet is None:
            raise ValueError("Wallet not found for user.")

        self.ensure_sufficient_balance(wallet, amount)
        wallet.balance -= amount
        transaction = Transaction(
            wallet_id=wallet.id,
            amount=-amount,
            transaction_type="prediction_charge",
            description=f"Prediction request #{prediction_request_id}.",
        )
        self.db.add(transaction)
        track_credits_charged(amount)
        return wallet
