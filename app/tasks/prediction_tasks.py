from sqlalchemy.orm import Session

from app.celery import celery_app
from app.db.session import SessionLocal


class PredictionTaskDispatcher:
    def enqueue(self, prediction_request_id: int):
        return run_prediction_task.delay(prediction_request_id)


@celery_app.task(bind=True, name="app.tasks.run_prediction")
def run_prediction_task(self, prediction_request_id: int) -> dict[str, str | int]:
    from app.services.prediction_service import PredictionService

    db: Session = SessionLocal()
    try:
        service = PredictionService(db)
        detail = service.process_prediction_request(
            prediction_request_id=prediction_request_id,
            task_id=self.request.id,
        )
        return {
            "prediction_request_id": detail.id,
            "status": detail.status,
        }
    finally:
        db.close()
