from app.models.prediction_request import PredictionRequest
from app.schemas.prediction import PredictionPayload
from app.services.prediction_service import PredictionService
from app.services.wallet_service import WalletService


class _FakeAsyncResult:
    id = "fake-task-id"


def test_successful_prediction_charges_wallet_and_saves_result(monkeypatch, db_session, regular_user):
    from app.tasks.prediction_tasks import PredictionTaskDispatcher
    from app.services.model_registry import ModelRegistry

    def fake_enqueue(self, prediction_request_id):
        service = PredictionService(db_session)
        service.process_prediction_request(
            prediction_request_id=prediction_request_id,
            task_id="fake-task-id",
        )
        return _FakeAsyncResult()

    monkeypatch.setattr(
        PredictionTaskDispatcher,
        "enqueue",
        fake_enqueue,
    )

    monkeypatch.setattr(ModelRegistry, "predict", lambda self, payload: 123.45)
    monkeypatch.setattr(
        ModelRegistry,
        "get_metadata",
        lambda self: {
            "target_name": "MedHouseVal",
            "model_name": "apartment_price_model",
            "model_version": "v1",
        },
    )

    service = PredictionService(db_session)
    created = service.create_prediction(
        regular_user,
        PredictionPayload(
            MedInc=8.3252,
            HouseAge=41.0,
            AveRooms=6.9841,
            AveBedrms=1.0238,
            Population=322.0,
            AveOccup=2.5556,
            Latitude=37.88,
            Longitude=-122.23,
            cost_credits=10,
        ),
    )
    detail = service.get_prediction_detail(regular_user, created.id)
    wallet = WalletService(db_session).get_wallet_for_user(regular_user)

    assert detail.status == "completed"
    assert detail.prediction == 123.45
    assert wallet.balance == 90


def test_failed_prediction_does_not_charge_wallet(monkeypatch, db_session, regular_user):
    from app.services.model_registry import ModelRegistry

    prediction_request = PredictionRequest(
        user_id=regular_user.id,
        status="queued",
        input_payload={
            "MedInc": 8.3252,
            "HouseAge": 41.0,
            "AveRooms": 6.9841,
            "AveBedrms": 1.0238,
            "Population": 322.0,
            "AveOccup": 2.5556,
            "Latitude": 37.88,
            "Longitude": -122.23,
        },
        cost_credits=10,
    )
    db_session.add(prediction_request)
    db_session.commit()
    db_session.refresh(prediction_request)

    def raise_prediction_error(self, payload):
        raise RuntimeError("Model failed")

    monkeypatch.setattr(ModelRegistry, "predict", raise_prediction_error)

    service = PredictionService(db_session)
    try:
        service.process_prediction_request(prediction_request.id, task_id="failed-task-id")
    except RuntimeError as exc:
        assert str(exc) == "Model failed"
    else:
        raise AssertionError("Expected RuntimeError from model prediction")

    detail = service.get_prediction_detail(regular_user, prediction_request.id)
    wallet = WalletService(db_session).get_wallet_for_user(regular_user)
    transactions = WalletService(db_session).list_transactions_for_user(regular_user)

    assert detail.status == "failed"
    assert detail.error_message == "Model failed"
    assert wallet.balance == 100
    assert all(item.transaction_type != "prediction_charge" for item in transactions)
