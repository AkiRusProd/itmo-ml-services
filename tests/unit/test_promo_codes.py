from datetime import datetime, timedelta, timezone

from app.schemas.promo_code import PromoCodeCreateRequest
from app.services.promo_code_service import PromoCodeService


def test_redeem_promo_code_credits_wallet(db_session, admin_user, regular_user):
    promo_service = PromoCodeService(db_session)
    promo_code = promo_service.create_promo_code(
        PromoCodeCreateRequest(code="WELCOME50", credit_amount=50, max_activations=2)
    )

    _, wallet = promo_service.redeem_promo_code(regular_user, "WELCOME50")

    assert promo_code.activation_count == 1
    assert wallet.balance == 150
    assert promo_code.expires_at is not None
    delta = promo_code.expires_at - datetime.now(timezone.utc).replace(tzinfo=None)
    assert 29 <= delta.days <= 30


def test_redeem_promo_code_cannot_be_used_twice_by_same_user(db_session, admin_user, regular_user):
    promo_service = PromoCodeService(db_session)
    promo_service.create_promo_code(
        PromoCodeCreateRequest(code="WELCOME50", credit_amount=50, max_activations=2)
    )
    promo_service.redeem_promo_code(regular_user, "WELCOME50")

    try:
        promo_service.redeem_promo_code(regular_user, "WELCOME50")
    except ValueError as exc:
        assert str(exc) == "Promo code already redeemed by this user."
    else:
        raise AssertionError("Expected ValueError for duplicate redemption")


def test_redeem_expired_promo_code_fails(db_session, admin_user, regular_user):
    promo_service = PromoCodeService(db_session)
    promo_service.create_promo_code(
        PromoCodeCreateRequest(
            code="OLD50",
            credit_amount=50,
            max_activations=1,
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
        )
    )

    try:
        promo_service.redeem_promo_code(regular_user, "OLD50")
    except ValueError as exc:
        assert str(exc) == "Promo code has expired."
    else:
        raise AssertionError("Expected ValueError for expired promo code")


def test_create_promo_code_respects_explicit_expiration(db_session):
    promo_service = PromoCodeService(db_session)
    expires_at = datetime.now(timezone.utc) + timedelta(days=5)

    promo_code = promo_service.create_promo_code(
        PromoCodeCreateRequest(
            code="FLASH25",
            credit_amount=25,
            max_activations=1,
            expires_at=expires_at,
        )
    )

    assert promo_code.expires_at is not None
    actual_expiration = promo_code.expires_at
    if actual_expiration.tzinfo is None:
        actual_expiration = actual_expiration.replace(tzinfo=timezone.utc)
    assert abs((actual_expiration - expires_at).total_seconds()) < 2
