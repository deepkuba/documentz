"""Typed startup configuration for the public API adapter."""

from pathlib import Path

from documentz_infrastructure.settings import ServiceSettings, load_service_settings


class ApiSettings(ServiceSettings):
    """Public API runtime settings."""


def load_api_settings(*, secrets_dir: Path | None = None) -> ApiSettings:
    """Load and validate API startup settings."""

    return load_service_settings(ApiSettings, secrets_dir=secrets_dir)
