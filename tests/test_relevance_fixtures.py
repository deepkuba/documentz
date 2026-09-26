import json
import unittest
from pathlib import Path

from tools.relevance_fixtures import load_fixture_set, score_rankings

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = REPOSITORY_ROOT / "tests" / "fixtures" / "relevance" / "multilingual.json"


class RelevanceFixtureTests(unittest.TestCase):
    def test_relevance_fixture_set_has_required_language_coverage(self) -> None:
        fixture_set = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

        coverage = {query["coverage"] for query in fixture_set["queries"]}

        self.assertEqual(coverage, {"english", "polish", "cross_language"})

    def test_fixture_set_has_required_scenarios_and_exhaustive_judgments(self) -> None:
        fixture_set = load_fixture_set(FIXTURE_PATH)

        roles = {document["fixture_role"] for document in fixture_set["documents"]}
        query_kinds = {query["kind"] for query in fixture_set["queries"]}

        self.assertTrue({"source", "summary", "distractor", "multi_topic_long_document"} <= roles)
        self.assertTrue(
            {
                "paraphrase",
                "summary",
                "cross_language_paraphrase",
                "late_passage",
                "boundary_overlap",
            }
            <= query_kinds
        )
        long_documents = [
            document
            for document in fixture_set["documents"]
            if document["fixture_role"] == "multi_topic_long_document"
        ]
        self.assertEqual({document["language"] for document in long_documents}, {"en", "pl"})
        self.assertTrue(
            all(
                4096 <= len(document["content"].encode("utf-8")) <= 16 * 1024
                for document in long_documents
            )
        )
        late_queries = [
            query for query in fixture_set["queries"] if query["kind"] == "late_passage"
        ]
        boundary_queries = [
            query for query in fixture_set["queries"] if query["kind"] == "boundary_overlap"
        ]
        self.assertEqual({query["language"] for query in late_queries}, {"en", "pl"})
        self.assertEqual({query["language"] for query in boundary_queries}, {"en", "pl"})
        self.assertTrue(
            all(
                query["passage_expectation"]["minimum_utf8_offset"] >= 4096
                for query in late_queries
            )
        )
        self.assertTrue(
            all(
                query["passage_expectation"]["requires_boundary_evidence"] is True
                for query in boundary_queries
            )
        )

    def test_identical_rankings_produce_identical_scores(self) -> None:
        fixture_set = load_fixture_set(FIXTURE_PATH)
        rankings = {
            query["id"]: query["relevant_document_ids"] + query["non_relevant_document_ids"]
            for query in fixture_set["queries"]
        }

        first_score = score_rankings(fixture_set, rankings, cutoff=3)
        second_score = score_rankings(fixture_set, rankings, cutoff=3)

        self.assertEqual(first_score, second_score)
        self.assertEqual(first_score["macro_recall_at_k"], 1.0)
        self.assertEqual(first_score["macro_precision_at_k"], 0.589744)
        self.assertEqual(first_score["mean_reciprocal_rank"], 1.0)
        self.assertEqual(first_score["mean_non_relevant_hits_at_k"], 1.230769)
        self.assertEqual(first_score["query_count"], 13)

    def test_scorer_rejects_unjudged_output(self) -> None:
        fixture_set = load_fixture_set(FIXTURE_PATH)
        rankings = {
            query["id"]: query["relevant_document_ids"] + query["non_relevant_document_ids"]
            for query in fixture_set["queries"]
        }
        rankings[fixture_set["queries"][0]["id"]][0] = "doc-not-in-fixture"

        with self.assertRaisesRegex(ValueError, "unknown document"):
            score_rankings(fixture_set, rankings, cutoff=3)


if __name__ == "__main__":
    unittest.main()
