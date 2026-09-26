"""Structural and secret-safety checks for the production inventory."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[2]
INVENTORY = ROOT / "docs" / "operations" / "production-inventory.md"

REQUIRED_ITEMS = {
    "host-provider",
    "host-os",
    "host-architecture",
    "host-cpu",
    "host-memory",
    "host-disk",
    "host-administrator",
    "shared-caddy-owner",
    "shared-caddy-config",
    "public-port-ownership",
    "route-prefix",
    "discovery-routes",
    "dns-owner",
    "dns-name",
    "canonical-base-url",
    "tls-owner",
    "tailscale-tailnet",
    "tailscale-host-identity",
    "nas-owner",
    "nas-endpoint",
    "nas-backup-path",
    "nas-retention",
    "container-registry",
    "registry-namespace",
    "registry-publish-identity",
    "registry-pull-identity",
    "deployment-operator",
    "deployment-access",
    "deployment-approval",
    "production-config-location",
    "mounted-secret-directory",
    "database-credential",
    "database-migration-credential",
    "database-backup-credential",
    "oidc-credential",
    "oauth-signing-key",
    "session-signing-key",
    "restic-repository-credential",
    "restic-encryption-key",
    "backup-key-escrow",
    "backup-schedule-owner",
    "backup-alert-destination",
    "local-backup-buffer",
    "restore-operator",
    "restore-sandbox",
    "purge-tombstone-source",
    "purge-ledger-storage",
    "index-rebuild-capacity",
}


class ProductionInventoryTest(unittest.TestCase):
    def test_production_inventory_has_all_required_nonsecret_values(self) -> None:
        text = INVENTORY.read_text(encoding="utf-8")
        found = set(re.findall(r"<!-- inventory:([a-z0-9-]+) -->", text))
        self.assertEqual(REQUIRED_ITEMS, found)

        for item in REQUIRED_ITEMS:
            row = re.search(
                rf"<!-- inventory:{item} -->\n\| .*? \| "
                r"`(confirmed|owner-required|dependent-task)` \| "
                r".*? \| .*? \| .*? \| .*? \|",
                text,
            )
            self.assertIsNotNone(row, f"{item} lacks the complete inventory row")

        self.assertIn("**Deployment ready:** No", text)
        self.assertIn("## Collection and verification runbook", text)

    def test_production_inventory_contains_no_secret_values(self) -> None:
        text = INVENTORY.read_text(encoding="utf-8")
        prohibited = (
            r"(?i)-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
            r"(?i)(?:password|token|secret|private_key)\s*[:=]\s*[\"']?[A-Za-z0-9+/=_-]{12,}",
            r"gh[opsu]_[A-Za-z0-9]{20,}",
        )
        for pattern in prohibited:
            self.assertNotRegex(text, pattern)


if __name__ == "__main__":
    unittest.main()
