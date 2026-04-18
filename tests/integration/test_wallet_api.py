def test_wallet_top_up_and_transactions_flow(client, auth_headers):
    top_up_response = client.post(
        "/api/v1/wallet/top-up",
        json={"amount": 50},
        headers=auth_headers,
    )
    assert top_up_response.status_code == 200
    assert top_up_response.json()["wallet_balance"] == 150

    wallet_response = client.get("/api/v1/wallet", headers=auth_headers)
    assert wallet_response.status_code == 200
    assert wallet_response.json()["balance"] == 150

    transactions_response = client.get(
        "/api/v1/wallet/transactions",
        headers=auth_headers,
    )
    assert transactions_response.status_code == 200
    transactions = transactions_response.json()
    assert len(transactions) == 2
    assert transactions[0]["transaction_type"] == "top_up"
    assert transactions[0]["amount"] == 50
