from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.prediction import (
    PredictionCreateResponse,
    PredictionDetailResponse,
    PredictionListItem,
    PredictionPayload,
)
from app.services.prediction_service import PredictionService


router = APIRouter()


@router.post("/predictions", response_model=PredictionCreateResponse, status_code=status.HTTP_201_CREATED)
def create_prediction(
    payload: PredictionPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PredictionCreateResponse:
    service = PredictionService(db)
    try:
        return service.create_prediction(current_user, payload)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Model artifact not found. Train the model first.",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {exc}",
        ) from exc


@router.get("/predictions", response_model=list[PredictionListItem])
def list_predictions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[PredictionListItem]:
    return PredictionService(db).list_predictions(current_user)


@router.get("/predictions/{prediction_request_id}", response_model=PredictionDetailResponse)
def get_prediction(
    prediction_request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PredictionDetailResponse:
    try:
        return PredictionService(db).get_prediction_detail(current_user, prediction_request_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
