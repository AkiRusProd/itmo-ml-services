from app.services.wallet_service import WalletService


def test_top_up_wallet_increases_balance_and_creates_transaction(db_session, regular_user):
    wallet_service = WalletService(db_session)

    wallet = wallet_service.top_up_wallet(regular_user, 50)
    transactions = wallet_service.list_transactions_for_user(regular_user)

    assert wallet.balance == 150
    assert transactions[0].transaction_type == "top_up"
    assert transactions[0].amount == 50


def test_top_up_wallet_rejects_non_positive_amount(db_session, regular_user):
    wallet_service = WalletService(db_session)

    try:
        wallet_service.top_up_wallet(regular_user, 0)
    except ValueError as exc:
        assert str(exc) == "Top-up amount must be positive."
    else:
        raise AssertionError("Expected ValueError for invalid top-up amount")
