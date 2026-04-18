from __future__ import annotations

import time
from typing import Callable

from fastapi import Request, Response
from prometheus_client import Counter, Gauge, Histogram, generate_latest
from starlette.responses import Response as StarletteResponse


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

CREDITS_CHARGED_TOTAL = Counter(
    "credits_charged_total",
    "Total number of credits charged for successful predictions.",
)

WALLET_TOPUPS_TOTAL = Counter(
    "wallet_topups_total",
    "Total number of mock wallet top-ups.",
)

WALLET_TOPUP_CREDITS_TOTAL = Counter(
    "wallet_topup_credits_total",
    "Total number of credits added via wallet top-up.",
)

PROMO_CODE_REDEMPTIONS_TOTAL = Counter(
    "promo_code_redemptions_total",
    "Total number of successful promo code redemptions.",
)

PROMO_CODE_CREDITS_TOTAL = Counter(
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
