"""Typed runtime configuration shared by executable adapters."""

from __future__ import annotations

import os
from collections.abc import Callable
from enum import StrEnum
from pathlib import Path
from typing import Self, cast
from urllib.parse import urlsplit

from pydantic import AnyHttpUrl, Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError

DEFAULT_SECRETS_DIRECTORY = Path(".secrets")


class RuntimeEnvironment(StrEnum):
    """Supported runtime safety modes."""

    LOCAL = "local"
    TEST = "test"
    PRODUCTION = "production"


class ServiceSettings(BaseSettings):
    """Configuration shared by the API and background worker."""

    model_config = SettingsConfigDict(
        case_sensitive=True,
        extra="ignore",
        populate_by_name=True,
    )

    environment: RuntimeEnvironment = Field(
        RuntimeEnvironment.LOCAL, validation_alias="DOCUMENTZ_ENVIRONMENT"
    )
    external_base_url: AnyHttpUrl = Field(
        AnyHttpUrl("http://localhost:8000/d"),
        validation_alias="DOCUMENTZ_EXTERNAL_BASE_URL",
    )
    database_url: SecretStr = Field(
        SecretStr("postgresql+psycopg://documentz@localhost:5432/documentz"),
        validation_alias="DOCUMENTZ_DATABASE_URL",
    )

    @field_validator("external_base_url", mode="before")
    @classmethod
    def reject_explicit_default_port(cls, value: object) -> object:
        """Reject an ambiguous spelling of the canonical HTTPS origin."""

        if isinstance(value, str) and urlsplit(value).port == 443:
            raise ValueError("external_base_url must omit the default HTTPS port")
        return value

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: SecretStr) -> SecretStr:
        """Accept only a usable PostgreSQL URL through the pinned psycopg driver."""

        try:
            url = make_url(value.get_secret_value())
        except ArgumentError, ValueError:
            raise ValueError("database_url must be a PostgreSQL psycopg URL") from None
        if url.drivername != "postgresql+psycopg" or not url.host or not url.database:
            raise ValueError("database_url must be a PostgreSQL psycopg URL")
        return value

    @model_validator(mode="after")
    def validate_production_base_url(self) -> Self:
        """Fail closed unless production has one explicit canonical public URL."""

        if self.environment is not RuntimeEnvironment.PRODUCTION:
            return self
        if "external_base_url" not in self.model_fields_set:
            raise ValueError("external_base_url is required in production")
        if "database_url" not in self.model_fields_set:
            raise ValueError("database_url is required in production")

        url = self.external_base_url
        if (
            url.scheme != "https"
            or url.path != "/d"
            or url.username is not None
            or url.password is not None
            or url.query is not None
            or url.fragment is not None
        ):
            raise ValueError(
                "external_base_url must be an absolute HTTPS origin with the exact /d path"
            )
        return self


def load_service_settings[SettingsType: ServiceSettings](
    settings_type: type[SettingsType], *, secrets_dir: Path | None = None
) -> SettingsType:
    """Load environment variables and strictly named mounted secret files."""

    configured_directory = os.environ.get("DOCUMENTZ_SECRETS_DIR")
    effective_directory = (
        secrets_dir
        if secrets_dir is not None
        else Path(configured_directory)
        if configured_directory
        else DEFAULT_SECRETS_DIRECTORY
    )
    settings_constructor = cast(Callable[..., SettingsType], settings_type)
    return settings_constructor(_secrets_dir=effective_directory)
