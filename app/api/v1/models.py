from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ml_model import MLModelResponse
from app.services.ml_model_service import MLModelService


router = APIRouter(prefix="/models")


@router.get("/current", response_model=MLModelResponse)
def get_current_model(db: Session = Depends(get_db)) -> MLModelResponse:
    return MLModelService(db).get_current_model()
