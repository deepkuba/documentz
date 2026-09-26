import json
import subprocess
import unittest
from pathlib import Path

from documentz_api import package_identity as api_identity
from documentz_application import package_identity as application_identity
from documentz_domain import package_identity as domain_identity
from documentz_infrastructure import package_identity as infrastructure_identity
from documentz_worker import package_identity as worker_identity


class PythonWorkspaceSmokeTests(unittest.TestCase):
    ROOT = Path(__file__).resolve().parents[1]
    DISTRIBUTIONS = {
        "documentz-api": (
            Path("apps/api"),
            "documentz_api",
            [
                "authlib==1.8.0",
                "documentz-application",
                "documentz-infrastructure",
                "fastapi==0.141.1",
                "pydantic-settings==2.15.0",
            ],
        ),
        "documentz-application": (
            Path("packages/application"),
            "documentz_application",
            ["documentz-domain"],
        ),
        "documentz-domain": (Path("packages/domain"), "documentz_domain", []),
        "documentz-infrastructure": (
            Path("packages/infrastructure"),
            "documentz_infrastructure",
            [
                "alembic==1.20.0",
                "documentz-application",
                "documentz-domain",
                "procrastinate==3.10.0",
                "psycopg==3.3.6",
                "sqlalchemy==2.1.1",
            ],
        ),
        "documentz-worker": (
            Path("apps/worker"),
            "documentz_worker",
            [
                "documentz-application",
                "documentz-infrastructure",
                "procrastinate==3.10.0",
            ],
        ),
    }

    def test_python_workspace_smoke(self) -> None:
        identities = {
            api_identity(),
            application_identity(),
            domain_identity(),
            infrastructure_identity(),
            worker_identity(),
        }

        self.assertEqual(
            identities,
            {
                "documentz-api",
                "documentz-application",
                "documentz-domain",
                "documentz-infrastructure",
                "documentz-worker",
            },
        )

        uv = self.ROOT / ".tools/uv-0.12.19/uv"
        probe = """
import importlib
import importlib.metadata
import json
import sys

distribution, module, expected = sys.argv[1:]
actual = importlib.metadata.requires(distribution) or []
assert actual == json.loads(expected), (distribution, actual)
imported = importlib.import_module(module)
assert imported.package_identity() == distribution
"""
        for distribution, (project, module, dependencies) in self.DISTRIBUTIONS.items():
            with self.subTest(distribution=distribution):
                subprocess.run(
                    [
                        uv,
                        "run",
                        "--isolated",
                        "--project",
                        project,
                        "--no-dev",
                        "--offline",
                        "python",
                        "-I",
                        "-c",
                        probe,
                        distribution,
                        module,
                        json.dumps(dependencies),
                    ],
                    cwd=self.ROOT,
                    check=True,
                )


if __name__ == "__main__":
    unittest.main()
