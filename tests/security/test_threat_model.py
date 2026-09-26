from pathlib import Path
import unittest


ROOT = Path(__file__).parents[2]
THREAT_MODEL = ROOT / "docs" / "security" / "THREAT_MODEL.md"


class ThreatModelDocumentationTests(unittest.TestCase):
    def test_threat_model_covers_every_declared_trust_boundary(self) -> None:
        self.assertTrue(THREAT_MODEL.is_file(), "security threat model does not exist")

        text = THREAT_MODEL.read_text(encoding="utf-8").casefold()
        required_boundaries = {
            "management portal",
            "oauth and oidc",
            "mcp adapter",
            "http api",
            "background worker",
            "postgresql database",
            "embedding service",
            "shared caddy reverse proxy",
            "nas backup target",
            "restore environment",
        }

        missing = sorted(boundary for boundary in required_boundaries if boundary not in text)
        self.assertEqual([], missing, f"missing trust boundaries: {', '.join(missing)}")

        for section in (
            "## Assets",
            "## Trust boundaries and data flows",
            "## Attacker-controlled inputs",
            "## Authorization boundaries",
            "## Destructive actions",
            "## Backup and restore exposure",
            "## Required security tests",
            "## Security review workflow",
        ):
            self.assertIn(section.casefold(), text)

        for purge_recovery_control in (
            "independently durable",
            "append-only",
            "backup checkpoints",
            "missing ledger",
            "tombstones committed after",
        ):
            self.assertIn(purge_recovery_control, text)


if __name__ == "__main__":
    unittest.main()
