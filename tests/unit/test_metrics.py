from app.models.prediction_request import PredictionRequest
from app.monitoring.metrics import sync_business_metrics_from_db
from app.models.transaction import Transaction
from app.models.wallet import Wallet


def test_sync_business_metrics_from_db_uses_persisted_transactions(db_session, regular_user):
    wallet = db_session.query(Wallet).filter(Wallet.user_id == regular_user.id).one()
    wallet.balance = 135

    db_session.add_all(
        [
            PredictionRequest(
                user_id=regular_user.id,
                status="completed",
                input_payload={"MedInc": 1.0},
                cost_credits=10,
            ),
            PredictionRequest(
                user_id=regular_user.id,
                status="failed",
                input_payload={"MedInc": 2.0},
                cost_credits=10,
            ),
            PredictionRequest(
                user_id=regular_user.id,
                status="queued",
                input_payload={"MedInc": 3.0},
                cost_credits=10,
            ),
            Transaction(
                wallet_id=wallet.id,
                amount=50,
                transaction_type="promo_code",
                description="Promo credits.",
            ),
            Transaction(
                wallet_id=wallet.id,
                amount=25,
                transaction_type="top_up",
                description="Top-up credits.",
            ),
            Transaction(
                wallet_id=wallet.id,
                amount=-40,
                transaction_type="prediction_charge",
                description="Prediction charge.",
            ),
        ]
    )
    db_session.commit()

    sync_business_metrics_from_db(db_session)

    from app.monitoring.metrics import (
        CREDITS_CHARGED_TOTAL,
        PREDICTION_REQUESTS_TOTAL,
        PREDICTION_PROCESSING_TOTAL,
        PREDICTION_QUEUE_DEPTH,
        PROMO_CODE_CREDITS_TOTAL,
        PROMO_CODE_REDEMPTIONS_TOTAL,
        TOTAL_CREDITS_BALANCE,
        USERS_COUNT,
        WALLET_TOPUP_CREDITS_TOTAL,
        WALLET_TOPUPS_TOTAL,
    )

    assert PREDICTION_REQUESTS_TOTAL.labels(status="completed")._value.get() == 1
    assert PREDICTION_REQUESTS_TOTAL.labels(status="failed")._value.get() == 1
    assert PREDICTION_REQUESTS_TOTAL.labels(status="queued")._value.get() == 1
    assert PREDICTION_REQUESTS_TOTAL.labels(status="processing")._value.get() == 0
    assert PREDICTION_PROCESSING_TOTAL.labels(status="completed")._value.get() == 1
    assert PREDICTION_PROCESSING_TOTAL.labels(status="failed")._value.get() == 1
    assert PREDICTION_PROCESSING_TOTAL.labels(status="queued")._value.get() == 1
    assert PREDICTION_PROCESSING_TOTAL.labels(status="processing")._value.get() == 0
    assert PREDICTION_QUEUE_DEPTH._value.get() == 1
    assert CREDITS_CHARGED_TOTAL._value.get() == 40
    assert WALLET_TOPUPS_TOTAL._value.get() == 1
    assert WALLET_TOPUP_CREDITS_TOTAL._value.get() == 25
    assert PROMO_CODE_REDEMPTIONS_TOTAL._value.get() == 1
    assert PROMO_CODE_CREDITS_TOTAL._value.get() == 50
    assert TOTAL_CREDITS_BALANCE._value.get() == 135
    assert USERS_COUNT._value.get() == 1
