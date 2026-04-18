from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.prediction_request import PredictionRequest
from app.models.prediction_result import PredictionResult
from app.models.user import User
from app.schemas.prediction import (
    PredictionCreateResponse,
    PredictionDetailResponse,
    PredictionListItem,
    PredictionPayload,
)
from app.services.billing_service import BillingService
from app.services.wallet_service import WalletService
from app.tasks.prediction_tasks import PredictionTaskDispatcher


class PredictionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.billing_service = BillingService(db)
        self.wallet_service = WalletService(db)
        self.dispatcher = PredictionTaskDispatcher()

    def create_prediction(self, user: User, payload: PredictionPayload) -> PredictionCreateResponse:
        wallet = self.wallet_service.get_wallet_for_user(user)
        self.billing_service.ensure_sufficient_balance(wallet, payload.cost_credits)

        prediction_request = PredictionRequest(
            user_id=user.id,
            status="processing",
            input_payload=payload.to_model_features(),
            cost_credits=payload.cost_credits,
        )
        self.db.add(prediction_request)
        self.db.flush()

        try:
            task_result = self.dispatcher.dispatch_inline(payload)
            prediction_request.task_id = task_result.task_id

            prediction_result = PredictionResult(
                prediction_request_id=prediction_request.id,
                prediction_value=task_result.prediction_value,
                target_name=task_result.target_name,
                model_name=task_result.model_name,
                model_version=task_result.model_version,
            )
            self.db.add(prediction_result)
            self.billing_service.charge_prediction(
                user=user,
                amount=prediction_request.cost_credits,
                prediction_request_id=prediction_request.id,
            )
            prediction_request.status = "completed"
            self.db.commit()
            self.db.refresh(prediction_request)
        except Exception as exc:
            prediction_request.status = "failed"
            prediction_request.error_message = str(exc)
            self.db.commit()
            raise

        return self.get_prediction_detail(user, prediction_request.id)

    def get_prediction_detail(self, user: User, prediction_request_id: int) -> PredictionDetailResponse:
        statement = (
            select(PredictionRequest)
            .options(joinedload(PredictionRequest.result))
            .where(
                PredictionRequest.id == prediction_request_id,
                PredictionRequest.user_id == user.id,
            )
        )
        prediction_request = self.db.execute(statement).unique().scalar_one_or_none()
        if prediction_request is None:
            raise ValueError("Prediction request not found.")
        return self._to_detail_response(prediction_request)

    def list_predictions(self, user: User) -> list[PredictionListItem]:
        statement = (
            select(PredictionRequest)
            .options(joinedload(PredictionRequest.result))
            .where(PredictionRequest.user_id == user.id)
            .order_by(PredictionRequest.created_at.desc())
        )
        requests = self.db.execute(statement).unique().scalars().all()
        return [self._to_list_item(item) for item in requests]

    def _to_detail_response(self, prediction_request: PredictionRequest) -> PredictionDetailResponse:
        result = prediction_request.result
        return PredictionDetailResponse(
            id=prediction_request.id,
            status=prediction_request.status,
            task_id=prediction_request.task_id,
            cost_credits=prediction_request.cost_credits,
            input_payload=prediction_request.input_payload,
            error_message=prediction_request.error_message,
            created_at=prediction_request.created_at,
            updated_at=prediction_request.updated_at,
            prediction=result.prediction_value if result else None,
            target_name=result.target_name if result else None,
            model_name=result.model_name if result else None,
            model_version=result.model_version if result else None,
        )

    def _to_list_item(self, prediction_request: PredictionRequest) -> PredictionListItem:
        result = prediction_request.result
        return PredictionListItem(
            id=prediction_request.id,
            status=prediction_request.status,
            task_id=prediction_request.task_id,
            cost_credits=prediction_request.cost_credits,
            created_at=prediction_request.created_at,
            prediction=result.prediction_value if result else None,
            model_name=result.model_name if result else None,
        )
