"""Safe executable logging configuration for the API process."""

from __future__ import annotations

import logging

_HANDLER_MARKER = "documentz_safe_request_handler"


def configure_request_logging() -> None:
    """Emit only the API's allowlisted request event, never raw server URLs."""
    logging.getLogger("uvicorn.access").disabled = True

    request_logger = logging.getLogger("documentz_api.request")
    if not any(getattr(handler, _HANDLER_MARKER, False) for handler in request_logger.handlers):
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(message)s"))
        setattr(handler, _HANDLER_MARKER, True)
        request_logger.addHandler(handler)
    request_logger.setLevel(logging.INFO)
    request_logger.propagate = False
