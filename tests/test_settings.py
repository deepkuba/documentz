import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from documentz_api.settings import load_api_settings
from documentz_worker.settings import load_worker_settings
from pydantic import ValidationError


class SettingsTests(unittest.TestCase):
    def test_production_config_requires_canonical_base_url(self) -> None:
        invalid_urls = (
            None,
            "http://context.example/d",
            "https://context.example/",
            "https://context.example/prefix/d",
            "https://context.example/d/",
            "https://user@context.example/d",
            "https://context.example:443/d",
            "https://context.example/d?source=alias",
            "https://context.example/d#fragment",
        )

        for loader in (load_api_settings, load_worker_settings):
            for external_base_url in invalid_urls:
                with self.subTest(loader=loader.__name__, external_base_url=external_base_url):
                    environment = {
                        "DOCUMENTZ_ENVIRONMENT": "production",
                        "DOCUMENTZ_DATABASE_URL": "postgresql+psycopg://documentz@db/documentz",
                    }
                    if external_base_url is not None:
                        environment["DOCUMENTZ_EXTERNAL_BASE_URL"] = external_base_url
                    with (
                        tempfile.TemporaryDirectory() as secrets_dir,
                        patch.dict(os.environ, environment, clear=True),
                        self.assertRaisesRegex(ValidationError, "external_base_url"),
                    ):
                        loader(secrets_dir=Path(secrets_dir))

    def test_mounted_secret_uses_the_exact_documentz_name(self) -> None:
        sentinel = "postgresql+psycopg://owner:lowercase-sentinel@db/documentz"
        with tempfile.TemporaryDirectory() as secrets_dir:
            directory = Path(secrets_dir)
            (directory / "documentz_database_url").write_text(sentinel, encoding="utf-8")

            with patch.dict(os.environ, {}, clear=True):
                settings = load_api_settings(secrets_dir=directory)

        self.assertNotEqual(settings.database_url.get_secret_value(), sentinel)

    def test_local_defaults_are_safe_and_shared(self) -> None:
        with tempfile.TemporaryDirectory() as secrets_dir, patch.dict(os.environ, {}, clear=True):
            api = load_api_settings(secrets_dir=Path(secrets_dir))
            worker = load_worker_settings(secrets_dir=Path(secrets_dir))

        for settings in (api, worker):
            with self.subTest(settings=type(settings).__name__):
                self.assertEqual(settings.environment, "local")
                self.assertEqual(str(settings.external_base_url), "http://localhost:8000/d")
                self.assertEqual(
                    settings.database_url.get_secret_value(),
                    "postgresql+psycopg://documentz@localhost:5432/documentz",
                )

    def test_api_and_worker_load_strictly_named_mounted_settings(self) -> None:
        sentinel = "postgresql+psycopg://owner:mounted-sentinel@db/documentz"
        with tempfile.TemporaryDirectory() as secrets_dir:
            directory = Path(secrets_dir)
            (directory / "DOCUMENTZ_DATABASE_URL").write_text(sentinel, encoding="utf-8")

            with patch.dict(
                os.environ,
                {"DOCUMENTZ_SECRETS_DIR": str(directory)},
                clear=True,
            ):
                api = load_api_settings()
                worker = load_worker_settings()

        self.assertEqual(api.database_url.get_secret_value(), sentinel)
        self.assertEqual(worker.database_url.get_secret_value(), sentinel)
        self.assertNotIn(sentinel, repr(api))
        self.assertNotIn(sentinel, repr(worker))

    def test_valid_production_settings_are_shared(self) -> None:
        environment = {
            "DOCUMENTZ_ENVIRONMENT": "production",
            "DOCUMENTZ_EXTERNAL_BASE_URL": "https://context.example/d",
            "DOCUMENTZ_DATABASE_URL": "postgresql+psycopg://documentz@db/documentz",
        }
        with (
            tempfile.TemporaryDirectory() as secrets_dir,
            patch.dict(os.environ, environment, clear=True),
        ):
            api = load_api_settings(secrets_dir=Path(secrets_dir))
            worker = load_worker_settings(secrets_dir=Path(secrets_dir))

        self.assertEqual(str(api.external_base_url), "https://context.example/d")
        self.assertEqual(str(worker.external_base_url), "https://context.example/d")

    def test_production_requires_explicit_valid_database_url(self) -> None:
        for database_url in (None, "", "sqlite:///documentz.db", "not-a-url"):
            with self.subTest(database_url=database_url):
                environment = {
                    "DOCUMENTZ_ENVIRONMENT": "production",
                    "DOCUMENTZ_EXTERNAL_BASE_URL": "https://context.example/d",
                }
                if database_url is not None:
                    environment["DOCUMENTZ_DATABASE_URL"] = database_url
                with (
                    tempfile.TemporaryDirectory() as secrets_dir,
                    patch.dict(os.environ, environment, clear=True),
                    self.assertRaisesRegex(ValidationError, "database_url"),
                ):
                    load_api_settings(secrets_dir=Path(secrets_dir))

    def test_production_validation_does_not_leak_mounted_secrets(self) -> None:
        sentinel = "postgresql+psycopg://owner:never-print-this@db/documentz"
        with tempfile.TemporaryDirectory() as secrets_dir:
            directory = Path(secrets_dir)
            (directory / "DOCUMENTZ_DATABASE_URL").write_text(sentinel, encoding="utf-8")

            with patch.dict(
                os.environ,
                {"DOCUMENTZ_ENVIRONMENT": "production"},
                clear=True,
            ):
                with self.assertRaises(ValidationError) as raised:
                    load_api_settings(secrets_dir=directory)

        self.assertNotIn(sentinel, str(raised.exception))


if __name__ == "__main__":
    unittest.main()
