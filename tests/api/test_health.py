"""Public HTTP contract tests for API process health."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from typing import Any, cast

from documentz_api.app import create_app


def _request(
    app: Any,
    path: str,
    *,
    headers: dict[str, str] | None = None,
    query_string: bytes = b"",
) -> tuple[int, dict[str, str], dict[str, str]]:
    """Issue one dependency-free HTTP request at the ASGI boundary."""
    messages: list[dict[str, Any]] = []
    request_sent = False

    async def receive() -> dict[str, Any]:
        nonlocal request_sent
        if not request_sent:
            request_sent = True
            return {"type": "http.request", "body": b"", "more_body": False}
        return {"type": "http.disconnect"}

    async def send(message: dict[str, Any]) -> None:
        messages.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.3"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": query_string,
        "headers": [
            (key.lower().encode("latin-1"), value.encode("latin-1"))
            for key, value in (headers or {}).items()
        ],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
        "root_path": "",
    }
    asyncio.run(app(scope, receive, send))

    start = next(message for message in messages if message["type"] == "http.response.start")
    body = b"".join(
        message.get("body", b"") for message in messages if message["type"] == "http.response.body"
    )
    headers = {
        key.decode("latin-1").lower(): value.decode("latin-1") for key, value in start["headers"]
    }
    return start["status"], headers, cast(dict[str, str], json.loads(body))


def test_api_health_http_contract() -> None:
    """Liveness is process-only and readiness checks the configured database."""
    calls = 0

    def database_is_ready() -> bool:
        nonlocal calls
        calls += 1
        return True

    app = create_app(settings=cast(Any, object()), readiness_probe=database_is_ready)

    live_status, live_headers, live_body = _request(app, "/health/live")
    assert (live_status, live_body) == (200, {"status": "live"})
    assert live_headers["x-request-id"]
    assert calls == 0

    ready_status, ready_headers, ready_body = _request(app, "/health/ready")
    assert (ready_status, ready_body) == (200, {"status": "ready"})
    assert ready_headers["x-request-id"]
    assert calls == 1


def test_readiness_fails_safely_when_database_is_unavailable() -> None:
    """Connection details and driver failures never cross the HTTP boundary."""

    def unavailable_database() -> bool:
        raise RuntimeError("postgresql://owner:sentinel-password@database/documentz")

    app = create_app(settings=cast(Any, object()), readiness_probe=unavailable_database)

    ready_status, ready_headers, ready_body = _request(app, "/health/ready")
    assert ready_status == 503
    assert ready_body == {"status": "not_ready"}
    assert ready_headers["x-request-id"]
    assert "sentinel" not in json.dumps(ready_body)


def test_request_logging_correlates_without_sensitive_input(
    caplog: Any,
) -> None:
    """Request telemetry is structured and excludes attacker-controlled secrets."""
    caplog.set_level(logging.INFO, logger="documentz_api.request")
    app = create_app(settings=cast(Any, object()), readiness_probe=lambda: True)

    status_code, response_headers, _ = _request(
        app,
        "/health/live",
        headers={
            "X-Request-ID": "correlation-123",
            "Authorization": "Bearer sentinel-token",
            "Cookie": "session=sentinel-cookie",
            "X-Client-Secret": "sentinel-client-secret",
        },
        query_string=b"query=sentinel-query",
    )

    assert status_code == 200
    assert response_headers["x-request-id"] == "correlation-123"
    event = json.loads(caplog.records[-1].getMessage())
    assert event == {
        "event": "http_request",
        "method": "GET",
        "request_id": "correlation-123",
        "route": "/health/live",
        "status_code": 200,
    }
    assert "sentinel" not in caplog.text

    _, unsafe_headers, _ = _request(
        app,
        "/health/live",
        headers={"X-Request-ID": "sentinel\ninjected-log-line"},
    )
    assert unsafe_headers["x-request-id"] != "sentinel\ninjected-log-line"
    assert re.fullmatch(r"[0-9a-f-]{36}", unsafe_headers["x-request-id"])
    assert "injected-log-line" not in caplog.text
