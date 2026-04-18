from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PromoCodeCreateRequest(BaseModel):
    code: str = Field(..., min_length=3, max_length=100)
    credit_amount: int = Field(..., ge=1, le=100000)
    max_activations: int = Field(default=1, ge=1, le=100000)
    expires_at: datetime | None = None


class PromoCodeRedeemRequest(BaseModel):
    code: str = Field(..., min_length=3, max_length=100)


class PromoCodeResponse(BaseModel):
    id: int
    code: str
    credit_amount: int
    is_active: bool
    max_activations: int
    activation_count: int
    expires_at: datetime | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PromoCodeRedeemResponse(BaseModel):
    message: str
    code: str
    credited_amount: int
    wallet_balance: int
