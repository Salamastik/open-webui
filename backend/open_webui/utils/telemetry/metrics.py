"""OpenTelemetry metrics bootstrap for Open WebUI.

This module initialises a MeterProvider that sends metrics to an OTLP
collector. The collector is responsible for exposing a Prometheus
`/metrics` endpoint – WebUI does **not** expose it directly.

Metrics collected:

* http.server.requests (counter)
* http.server.duration (histogram, milliseconds)

Attributes used: http.method, http.route, http.status_code

If you wish to add more attributes (e.g. user-agent) you can, but beware of
high-cardinality label sets.
"""

from __future__ import annotations

import time
from typing import Dict, List, Sequence, Any
import asyncio
import httpx
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.view import View
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

from open_webui.env import OTEL_SERVICE_NAME, OTEL_EXPORTER_OTLP_ENDPOINT

from open_webui.routers.users import get_users

_EXPORT_INTERVAL_MILLIS = 10_000  # 10 seconds


def _build_meter_provider() -> MeterProvider:
    """Return a configured MeterProvider."""

    # Periodic reader pushes metrics over OTLP/gRPC to collector
    readers: List[PeriodicExportingMetricReader] = [
        PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=OTEL_EXPORTER_OTLP_ENDPOINT),
            export_interval_millis=_EXPORT_INTERVAL_MILLIS,
        )
    ]

    # Optional view to limit cardinality: drop user-agent etc.
    views: List[View] = [
        View(
            instrument_name="http.server.duration",
            attribute_keys=["http.method", "http.route", "http.status_code"],
        ),
        View(
            instrument_name="http.server.requests",
            attribute_keys=["http.method", "http.route", "http.status_code"],
        ),
    ]

    provider = MeterProvider(
        resource=Resource.create({SERVICE_NAME: OTEL_SERVICE_NAME}),
        metric_readers=list(readers),
        views=views,
    )
    return provider


def setup_metrics(app: FastAPI) -> None:
    """Attach OTel metrics middleware to *app* and initialise provider."""

    metrics.set_meter_provider(_build_meter_provider())
    meter = metrics.get_meter(__name__)

    # Instruments
    request_counter = meter.create_counter(
        name="http.server.requests",
        description="Total HTTP requests",
        unit="1",
    )
    duration_histogram = meter.create_histogram(
        name="http.server.duration",
        description="HTTP request duration",
        unit="ms",
    )

    # Active users in the last hour (ObservableGauge)
    def get_active_users_last_hour_callback(options):
        try:
            # get_users is async, so we must run it in a sync context
            import asyncio

            users_response = asyncio.run(get_users(user=None))
            users = users_response.get("users", []) if isinstance(users_response, dict) else []
            now = int(time.time())
            one_hour_ago = now - 3600
            active_count = 0
            for user in users:
                user_dict = jsonable_encoder(user)
                last_active_at = user_dict.get("last_active_at")
                print(now, "   now", last_active_at, "   last_active_at", one_hour_ago, "   one_hour_ago")
                if isinstance(last_active_at, int) and last_active_at >= one_hour_ago:
                    active_count += 1
            return [metrics.Observation(active_count)]
        except Exception:
            return [metrics.Observation(0)]

    meter.create_observable_gauge(
        name="active_users_last_hour",
        callbacks=[get_active_users_last_hour_callback],
        description="Number of users active in the last hour",
        unit="1",
    )

    # FastAPI middleware
    @app.middleware("http")
    async def _metrics_middleware(request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        # Route template e.g. "/items/{item_id}" instead of real path.
        route = request.scope.get("route")
        route_path = getattr(route, "path", request.url.path)

        attrs: Dict[str, str | int] = {
            "http.method": request.method,
            "http.route": route_path,
            "http.status_code": response.status_code,
        }

        request_counter.add(1, attrs)
        duration_histogram.record(elapsed_ms, attrs)

        return response
