# Apartment Price Service

Minimal backend scaffold for an ML service that predicts apartment prices.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Available endpoints

- `GET /`
- `GET /api/v1/health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/users/me`
- `GET /api/v1/wallet`
- `GET /api/v1/wallet/transactions`
- `POST /api/v1/predictions`
- `GET /api/v1/predictions`
- `GET /api/v1/predictions/{id}`

## Example request

```json
{
  "MedInc": 8.3252,
  "HouseAge": 41.0,
  "AveRooms": 6.9841,
  "AveBedrms": 1.0238,
  "Population": 322.0,
  "AveOccup": 2.5556,
  "Latitude": 37.88,
  "Longitude": -122.23
}
```

## Authentication flow

1. Register:

```json
{
  "email": "user@example.com",
  "password": "strongpass123",
  "full_name": "Rustam User"
}
```

2. Login and get `access_token`.
3. Pass `Authorization: Bearer <token>` to protected endpoints.

## Prediction flow

`POST /api/v1/predictions` is now protected and persists both:
- the incoming prediction request with status and input payload;
- the resulting prediction value and model metadata.

For the current MVP the task runs inline, but each request already stores a `task_id`.
That gives us a clean migration path to `Celery + Redis` later without changing the API contract.

## Database and migrations

By default the app uses local SQLite via `DATABASE_URL=sqlite:///./app.db`.
You can later switch to PostgreSQL by overriding `DATABASE_URL`.

Alembic scaffold is included:

```bash
alembic upgrade head
```
