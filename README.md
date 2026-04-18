# Apartment Price Service

Minimal backend scaffold for an ML service that predicts apartment prices.

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Run with Docker Compose

```bash
cp .env.example .env
docker compose up --build
```

Services:
- API: `http://127.0.0.1:8000`
- Swagger: `http://127.0.0.1:8000/docs`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- Celery worker: background prediction processing
- Prometheus: `http://127.0.0.1:9090`
- Grafana: `http://127.0.0.1:3000` (`admin` / `admin`)
- Streamlit dashboard: `http://127.0.0.1:8501`

To seed a demo admin and promo code locally:

```bash
.venv/bin/python scripts/seed_demo_data.py
```

## Available endpoints

- `GET /`
- `GET /api/v1/health`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/users/me`
- `GET /api/v1/wallet`
- `POST /api/v1/wallet/top-up`
- `GET /api/v1/wallet/transactions`
- `POST /api/v1/promo-codes`
- `POST /api/v1/promo-codes/redeem`
- `POST /api/v1/predictions`
- `GET /api/v1/predictions`
- `GET /api/v1/predictions/{id}`
- `GET /api/v1/metrics`

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

Predictions now run through `Celery + Redis`:
- API creates a `prediction_request` with status `queued`;
- worker picks it up and updates it to `processing/completed/failed`;
- client polls `GET /api/v1/predictions` or `GET /api/v1/predictions/{id}`.

For local smoke tests you can force synchronous execution with:

```bash
CELERY_TASK_ALWAYS_EAGER=true uvicorn app.main:app --reload
```

## Database and migrations

By default the app uses local SQLite via `DATABASE_URL=sqlite:///./app.db`.
You can later switch to PostgreSQL by overriding `DATABASE_URL`.

Alembic scaffold is included:

```bash
alembic upgrade head
```

For Docker Compose the default database URL is PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg://app_user:app_password@db:5432/apartment_service
REDIS_URL=redis://redis:6379/0
CELERY_TASK_ALWAYS_EAGER=false
```

## Monitoring

Prometheus scrapes the API metrics endpoint:

- `GET /api/v1/metrics`

Grafana is provisioned automatically with:
- a Prometheus datasource
- an overview dashboard for request rate, latency, prediction outcomes, queue depth, and credits

## Analytics Dashboard

Streamlit dashboard is available at:

- `http://127.0.0.1:8501`

It shows:
- total users
- total and successful predictions
- credits charged, topped up, and issued via promo codes
- prediction activity by day
- credits flow by day
- recent predictions and transactions
