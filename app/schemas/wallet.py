from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WalletResponse(BaseModel):
    id: int
    user_id: int
    balance: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransactionResponse(BaseModel):
    id: int
    amount: int
    transaction_type: str
    description: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
