from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.monitoring.metrics import metrics_response, sync_business_metrics_from_db


router = APIRouter()


@router.get("/metrics", include_in_schema=False)
def get_metrics(db: Session = Depends(get_db)):
    sync_business_metrics_from_db(db)
    return metrics_response()
