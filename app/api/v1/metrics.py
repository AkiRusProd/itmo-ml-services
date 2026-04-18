from fastapi import APIRouter

from app.monitoring.metrics import metrics_response


router = APIRouter()


@router.get("/metrics", include_in_schema=False)
def get_metrics():
    return metrics_response()
