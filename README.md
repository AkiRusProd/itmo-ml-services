# Apartment Price Service

Minimal backend scaffold for an ML service that predicts apartment prices.

## Overview

The project implements a scalable ML service for apartment price prediction with:
- JWT authentication
- internal credit-based billing
- asynchronous prediction processing through `Celery + Redis`
- PostgreSQL for persistent storage
- monitoring via `Prometheus + Grafana`
- user-facing analytics dashboard via `Streamlit`

It follows the project brief requirements for:
- REST API with Swagger
- asynchronous ML execution
- billing with transaction history
- Docker Compose deployment
- monitoring and dashboarding

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
- `GET /api/v1/models/current`
- `GET /api/v1/metrics`

## Architecture

Core services:
- `api` — FastAPI application with auth, billing, prediction endpoints, and Swagger
- `worker` — Celery worker that processes queued prediction jobs
- `db` — PostgreSQL database
- `redis` — broker/backend for Celery
- `prometheus` — metrics scraping
- `grafana` — metrics dashboards
- `dashboard` — Streamlit analytics app

Main persistence entities:
- `users`
- `wallets`
- `transactions`
- `prediction_requests`
- `prediction_results`
- `promo_codes`
- `promo_code_activations`
- `ml_models`

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

## Billing Logic

Billing is based on internal credits.

Implemented rules:
- each new user receives a welcome bonus;
- wallet top-up creates a transaction record;
- promo code activation creates a transaction record;
- credits are charged only after successful prediction completion;
- failed prediction must not create a charge transaction;
- all balance changes are reproducible from the transaction history.

Main transaction types:
- `bonus`
- `top_up`
- `promo_code`
- `prediction_charge`

This design matches the brief requirement for transparent and auditable billing.

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

## Model Metadata

Current active model metadata is available via:

- `GET /api/v1/models/current`

This endpoint returns the active model name, version, artifact path, target, and expected features.

## Tests

Run unit tests:

```bash
.venv/bin/pytest tests/unit -q
```

Run the full test suite:

```bash
.venv/bin/pytest tests -q
```

Notes:
- unit tests are green in the current environment;
- integration tests are included, but in the current sandbox they may be skipped because local socket binding is restricted.

## Manual Demo Checklist

1. Start the project:

```bash
cp .env.example .env
docker compose up --build
```

2. Open:
- Swagger: `http://127.0.0.1:8000/docs`
- Grafana: `http://127.0.0.1:3000`
- Streamlit: `http://127.0.0.1:8501`

3. Run the main user scenario:
- register a user;
- login and get JWT token;
- inspect wallet and transactions;
- optionally top up the wallet;
- redeem a promo code;
- create a prediction request;
- poll prediction status;
- verify final prediction result;
- verify credits were charged exactly once.

4. Inspect observability:
- Prometheus target scraping;
- Grafana dashboard panels;
- Streamlit business dashboard.

## Submission Notes

Before submission, it is worth confirming:
- full `docker compose up --build` run works end-to-end;
- Grafana dashboard loads correctly;
- Streamlit dashboard reads from PostgreSQL;
- `GET /api/v1/models/current` returns active model metadata;
- business plan file is attached: [BUSINESS_PLAN.md](/home/rustam/my-projects/itmo-ml-services/BUSINESS_PLAN.md)
