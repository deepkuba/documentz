"""FastAPI application factory for the public HTTP adapter."""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Callable
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING
from uuid import uuid4

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import RequestResponseEndpoint
from starlette.routing import Route

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from documentz_api.settings import ApiSettings

from documentz_api.database import DatabaseReadiness

ReadinessProbe = Callable[[], bool]
_REQUEST_ID_PATTERN = re.compile(r"[A-Za-z0-9._-]{1,64}")
_request_logger = logging.getLogger("documentz_api.request")


def _request_id(request: Request) -> str:
    supplied = request.headers.get("X-Request-ID", "")
    if _REQUEST_ID_PATTERN.fullmatch(supplied):
        return supplied
    return str(uuid4())


def create_app(
    *,
    settings: ApiSettings,
    readiness_probe: ReadinessProbe | None = None,
) -> FastAPI:
    """Build an API application with explicit process dependencies."""
    database_readiness = None
    if readiness_probe is None:
        database_readiness = DatabaseReadiness(settings.database_url)
        readiness_probe = database_readiness

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        try:
            yield
        finally:
            if database_readiness is not None:
                database_readiness.close()

    app = FastAPI(lifespan=lifespan)

    @app.middleware("http")
    async def log_request(request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = _request_id(request)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        route = request.scope.get("route")
        route_template = route.path if isinstance(route, Route) else "unmatched"
        _request_logger.info(
            json.dumps(
                {
                    "event": "http_request",
                    "method": request.method,
                    "request_id": request_id,
                    "route": route_template,
                    "status_code": response.status_code,
                },
                separators=(",", ":"),
                sort_keys=True,
            )
        )
        return response

    @app.get("/health/live")
    async def live() -> dict[str, str]:
        return {"status": "live"}

    @app.get("/health/ready")
    async def ready() -> Response:
        try:
            database_ready = await run_in_threadpool(readiness_probe)
        except Exception:  # Database/driver details must not cross the health boundary.
            database_ready = False
        if database_ready:
            return JSONResponse({"status": "ready"})
        return JSONResponse(
            {"status": "not_ready"}, status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    return app
