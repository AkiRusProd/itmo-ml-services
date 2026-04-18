from app.core.security import decode_access_token
from app.schemas.auth import LoginRequest, RegisterRequest


def test_register_user_creates_wallet_and_welcome_transaction(db_session, auth_service):
    user = auth_service.register_user(
        RegisterRequest(
            email="new@example.com",
            password="strongpass123",
            full_name="New User",
        )
    )

    assert user.id is not None
    assert user.wallet is not None
    assert user.wallet.balance == 100
    assert len(user.wallet.transactions) == 1
    assert user.wallet.transactions[0].transaction_type == "bonus"


def test_login_returns_valid_access_token(auth_service, regular_user):
    token = auth_service.authenticate_user(
        LoginRequest(email=regular_user.email, password="strongpass123")
    )

    payload = decode_access_token(token.access_token)
    assert payload["sub"] == str(regular_user.id)


def test_login_fails_with_invalid_password(auth_service, regular_user):
    try:
        auth_service.authenticate_user(
            LoginRequest(email=regular_user.email, password="wrongpass123")
        )
    except ValueError as exc:
        assert str(exc) == "Invalid email or password."
    else:
        raise AssertionError("Expected ValueError for invalid credentials")
