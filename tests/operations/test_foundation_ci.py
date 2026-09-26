"""Contract checks for the executable foundation CI workflow."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "foundation.yml"


class FoundationCiTests(unittest.TestCase):
    def test_foundation_ci_covers_established_gates(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")

        for trigger in ("pull_request:", "push:", "branches: [main]"):
            self.assertIn(trigger, workflow)

        for gate in (
            "make format-check",
            "make lint",
            "make type-check",
            "make unit-test",
            "pnpm format-check",
            "pnpm lint",
            "pnpm type-check",
            "pnpm portal-test",
            "pnpm portal-build",
            "scripts/postgres_pgvector_smoke.sh development",
            "scripts/postgres_pgvector_smoke.sh test",
            "pip-audit==2.10.1",
            "pnpm audit --audit-level high",
            "gitleaks",
        ):
            self.assertIn(gate, workflow)

        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertIn("persist-credentials: false", workflow)
        self.assertNotRegex(workflow, r"(?m)^\s+uses: [^\n]+@(?![0-9a-f]{40}\s*$)")

        for runtime, version in (("PYTHON_VERSION", "3.14.7"), ("NODE_VERSION", "24.21.0")):
            self.assertRegex(workflow, rf'{runtime}: ["\']?{re.escape(version)}["\']?')

        self.assertIsNone(
            re.search(r"(?i)(password|token|secret):\s*[^$\s]", workflow),
            "CI must generate ephemeral values or use secret references",
        )


if __name__ == "__main__":
    unittest.main()
