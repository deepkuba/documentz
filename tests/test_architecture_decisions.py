import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]


class ArchitectureDecisionTests(unittest.TestCase):
    def test_architecture_decisions_are_complete(self) -> None:
        required_adrs = {
            "docs/adr/0001-python-toolchain.md",
            "docs/adr/0002-portal-toolchain.md",
            "docs/adr/0003-oauth-and-jobs.md",
        }
        missing_adrs = sorted(path for path in required_adrs if not (ROOT / path).is_file())
        self.assertEqual([], missing_adrs, f"missing toolchain ADRs: {missing_adrs}")

        manifest_path = ROOT / "toolchain.toml"
        self.assertTrue(manifest_path.is_file(), "toolchain.toml must pin foundation choices")
        manifest = manifest_path.read_text(encoding="utf-8")

        required_choices = {
            "runtime": ("python", "node"),
            "package_manager": ("python", "javascript"),
            "backend": ("oauth", "jobs", "formatter_linter", "type_checker", "test_runner"),
            "portal": ("ui", "build", "test_runner", "linter", "formatter", "type_checker"),
        }
        for section, names in required_choices.items():
            for name in names:
                table = rf"\[{section}\.{name}\](.*?)(?=\n\[|\Z)"
                match = re.search(table, manifest, re.DOTALL)
                self.assertIsNotNone(match, f"missing choice {section}.{name}")
                choice = match.group(1)
                self.assertRegex(choice, r'(?m)^name = "[^"]+"$', f"{section}.{name} must name a tool")
                self.assertRegex(choice, r'(?m)^version = "\d+\.\d+\.\d+"$', f"{section}.{name} must be exactly pinned")
                self.assertRegex(choice, r'(?m)^evidence = "https://[^"]+"$', f"{section}.{name} needs compatibility evidence")

        bootstrap_path = ROOT / "BOOTSTRAP.md"
        self.assertTrue(bootstrap_path.is_file(), "BOOTSTRAP.md must define clean-checkout setup")
        bootstrap = bootstrap_path.read_text(encoding="utf-8")
        for command in (
            "uv-x86_64-unknown-linux-gnu.tar.gz",
            "node-v24.21.0-linux-x64.tar.xz",
            "sha256sum --check -",
            "uv sync --frozen",
            "corepack prepare pnpm@12.5.1 --activate",
            "pnpm install --frozen-lockfile",
        ):
            self.assertIn(command, bootstrap)

        portal_section = bootstrap.split("## Portal workspace", 1)[1]
        self.assertLess(
            portal_section.index("mkdir -p .tools/downloads .tools/node-v24.21.0"),
            portal_section.index("--output .tools/downloads/node.tar.xz"),
        )

        plan = (ROOT / "IMPLEMENTATION_PLAN.md").read_text(encoding="utf-8")
        self.assertIn(
            "- [x] Select and record the OAuth library, PostgreSQL job library, and frontend build stack in short ADRs.",
            plan,
        )


if __name__ == "__main__":
    unittest.main()
