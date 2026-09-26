import ast
import json
import os
import subprocess
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
COMPOSE_FILE = REPOSITORY_ROOT / "compose.yaml"


class PostgresPgvectorSmokeTests(unittest.TestCase):
    def test_postgres_pgvector_smoke(self) -> None:
        result = subprocess.run(
            [
                "docker",
                "compose",
                "-f",
                str(COMPOSE_FILE),
                "--profile",
                "*",
                "config",
                "--format",
                "json",
            ],
            cwd=REPOSITORY_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        config = json.loads(result.stdout)

        self.assertIn("postgres", config["services"])
        self.assertIn("postgres-test", config["services"])
        development = config["services"]["postgres"]
        test = config["services"]["postgres-test"]

        expected_image = (
            "pgvector/pgvector@sha256:"
            "99a149d3c84cfb0f32d8da7d72737e4643468787220af2223418730f8e9e9cdc"
        )
        self.assertEqual(development["image"], expected_image)
        self.assertEqual(test["image"], expected_image)
        self.assertNotIn("ports", development)
        self.assertNotIn("ports", test)
        self.assertEqual(
            development["environment"]["POSTGRES_INITDB_ARGS"],
            "--auth-host=scram-sha-256 --data-checksums",
        )
        self.assertTrue(config["networks"]["database-development"]["internal"])
        self.assertTrue(config["networks"]["database-test"]["internal"])
        self.assertEqual(development["networks"], {"database-development": None})
        self.assertEqual(test["networks"], {"database-test": None})
        self.assertIn("postgres-development-data", config["volumes"])
        self.assertFalse(
            any(mount["target"] == "/var/lib/postgresql/data" for mount in test.get("volumes", []))
        )
        self.assertEqual(
            test["tmpfs"][0],
            "/var/lib/postgresql/data:rw,noexec,nosuid,size=512m,mode=0700",
        )
        self.assertNotEqual(development["secrets"][0]["source"], test["secrets"][0]["source"])

        init_sql = REPOSITORY_ROOT / "deploy/postgres/init/001-enable-vector.sql"
        self.assertEqual(
            init_sql.read_text(encoding="utf-8"),
            "CREATE EXTENSION IF NOT EXISTS vector;\n",
        )

        migration = REPOSITORY_ROOT / "migrations/versions/0001_empty_foundation.py"
        syntax_tree = ast.parse(migration.read_text(encoding="utf-8"))
        assignments = {
            node.target.id: ast.literal_eval(node.value)
            for node in syntax_tree.body
            if isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.value is not None
        }
        self.assertEqual(assignments["revision"], "0001_empty_foundation")
        self.assertIsNone(assignments["down_revision"])
        alembic_env = (REPOSITORY_ROOT / "migrations/env.py").read_text(encoding="utf-8")
        self.assertIn('os.environ.get("DOCUMENTZ_DATABASE_URL")', alembic_env)
        self.assertNotIn("postgresql://", alembic_env)
        smoke_script = REPOSITORY_ROOT / "scripts/postgres_pgvector_smoke.sh"
        self.assertTrue(os.access(smoke_script, os.X_OK))
        smoke_source = smoke_script.read_text(encoding="utf-8")
        self.assertIn(
            ".tools/uv-0.12.19/uv run --frozen alembic -c alembic.ini upgrade head",
            smoke_source,
        )
        self.assertNotIn("command -v alembic", smoke_source)
        self.assertNotIn("\nalembic -c alembic.ini", smoke_source)
        self.assertIn("SELECT extversion FROM pg_extension", smoke_source)

        quality_targets = (REPOSITORY_ROOT / "Makefile").read_text(encoding="utf-8")
        for target in ("ruff format", "ruff check", "mypy"):
            self.assertRegex(quality_targets, rf"{target} .*\bmigrations\b")

        infrastructure_manifest = (
            REPOSITORY_ROOT / "packages/infrastructure/pyproject.toml"
        ).read_text(encoding="utf-8")
        self.assertIn('"psycopg==3.3.6"', infrastructure_manifest)


if __name__ == "__main__":
    unittest.main()
