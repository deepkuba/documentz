"""Validate and score the synthetic multilingual retrieval fixture set."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


REQUIRED_COVERAGE = {"english", "polish", "cross_language"}
REQUIRED_ROLES = {"source", "summary", "distractor", "multi_topic_long_document"}
REQUIRED_QUERY_KINDS = {"paraphrase", "summary", "cross_language_paraphrase"}


def load_fixture_set(path: Path) -> dict[str, Any]:
    """Load a fixture file and reject ambiguous or incomplete judgments."""

    fixture_set = json.loads(path.read_text(encoding="utf-8"))
    documents = fixture_set.get("documents", [])
    queries = fixture_set.get("queries", [])
    document_ids = _unique_ids(documents, "document")
    query_ids = _unique_ids(queries, "query")

    if fixture_set.get("fixture_version") != 1:
        raise ValueError("fixture_version must be 1")
    if fixture_set.get("data_classification") != "synthetic_non_sensitive":
        raise ValueError("fixture data must be classified as synthetic and non-sensitive")
    documents_by_id = {document["id"]: document for document in documents}
    if {document.get("language") for document in documents} != {"en", "pl"}:
        raise ValueError("documents must include only English and Polish fixtures")
    if {query.get("coverage") for query in queries} != REQUIRED_COVERAGE:
        raise ValueError("queries must cover English, Polish, and cross-language retrieval")
    if not REQUIRED_ROLES <= {document.get("fixture_role") for document in documents}:
        raise ValueError("fixture set is missing a required document role")
    if not REQUIRED_QUERY_KINDS <= {query.get("kind") for query in queries}:
        raise ValueError("fixture set is missing a required query scenario")

    for query in queries:
        relevant = _id_set(query.get("relevant_document_ids"), query["id"], "relevant")
        non_relevant = _id_set(
            query.get("non_relevant_document_ids"), query["id"], "non-relevant"
        )
        if not relevant:
            raise ValueError(f"query {query['id']} has no relevant documents")
        if relevant & non_relevant:
            raise ValueError(f"query {query['id']} has conflicting judgments")
        if relevant | non_relevant != document_ids:
            raise ValueError(f"query {query['id']} does not judge every document")
        if query.get("language") not in {"en", "pl"}:
            raise ValueError(f"query {query['id']} has an unsupported language")
        if query.get("coverage") == "cross_language":
            source_languages = {documents_by_id[document_id]["language"] for document_id in relevant}
            if query["language"] in source_languages or len(source_languages) != 1:
                raise ValueError(
                    f"cross-language query {query['id']} must target the other language"
                )

    if not query_ids:
        raise ValueError("fixture set has no queries")
    return fixture_set


def score_rankings(
    fixture_set: Mapping[str, Any],
    rankings: Mapping[str, Sequence[str]],
    *,
    cutoff: int,
) -> dict[str, Any]:
    """Score complete ranked runs with deterministic macro metrics."""

    if cutoff <= 0:
        raise ValueError("cutoff must be greater than zero")

    queries = fixture_set["queries"]
    expected_query_ids = {query["id"] for query in queries}
    if set(rankings) != expected_query_ids:
        raise ValueError("rankings must contain exactly every fixture query")

    per_query: list[dict[str, Any]] = []
    for query in queries:
        query_id = query["id"]
        ranked_ids = list(rankings[query_id])
        if len(ranked_ids) != len(set(ranked_ids)):
            raise ValueError(f"query {query_id} ranks a document more than once")

        judged_ids = set(query["relevant_document_ids"]) | set(
            query["non_relevant_document_ids"]
        )
        unknown_ids = set(ranked_ids) - judged_ids
        if unknown_ids:
            raise ValueError(
                f"query {query_id} contains unknown document(s): {sorted(unknown_ids)}"
            )

        top_ids = ranked_ids[:cutoff]
        relevant_ids = set(query["relevant_document_ids"])
        non_relevant_ids = set(query["non_relevant_document_ids"])
        relevant_hits = sum(document_id in relevant_ids for document_id in top_ids)
        first_relevant_rank = next(
            (
                rank
                for rank, document_id in enumerate(ranked_ids, start=1)
                if document_id in relevant_ids
            ),
            None,
        )
        per_query.append(
            {
                "query_id": query_id,
                "recall_at_k": relevant_hits / len(relevant_ids),
                "precision_at_k": relevant_hits / cutoff,
                "reciprocal_rank": 0.0 if first_relevant_rank is None else 1 / first_relevant_rank,
                "non_relevant_hits_at_k": sum(
                    document_id in non_relevant_ids for document_id in top_ids
                ),
            }
        )

    query_count = len(per_query)
    return {
        "cutoff": cutoff,
        "query_count": query_count,
        "macro_recall_at_k": _mean(per_query, "recall_at_k"),
        "macro_precision_at_k": _mean(per_query, "precision_at_k"),
        "mean_reciprocal_rank": _mean(per_query, "reciprocal_rank"),
        "mean_non_relevant_hits_at_k": _mean(per_query, "non_relevant_hits_at_k"),
        "per_query": per_query,
    }


def _unique_ids(records: Sequence[Mapping[str, Any]], record_name: str) -> set[str]:
    ids = [record.get("id") for record in records]
    if any(not isinstance(record_id, str) or not record_id for record_id in ids):
        raise ValueError(f"every {record_name} must have a non-empty string id")
    if len(ids) != len(set(ids)):
        raise ValueError(f"duplicate {record_name} id")
    return set(ids)


def _id_set(value: Any, query_id: str, judgment: str) -> set[str]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"query {query_id} has invalid {judgment} judgments")
    if len(value) != len(set(value)):
        raise ValueError(f"query {query_id} repeats a {judgment} judgment")
    return set(value)


def _mean(results: Sequence[Mapping[str, Any]], key: str) -> float:
    return round(sum(result[key] for result in results) / len(results), 6)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fixtures", type=Path, help="path to the relevance fixture JSON")
    parser.add_argument("rankings", type=Path, help="JSON object mapping query IDs to ranked IDs")
    parser.add_argument("--cutoff", type=int, default=5)
    args = parser.parse_args()

    fixture_set = load_fixture_set(args.fixtures)
    rankings = json.loads(args.rankings.read_text(encoding="utf-8"))
    print(json.dumps(score_rankings(fixture_set, rankings, cutoff=args.cutoff), indent=2))


if __name__ == "__main__":
    main()
