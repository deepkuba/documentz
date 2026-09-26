"""Typed startup configuration for the background worker adapter."""

from pathlib import Path

from documentz_infrastructure.settings import ServiceSettings, load_service_settings


class WorkerSettings(ServiceSettings):
    """Background worker runtime settings."""


def load_worker_settings(*, secrets_dir: Path | None = None) -> WorkerSettings:
    """Load and validate worker startup settings."""

    return load_service_settings(WorkerSettings, secrets_dir=secrets_dir)
