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
        self.assertTrue({"paraphrase", "summary", "cross_language_paraphrase"} <= query_kinds)
        long_documents = [
            document
            for document in fixture_set["documents"]
            if document["fixture_role"] == "multi_topic_long_document"
        ]
        self.assertEqual({document["language"] for document in long_documents}, {"en", "pl"})
        self.assertTrue(all(len(document["content"]) >= 500 for document in long_documents))

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
        self.assertEqual(first_score["macro_precision_at_k"], 0.703704)
        self.assertEqual(first_score["mean_reciprocal_rank"], 1.0)
        self.assertEqual(first_score["mean_non_relevant_hits_at_k"], 0.888889)
        self.assertEqual(first_score["query_count"], 9)

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
