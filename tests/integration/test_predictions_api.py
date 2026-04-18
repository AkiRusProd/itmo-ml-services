import time


def test_predictions_create_list_get_and_charge_flow(client, auth_headers):
    create_response = client.post(
        "/api/v1/predictions",
        json={
            "MedInc": 8.3252,
            "HouseAge": 41.0,
            "AveRooms": 6.9841,
            "AveBedrms": 1.0238,
            "Population": 322.0,
            "AveOccup": 2.5556,
            "Latitude": 37.88,
            "Longitude": -122.23,
            "cost_credits": 10,
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["status"] in {"queued", "processing", "completed"}

    deadline = time.time() + 10
    detail = None
    while time.time() < deadline:
        detail_response = client.get(
            f"/api/v1/predictions/{created['id']}",
            headers=auth_headers,
        )
        assert detail_response.status_code == 200
        detail = detail_response.json()
        if detail["status"] == "completed":
            break
        time.sleep(0.2)

    assert detail is not None
    assert detail["status"] == "completed"
    assert detail["prediction"] is not None
    assert detail["model_name"] == "apartment_price_model"

    list_response = client.get("/api/v1/predictions", headers=auth_headers)
    assert list_response.status_code == 200
    predictions = list_response.json()
    assert len(predictions) == 1
    assert predictions[0]["status"] == "completed"

    wallet_response = client.get("/api/v1/wallet", headers=auth_headers)
    assert wallet_response.status_code == 200
    assert wallet_response.json()["balance"] == 90
