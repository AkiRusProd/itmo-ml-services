from __future__ import annotations

import time
from typing import Callable

from fastapi import Request, Response
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from starlette.responses import Response as StarletteResponse

from app.models.transaction import Transaction


HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests handled by the API.",
    ["method", "path", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds.",
    ["method", "path"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

PREDICTION_REQUESTS_TOTAL = Counter(
    "prediction_requests_total",
    "Number of prediction requests created by users.",
    ["status"],
)

PREDICTION_PROCESSING_TOTAL = Counter(
    "prediction_processing_total",
    "Number of prediction processing attempts by final status.",
    ["status"],
)

CREDITS_CHARGED_TOTAL = Gauge(
    "credits_charged_total",
    "Total number of credits charged for successful predictions.",
)

WALLET_TOPUPS_TOTAL = Gauge(
    "wallet_topups_total",
    "Total number of mock wallet top-ups.",
)

WALLET_TOPUP_CREDITS_TOTAL = Gauge(
    "wallet_topup_credits_total",
    "Total number of credits added via wallet top-up.",
)

PROMO_CODE_REDEMPTIONS_TOTAL = Gauge(
    "promo_code_redemptions_total",
    "Total number of successful promo code redemptions.",
)

PROMO_CODE_CREDITS_TOTAL = Gauge(
    "promo_code_credits_total",
    "Total number of credits issued through promo codes.",
)

PREDICTION_QUEUE_DEPTH = Gauge(
    "prediction_queue_depth",
    "Number of prediction requests currently waiting or processing.",
)


async def metrics_middleware(
    request: Request,
    call_next: Callable[[Request], Response],
) -> Response:
    path = request.url.path
    method = request.method
    start_time = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start_time

    HTTP_REQUESTS_TOTAL.labels(
        method=method,
        path=path,
        status_code=str(response.status_code),
    ).inc()
    HTTP_REQUEST_DURATION_SECONDS.labels(method=method, path=path).observe(duration)
    return response


def metrics_response() -> StarletteResponse:
    return StarletteResponse(generate_latest(), media_type="text/plain; version=0.0.4")


def sync_business_metrics_from_db(db: Session) -> None:
    charged_total = db.execute(
        select(func.coalesce(-func.sum(Transaction.amount), 0)).where(
            Transaction.transaction_type == "prediction_charge"
        )
    ).scalar_one()
    topups_total = db.execute(
        select(func.coalesce(func.count(Transaction.id), 0)).where(
            Transaction.transaction_type == "top_up"
        )
    ).scalar_one()
    topup_credits_total = db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.transaction_type == "top_up"
        )
    ).scalar_one()
    promo_redemptions_total = db.execute(
        select(func.coalesce(func.count(Transaction.id), 0)).where(
            Transaction.transaction_type == "promo_code"
        )
    ).scalar_one()
    promo_credits_total = db.execute(
        select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            Transaction.transaction_type == "promo_code"
        )
    ).scalar_one()

    CREDITS_CHARGED_TOTAL.set(float(charged_total))
    WALLET_TOPUPS_TOTAL.set(float(topups_total))
    WALLET_TOPUP_CREDITS_TOTAL.set(float(topup_credits_total))
    PROMO_CODE_REDEMPTIONS_TOTAL.set(float(promo_redemptions_total))
    PROMO_CODE_CREDITS_TOTAL.set(float(promo_credits_total))


def track_prediction_request_created(status: str) -> None:
    PREDICTION_REQUESTS_TOTAL.labels(status=status).inc()


def track_prediction_processing(status: str) -> None:
    PREDICTION_PROCESSING_TOTAL.labels(status=status).inc()


def track_credits_charged(amount: int) -> None:
    CREDITS_CHARGED_TOTAL.inc(amount)


def track_wallet_topup(amount: int) -> None:
    WALLET_TOPUPS_TOTAL.inc()
    WALLET_TOPUP_CREDITS_TOTAL.inc(amount)


def track_promo_code_redemption(amount: int) -> None:
    PROMO_CODE_REDEMPTIONS_TOTAL.inc()
    PROMO_CODE_CREDITS_TOTAL.inc(amount)


def set_prediction_queue_depth(value: int) -> None:
    PREDICTION_QUEUE_DEPTH.set(value)
