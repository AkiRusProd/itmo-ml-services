from app.monitoring.metrics import sync_business_metrics_from_db
from app.models.transaction import Transaction
from app.models.wallet import Wallet


def test_sync_business_metrics_from_db_uses_persisted_transactions(db_session, regular_user):
    wallet = db_session.query(Wallet).filter(Wallet.user_id == regular_user.id).one()

    db_session.add_all(
        [
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
        PROMO_CODE_CREDITS_TOTAL,
        PROMO_CODE_REDEMPTIONS_TOTAL,
        WALLET_TOPUP_CREDITS_TOTAL,
        WALLET_TOPUPS_TOTAL,
    )

    assert CREDITS_CHARGED_TOTAL._value.get() == 40
    assert WALLET_TOPUPS_TOTAL._value.get() == 1
    assert WALLET_TOPUP_CREDITS_TOTAL._value.get() == 25
    assert PROMO_CODE_REDEMPTIONS_TOTAL._value.get() == 1
    assert PROMO_CODE_CREDITS_TOTAL._value.get() == 50
