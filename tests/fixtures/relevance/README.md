# Multilingual relevance fixtures

`multilingual.json` is a synthetic, non-sensitive benchmark corpus for E00. It
contains English and Polish sources, concise summaries, close lexical
distractors, paraphrased queries, cross-language queries, and long documents
that deliberately mix several topics. Each long fixture is at least 4 KiB in
UTF-8, carries relevant evidence near both ends among unrelated passages, and
therefore forces multi-passage behavior for the candidate chunk sizes evaluated
by E01 while staying below the 16 KiB Context Document limit.
The `late_passage` cases contain unique evidence only after byte 4096 and reject
prefix-only indexing. Separate `boundary_overlap` cases contain no intact fallback
clue: their required evidence is the phrase split at the recorded UTF-8 boundary.
E01 must score that passage-level requirement independently, so retrieving the
document for another clue cannot hide zero or incorrect overlap. Document-level
ranking still checks deduplication.

Every query exhaustively partitions all document IDs into
`relevant_document_ids` and `non_relevant_document_ids`. There are no implicit
or unjudged documents, so a benchmark run cannot silently choose how to treat a
missing judgment.

## Scoring a run

Create a UTF-8 JSON object whose keys are every query ID and whose values are
document IDs in descending retrieval order:

```json
{
  "query-en-rainwater-paraphrase": [
    "doc-en-rainwater-source",
    "doc-en-rainwater-summary"
  ]
}
```

The real file must contain all thirteen query keys. A ranking may be shorter than
the corpus, but duplicate or unknown document IDs are rejected. Score it with:

```sh
python3 -m tools.relevance_fixtures \
  tests/fixtures/relevance/multilingual.json \
  path/to/rankings.json \
  --cutoff 3
```

The scorer reports per-query recall, precision, reciprocal rank, and explicit
non-relevant hits, plus deterministic macro averages rounded to six decimal
places. Query order always follows the versioned fixture file.
