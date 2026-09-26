"""Small database connectivity boundary for API readiness."""

from __future__ import annotations

from pydantic import SecretStr
from sqlalchemy import Engine, create_engine, text


class DatabaseReadiness:
    """Own a bounded connection pool and expose a content-free readiness probe."""

    def __init__(self, database_url: SecretStr) -> None:
        self._engine: Engine = create_engine(
            database_url.get_secret_value(),
            connect_args={"connect_timeout": 2},
            pool_pre_ping=True,
            pool_size=2,
            max_overflow=0,
            pool_timeout=2,
        )

    def __call__(self) -> bool:
        with self._engine.connect() as connection:
            return connection.execute(text("SELECT 1")).scalar_one() == 1

    def close(self) -> None:
        self._engine.dispose()
