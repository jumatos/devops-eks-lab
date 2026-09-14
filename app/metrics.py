from time import perf_counter

from prometheus_client import CollectorRegistry, Counter, Histogram
from starlette.types import ASGIApp, Message, Receive, Scope, Send


REGISTRY = CollectorRegistry()

HTTP_REQUESTS = Counter(
    "task_api_http_requests_total",
    "Total HTTP requests.",
    labelnames=("method", "route", "status_code"),
    registry=REGISTRY,
)

HTTP_DURATION = Histogram(
    "task_api_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    labelnames=("method", "route"),
    registry=REGISTRY,
)

KNOWN_METHODS = {
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "HEAD",
    "OPTIONS",
    "TRACE",
    "CONNECT",
}


class MetricsMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http" or scope["path"] == "/metrics":
            await self.app(scope, receive, send)
            return

        started = perf_counter()
        status_code = 500

        async def send_with_metrics(message: Message) -> None:
            nonlocal status_code

            if message["type"] == "http.response.start":
                status_code = message["status"]

            await send(message)

        try:
            await self.app(scope, receive, send_with_metrics)
        finally:
            matched_route = scope.get("route")
            route = getattr(matched_route, "path", "unmatched")

            method = scope["method"]
            if method not in KNOWN_METHODS:
                method = "OTHER"

            HTTP_REQUESTS.labels(
                method=method,
                route=route,
                status_code=str(status_code),
            ).inc()

            HTTP_DURATION.labels(
                method=method,
                route=route,
            ).observe(perf_counter() - started)