"""Completeness checks for the framework-neutral public contract examples."""

import json
from collections import Counter
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).parents[2]
EXAMPLES = ROOT / "docs" / "public-contract-examples.md"

HTTP_OPERATIONS = {
    "list-projects",
    "create-project",
    "get-project",
    "update-project",
    "archive-project",
    "list-contexts",
    "store-context",
    "get-context",
    "update-context",
    "list-document-snapshots",
    "get-document-snapshot",
    "change-context-lifecycle",
    "create-fragment-set",
    "get-fragment-set",
    "put-fragment",
    "publish-fragment-set",
    "abandon-fragment-set",
    "list-summary-requests",
    "decline-summary-request",
    "search-context",
}

MCP_TOOLS = {
    "list_projects",
    "create_project",
    "update_project",
    "archive_project",
    "list_contexts",
    "store_context",
    "get_context",
    "update_context",
    "change_context_lifecycle",
    "list_document_snapshots",
    "get_document_snapshot",
    "create_fragment_set",
    "get_fragment_set",
    "publish_fragment_set",
    "abandon_fragment_set",
    "list_summary_requests",
    "decline_summary_request",
    "search_context",
}


class CanonicalContractExamplesTest(unittest.TestCase):
    def test_canonical_examples_are_complete(self) -> None:
        """Every planned operation has request/input, success, and error examples."""
        text = EXAMPLES.read_text(encoding="utf-8")

        for interface, planned in (("http", HTTP_OPERATIONS), ("mcp", MCP_TOOLS)):
            markers = re.findall(
                rf"<!-- example:{interface}:([a-z0-9_-]+):(request|success|error) -->", text
            )
            counts = Counter(markers)
            expected = {
                (operation, example_kind)
                for operation in planned
                for example_kind in ("request", "success", "error")
            }
            self.assertEqual(expected, set(counts), f"unexpected {interface} canonical markers")
            duplicates = sorted(marker for marker, count in counts.items() if count != 1)
            self.assertFalse(duplicates, f"duplicate {interface} canonical markers: {duplicates}")
            found = set(markers)
            missing = {
                (operation, example_kind)
                for operation in planned
                for example_kind in ("request", "success", "error")
                if (operation, example_kind) not in found
            }
            self.assertFalse(missing, f"missing {interface} canonical examples: {sorted(missing)}")

        blocks = re.findall(
            r"<!-- example:(http|mcp):([a-z0-9_-]+):(request|success|error) -->\n"
            r"(.*?)(?=\n<!-- example:|\n### |\n## |\Z)",
            text,
            flags=re.DOTALL,
        )
        self.assertEqual(3 * (len(HTTP_OPERATIONS) + len(MCP_TOOLS)), len(blocks))
        for interface, operation, kind, body in blocks:
            self.assertTrue(
                body.lstrip().startswith("`"),
                f"{interface}:{operation}:{kind} is disconnected from its example",
            )

        for required_section in (
            "## Contract conventions",
            "## Document projections",
            "## Cursor envelopes",
            "## Stable errors",
            "## Security and trust-boundary notes",
        ):
            self.assertIn(required_section, text)

        self.assertNotRegex(text, r"(?i)\b(TODO|TBD|to be decided|unresolved)\b")

    def test_canonical_json_examples_are_valid(self) -> None:
        """Every JSON fence is usable as a literal contract fixture."""
        text = EXAMPLES.read_text(encoding="utf-8")
        examples = re.findall(r"```json\n(.*?)\n```", text, flags=re.DOTALL)
        self.assertGreater(len(examples), 0)
        for index, example in enumerate(examples, start=1):
            with self.subTest(example=index):
                json.loads(example)

    def test_canonical_examples_do_not_contain_secret_material(self) -> None:
        """Examples must not normalize copying credentials into documentation."""
        text = EXAMPLES.read_text(encoding="utf-8")
        prohibited = (
            r"(?i)authorization:\s*bearer\s+\S+",
            r"(?i)client_secret\s*[:=]",
            r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        )
        for pattern in prohibited:
            self.assertNotRegex(text, pattern)

    def test_mcp_errors_use_the_protocol_error_signal(self) -> None:
        text = EXAMPLES.read_text(encoding="utf-8")
        self.assertIn("`CallToolResult.isError`", text)
        self.assertNotIn('"is_error"', text)

        for operation in MCP_TOOLS:
            marker = f"<!-- example:mcp:{operation}:error -->"
            example = text.split(marker, 1)[1].split("```json\n", 1)[1].split("\n```", 1)[0]
            self.assertEqual({"error"}, set(json.loads(example)))

    def test_snapshot_and_project_update_contracts_are_unambiguous(self) -> None:
        text = EXAMPLES.read_text(encoding="utf-8")
        self.assertIn("Historical snapshot projections are separate", text)
        self.assertRegex(text, r"Snapshot responses do\s+not contain")

        marker = "<!-- example:mcp:update_project:request -->"
        request = text.split(marker, 1)[1].split("```json\n", 1)[1].split("\n```", 1)[0]
        self.assertNotIn("archived", json.loads(request))


if __name__ == "__main__":
    unittest.main()
