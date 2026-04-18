from fastapi import APIRouter, HTTPException, status

from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.model_registry import ModelRegistry


router = APIRouter()


@router.post("/predictions", response_model=PredictionResponse)
def predict_apartment_price(payload: PredictionRequest) -> PredictionResponse:
    try:
        prediction = ModelRegistry().predict(payload)
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

    return PredictionResponse(
        prediction=prediction,
        target_name="MedHouseVal",
        model_name="apartment_price_model",
    )

