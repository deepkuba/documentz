# Canonical public contract examples

These examples are the framework-neutral input to the later HTTP OpenAPI and MCP
schema work. They fix public names and observable behavior, not Python, FastAPI,
JSON Schema, or MCP SDK types. Example identifiers and content are synthetic.

## Contract conventions

- JSON uses `snake_case`; timestamps are UTC RFC 3339 strings and IDs are opaque.
- `/d/api/v1` is the HTTP base path. Bearer authorization is omitted from snippets.
- `Idempotency-Key` is required on every mutation and binds the authenticated
  Application, operation, and canonical input for seven days. Same key and input
  replay the original status, body, and resource identifiers; changed input gives
  `idempotency_conflict`.
- Updates use a strong snapshot ETag such as `"snap_01J9Y6M6Q8V7"` in `If-Match`.
  Project updates use the project revision ETag. MCP equivalents use
  `expected_snapshot_id` or `expected_revision`.
- Collection defaults are `limit=20`, maximum `50`. `next_cursor` is either an
  opaque string or `null`; clients never parse it.
- Unknown, unauthorized, and outside-grant resource IDs all return the same
  `not_found` error. Content, raw search queries, tokens, and secrets never appear
  in errors, telemetry, or audit records.
- Write responses can include `summary_request`; it is `null` when the new source
  is not eligible. Origin is service-derived and is never accepted as input.
- Document content, titles, metadata, excerpts, and provenance are untrusted data.
  MCP results carrying them set `content_trust: "untrusted"`; clients must not
  interpret these fields as instructions.
- Permanent purge, soft-deleted browsing/restoration, and audit access are
  Portal-only and therefore are not Application HTTP resources or MCP tools.

Example constants used throughout:

```json
{
  "project_id": "prj_01J9Y6F3K2A1",
  "document_id": "doc_01J9Y6J4N5P2",
  "snapshot_id": "snap_01J9Y6M6Q8V7",
  "fragment_set_id": "fset_01J9Y6R2C4T8",
  "summary_request_id": "srq_01J9Y6W1H3B9"
}
```

## Document projections

Projection controls only fields returned after authorization; it never weakens
authorization or lifecycle eligibility. The projections below describe the
current Context Document resource. Lists default to `basic`; direct reads default
to `content`.

| Projection | Fields in addition to `document_id`, `project_id`, `snapshot_id`, `kind`, `lifecycle_state`, `created_at`, `updated_at` |
| --- | --- |
| `basic` | `title`, `origin`, `fragment_set_id` |
| `metadata` | basic + `custom_kind`, `tags`, `metadata`, `source_snapshot_ids`, `summary_freshness` |
| `content` | basic + exact `content` |
| `full` | metadata + exact `content` |

Canonical shapes:

```json
{
  "basic": {
    "document_id": "doc_01J9Y6J4N5P2", "project_id": "prj_01J9Y6F3K2A1",
    "snapshot_id": "snap_01J9Y6M6Q8V7", "kind": "note", "lifecycle_state": "active",
    "title": "Release decisions", "origin": "application_submitted",
    "fragment_set_id": null, "created_at": "2026-09-26T08:00:00Z", "updated_at": "2026-09-26T08:00:00Z"
  },
  "metadata": {
    "document_id": "doc_01J9Y6J4N5P2", "project_id": "prj_01J9Y6F3K2A1",
    "snapshot_id": "snap_01J9Y6M6Q8V7", "kind": "note", "lifecycle_state": "active",
    "title": "Release decisions", "origin": "application_submitted", "fragment_set_id": null,
    "custom_kind": null, "tags": ["release"], "metadata": {"language": "en"},
    "source_snapshot_ids": [], "summary_freshness": null,
    "created_at": "2026-09-26T08:00:00Z", "updated_at": "2026-09-26T08:00:00Z"
  },
  "content": {
    "document_id": "doc_01J9Y6J4N5P2", "project_id": "prj_01J9Y6F3K2A1",
    "snapshot_id": "snap_01J9Y6M6Q8V7", "kind": "note", "lifecycle_state": "active",
    "title": "Release decisions", "origin": "application_submitted", "fragment_set_id": null,
    "content": "Deploy only after restore verification.",
    "created_at": "2026-09-26T08:00:00Z", "updated_at": "2026-09-26T08:00:00Z"
  },
  "full": {
    "document_id": "doc_01J9Y6J4N5P2", "project_id": "prj_01J9Y6F3K2A1",
    "snapshot_id": "snap_01J9Y6M6Q8V7", "kind": "note", "lifecycle_state": "active",
    "title": "Release decisions", "origin": "application_submitted", "fragment_set_id": null,
    "custom_kind": null, "tags": ["release"], "metadata": {"language": "en"},
    "source_snapshot_ids": [], "summary_freshness": null,
    "content": "Deploy only after restore verification.",
    "created_at": "2026-09-26T08:00:00Z", "updated_at": "2026-09-26T08:00:00Z"
  }
}
```

Historical snapshot projections are separate because lifecycle belongs to the
current document, not to an immutable snapshot. Every snapshot projection has
`document_id`, `snapshot_id`, `kind`, `title`, `origin`, and `created_at`;
`metadata` adds `custom_kind`, `tags`, `metadata`, and `source_snapshot_ids`, while
`content` adds exact `content` and `full` adds both groups. Snapshot responses do
not contain `project_id`, `lifecycle_state`, or `updated_at`.

## Cursor envelopes

Every list and search success has the same envelope. A cursor is bound to the
authenticated grant, operation, normalized filters, ordering, page size, and—for
search—the active index version. Reuse with different inputs gives
`cursor_invalid`; an incompatible index change gives `cursor_expired`.

```json
{
  "items": [{"project_id": "prj_01J9Y6F3K2A1", "name": "Documentz"}],
  "page": {"next_cursor": "cur_AQIDBAUGBwg", "limit": 20}
}
```

The terminal page is identical except for `"next_cursor": null`. Position-range
fragment retrieval uses `start_position` and `limit` but returns this envelope.

## Stable errors

HTTP errors use the status shown below. MCP tool failures return the same `error`
object as structured tool output and set the outer MCP `CallToolResult.isError`
transport field to `true`; the transport envelope is omitted from the examples.
Protocol authentication failures happen at the HTTP transport boundary.

```json
{
  "error": {
    "code": "conflict",
    "message": "The resource changed since the supplied version.",
    "request_id": "req_01J9Y70V6D4K",
    "details": {"expected_snapshot_id": "snap_01J9Y6M6Q8V7"}
  }
}
```

| HTTP | Code | Stable meaning |
| --- | --- | --- |
| 400 | `invalid_request` | Malformed or semantically invalid input |
| 400 | `cursor_invalid` | Cursor cannot be used with this request/grant |
| 409 | `cursor_expired` | Search cursor refers to an incompatible index |
| 404 | `not_found` | Missing or unauthorized resource; intentionally indistinguishable |
| 409 | `conflict` | Expected revision, snapshot, or lifecycle state is stale |
| 409 | `idempotency_conflict` | Key was already bound to different canonical input |
| 409 | `summary_source_invalid` | A summary source violates source rules |
| 409 | `fragment_set_incomplete` | Publication lacks a declared position |
| 413 | `content_too_large` | UTF-8 content or Fragment Set exceeds its byte limit |
| 429 | `rate_limited` | Application operation limit exceeded |

Validation `details` contain only safe field names/reasons, never rejected values.

## HTTP examples

All HTTP snippets include a request, success, and representative error. Other
stable errors from the table remain applicable.

### Projects

<!-- example:http:list-projects:request -->
`GET /d/api/v1/projects?limit=20&cursor=cur_AQIDBAUGBwg`

<!-- example:http:list-projects:success -->
```json
{"items":[{"project_id":"prj_01J9Y6F3K2A1","name":"Documentz","description":"Service delivery context","archived":false,"revision":3}],"page":{"next_cursor":null,"limit":20}}
```

<!-- example:http:list-projects:error -->
```json
{"error":{"code":"cursor_invalid","message":"The cursor cannot be used for this request.","request_id":"req_01J9Y70V6D4K","details":{}}}
```

<!-- example:http:create-project:request -->
`POST /d/api/v1/projects` with `Idempotency-Key: idem-project-001`
```json
{"name":"Documentz","description":"Service delivery context"}
```

<!-- example:http:create-project:success -->
`201 Created`, `Location: /d/api/v1/projects/prj_01J9Y6F3K2A1`, `ETag: "project-revision-1"`
```json
{"project_id":"prj_01J9Y6F3K2A1","name":"Documentz","description":"Service delivery context","archived":false,"revision":1}
```

<!-- example:http:create-project:error -->
```json
{"error":{"code":"invalid_request","message":"The request is invalid.","request_id":"req_01J9Y70V6D4K","details":{"fields":{"name":"must be unique"}}}}
```

<!-- example:http:get-project:request -->
`GET /d/api/v1/projects/prj_01J9Y6F3K2A1`

<!-- example:http:get-project:success -->
```json
{"project_id":"prj_01J9Y6F3K2A1","name":"Documentz","description":"Service delivery context","archived":false,"revision":3}
```

<!-- example:http:get-project:error -->
```json
{"error":{"code":"not_found","message":"The requested resource was not found.","request_id":"req_01J9Y70V6D4K","details":{}}}
```

<!-- example:http:update-project:request -->
`PATCH /d/api/v1/projects/prj_01J9Y6F3K2A1` with `If-Match: "project-revision-3"` and `Idempotency-Key: idem-project-002`
```json
{"name":"Documentz PoC","description":"Production PoC context"}
```

<!-- example:http:update-project:success -->
`200 OK`, `ETag: "project-revision-4"`
```json
{"project_id":"prj_01J9Y6F3K2A1","name":"Documentz PoC","description":"Production PoC context","archived":false,"revision":4}
```

<!-- example:http:update-project:error -->
```json
{"error":{"code":"conflict","message":"The resource changed since the supplied version.","request_id":"req_01J9Y70V6D4K","details":{"expected_revision":3}}}
```

<!-- example:http:archive-project:request -->
`POST /d/api/v1/projects/prj_01J9Y6F3K2A1/archive` with `If-Match: "project-revision-4"` and `Idempotency-Key: idem-project-003`
```json
{}
```

<!-- example:http:archive-project:success -->
```json
{"project_id":"prj_01J9Y6F3K2A1","name":"Documentz PoC","description":"Production PoC context","archived":true,"revision":5}
```

<!-- example:http:archive-project:error -->
```json
{"error":{"code":"conflict","message":"The resource changed since the supplied version.","request_id":"req_01J9Y70V6D4K","details":{"expected_revision":4}}}
```

### Context Documents and snapshots

<!-- example:http:list-contexts:request -->
`GET /d/api/v1/projects/prj_01J9Y6F3K2A1/contexts?projection=metadata&lifecycle_state=active&kind=note&tag=release&limit=20`

<!-- example:http:list-contexts:success -->
```json
{"items":[{"document_id":"doc_01J9Y6J4N5P2","project_id":"prj_01J9Y6F3K2A1","snapshot_id":"snap_01J9Y6M6Q8V7","kind":"note","lifecycle_state":"active","title":"Release decisions","origin":"application_submitted","fragment_set_id":null,"custom_kind":null,"tags":["release"],"metadata":{"language":"en"},"source_snapshot_ids":[],"summary_freshness":null,"created_at":"2026-09-26T08:00:00Z","updated_at":"2026-09-26T08:00:00Z"}],"page":{"next_cursor":null,"limit":20}}
```

<!-- example:http:list-contexts:error -->
```json
{"error":{"code":"invalid_request","message":"The request is invalid.","request_id":"req_01J9Y70V6D4K","details":{"fields":{"lifecycle_state":"Applications may list active or rejected documents"}}}}
```

<!-- example:http:store-context:request -->
`POST /d/api/v1/projects/prj_01J9Y6F3K2A1/contexts` with `Idempotency-Key: idem-context-001`
```json
{"kind":"note","custom_kind":null,"title":"Release decisions","content":"Deploy only after restore verification.","tags":["release"],"metadata":{"language":"en"},"source_snapshot_ids":[]}
```

<!-- example:http:store-context:success -->
`201 Created`, `ETag: "snap_01J9Y6M6Q8V7"`
```json
{"context":{"document_id":"doc_01J9Y6J4N5P2","project_id":"prj_01J9Y6F3K2A1","snapshot_id":"snap_01J9Y6M6Q8V7","kind":"note","lifecycle_state":"active","title":"Release decisions","origin":"application_submitted","fragment_set_id":null,"content":"Deploy only after restore verification.","created_at":"2026-09-26T08:00:00Z","updated_at":"2026-09-26T08:00:00Z"},"summary_request":null}
```

<!-- example:http:store-context:error -->
```json
{"error":{"code":"content_too_large","message":"Content exceeds the allowed UTF-8 byte size.","request_id":"req_01J9Y70V6D4K","details":{"maximum_bytes":16384}}}
```

<!-- example:http:get-context:request -->
`GET /d/api/v1/projects/prj_01J9Y6F3K2A1/contexts/doc_01J9Y6J4N5P2?projection=full`

<!-- example:http:get-context:success -->
`200 OK`, `ETag: "snap_01J9Y6M6Q8V7"`
```json
{"document_id":"doc_01J9Y6J4N5P2","project_id":"prj_01J9Y6F3K2A1","snapshot_id":"snap_01J9Y6M6Q8V7","kind":"note","lifecycle_state":"active","title":"Release decisions","origin":"application_submitted","fragment_set_id":null,"custom_kind":null,"tags":["release"],"metadata":{"language":"en"},"source_snapshot_ids":[],"summary_freshness":null,"content":"Deploy only after restore verification.","created_at":"2026-09-26T08:00:00Z","updated_at":"2026-09-26T08:00:00Z"}
```

<!-- example:http:get-context:error -->
```json
{"error":{"code":"not_found","message":"The requested resource was not found.","request_id":"req_01J9Y70V6D4K","details":{}}}
```

<!-- example:http:update-context:request -->
`PATCH /d/api/v1/projects/prj_01J9Y6F3K2A1/contexts/doc_01J9Y6J4N5P2` with `If-Match: "snap_01J9Y6M6Q8V7"` and `Idempotency-Key: idem-context-002`
```json
{"title":"Release and restore decisions","content":"Deploy only after a successful isolated restore.","tags":["release","recovery"],"metadata":{"language":"en"}}
```

<!-- example:http:update-context:success -->
`200 OK`, `ETag: "snap_01J9Y78AC2M4"`
```json
{"context":{"document_id":"doc_01J9Y6J4N5P2","project_id":"prj_01J9Y6F3K2A1","snapshot_id":"snap_01J9Y78AC2M4","kind":"note","lifecycle_state":"active","title":"Release and restore decisions","origin":"application_submitted","fragment_set_id":null,"content":"Deploy only after a successful isolated restore.","created_at":"2026-09-26T08:00:00Z","updated_at":"2026-09-26T09:00:00Z"},"summary_request":null}
```

<!-- example:http:update-context:error -->
```json
{"error":{"code":"conflict","message":"The resource changed since the supplied version.","request_id":"req_01J9Y70V6D4K","details":{"expected_snapshot_id":"snap_01J9Y6M6Q8V7"}}}
```

<!-- example:http:list-document-snapshots:request -->
`GET /d/api/v1/projects/prj_01J9Y6F3K2A1/contexts/doc_01J9Y6J4N5P2/snapshots?projection=metadata&limit=20`

<!-- example:http:list-document-snapshots:success -->
```json
{"items":[{"document_id":"doc_01J9Y6J4N5P2","snapshot_id":"snap_01J9Y78AC2M4","kind":"note","title":"Release and restore decisions","origin":"application_submitted","custom_kind":null,"tags":["release","recovery"],"metadata":{"language":"en"},"source_snapshot_ids":[],"created_at":"2026-09-26T09:00:00Z"}],"page":{"next_cursor":"cur_snapshots_2","limit":20}}
```

<!-- example:http:list-document-snapshots:error -->
```json
{"error":{"code":"not_found","message":"The requested resource was not found.","request_id":"req_01J9Y70V6D4K","details":{}}}
```

<!-- example:http:get-document-snapshot:request -->
`GET /d/api/v1/projects/prj_01J9Y6F3K2A1/contexts/doc_01J9Y6J4N5P2/snapshots/snap_01J9Y6M6Q8V7?projection=full`

<!-- example:http:get-document-snapshot:success -->
```json
{"document_id":"doc_01J9Y6J4N5P2","snapshot_id":"snap_01J9Y6M6Q8V7","kind":"note","title":"Release decisions","origin":"application_submitted","custom_kind":null,"tags":["release"],"metadata":{"language":"en"},"source_snapshot_ids":[],"content":"Deploy only after restore verification.","created_at":"2026-09-26T08:00:00Z"}
```

<!-- example:http:get-document-snapshot:error -->
```json
{"error":{"code":"not_found","message":"The requested resource was not found.","request_id":"req_01J9Y70V6D4K","details":{}}}
```

<!-- example:http:change-context-lifecycle:request -->
`POST /d/api/v1/projects/prj_01J9Y6F3K2A1/contexts/doc_01J9Y6J4N5P2/lifecycle` with `Idempotency-Key: idem-life-001`
```json
{"transition":"reject","expected_state":"active"}
```

<!-- example:http:change-context-lifecycle:success -->
```json
{"document_id":"doc_01J9Y6J4N5P2","lifecycle_state":"rejected","updated_at":"2026-09-26T10:00:00Z"}
```

<!-- example:http:change-context-lifecycle:error -->
```json
{"error":{"code":"conflict","message":"The resource changed since the supplied state.","request_id":"req_01J9Y70V6D4K","details":{"expected_state":"active"}}}
```

Application transitions are `reject`, `reactivate`, and `soft_delete`; restoration
from `soft_deleted` and permanent purge remain Portal-only.

### Fragment Sets

<!-- example:http:create-fragment-set:request -->
`POST /d/api/v1/projects/prj_01J9Y6F3K2A1/fragment-sets` with `Idempotency-Key: idem-fset-001`
```json
{"fragment_count":2,"kind":"source_document","custom_kind":null,"title":"Architecture record","tags":["architecture"],"metadata":{"media_type":"text/markdown"}}
```

<!-- example:http:create-fragment-set:success -->
```json
{"fragment_set_id":"fset_01J9Y6R2C4T8","project_id":"prj_01J9Y6F3K2A1","state":"draft","fragment_count":2,"stored_positions":[],"expires_at":"2026-09-27T10:00:00Z"}
```

<!-- example:http:create-fragment-set:error -->
```json
{"error":{"code":"invalid_request","message":"The request is invalid.","request_id":"req_01J9Y70V6D4K","details":{"fields":{"fragment_count":"must be between 1 and 256"}}}}
```

<!-- example:http:get-fragment-set:request -->
`GET /d/api/v1/projects/prj_01J9Y6F3K2A1/fragment-sets/fset_01J9Y6R2C4T8?start_position=0&limit=20&projection=content`

<!-- example:http:get-fragment-set:success -->
```json
{"fragment_set":{"fragment_set_id":"fset_01J9Y6R2C4T8","project_id":"prj_01J9Y6F3K2A1","state":"draft","fragment_count":2,"stored_positions":[0,1],"expires_at":"2026-09-27T10:00:00Z"},"items":[{"position":0,"document_id":"doc_frag_0","snapshot_id":"snap_frag_0","content":"# Architecture\n"},{"position":1,"document_id":"doc_frag_1","snapshot_id":"snap_frag_1","content":"PostgreSQL is authoritative.\n"}],"page":{"next_cursor":null,"limit":20}}
```

<!-- example:http:get-fragment-set:error -->
```json
{"error":{"code":"not_found","message":"The requested resource was not found.","request_id":"req_01J9Y70V6D4K","details":{}}}
```

<!-- example:http:put-fragment:request -->
`PUT /d/api/v1/projects/prj_01J9Y6F3K2A1/fragment-sets/fset_01J9Y6R2C4T8/fragments/0` with `Idempotency-Key: idem-frag-000`
```json
{"content":"# Architecture\n"}
```

<!-- example:http:put-fragment:success -->
```json
{"fragment_set_id":"fset_01J9Y6R2C4T8","position":0,"document_id":"doc_frag_0","snapshot_id":"snap_frag_0","stored_positions":[0]}
```

<!-- example:http:put-fragment:error -->
```json
{"error":{"code":"content_too_large","message":"Content exceeds the allowed UTF-8 byte size.","request_id":"req_01J9Y70V6D4K","details":{"maximum_bytes":16384}}}
```

<!-- example:http:publish-fragment-set:request -->
`POST /d/api/v1/projects/prj_01J9Y6F3K2A1/fragment-sets/fset_01J9Y6R2C4T8/publish` with `Idempotency-Key: idem-fset-002`
```json
{}
```

<!-- example:http:publish-fragment-set:success -->
```json
{"fragment_set_id":"fset_01J9Y6R2C4T8","state":"published","published_at":"2026-09-26T11:00:00Z","summary_request":{"summary_request_id":"srq_01J9Y6W1H3B9","project_id":"prj_01J9Y6F3K2A1","state":"pending","source_snapshot_ids":["snap_frag_0","snap_frag_1"]}}
```

<!-- example:http:publish-fragment-set:error -->
```json
{"error":{"code":"fragment_set_incomplete","message":"The Fragment Set is incomplete.","request_id":"req_01J9Y70V6D4K","details":{"missing_positions":[1]}}}
```

<!-- example:http:abandon-fragment-set:request -->
`POST /d/api/v1/projects/prj_01J9Y6F3K2A1/fragment-sets/fset_01J9Y6R2C4T8/abandon` with `Idempotency-Key: idem-fset-003`
```json
{}
```

<!-- example:http:abandon-fragment-set:success -->
`204 No Content`

<!-- example:http:abandon-fragment-set:error -->
```json
{"error":{"code":"conflict","message":"A published Fragment Set cannot be abandoned.","request_id":"req_01J9Y70V6D4K","details":{}}}
```

### Summary Requests and search

<!-- example:http:list-summary-requests:request -->
`GET /d/api/v1/projects/prj_01J9Y6F3K2A1/summary-requests?state=pending&limit=20`

<!-- example:http:list-summary-requests:success -->
```json
{"items":[{"summary_request_id":"srq_01J9Y6W1H3B9","project_id":"prj_01J9Y6F3K2A1","state":"pending","source_snapshot_ids":["snap_frag_0","snap_frag_1"],"created_at":"2026-09-26T11:00:00Z"}],"page":{"next_cursor":null,"limit":20}}
```

<!-- example:http:list-summary-requests:error -->
```json
{"error":{"code":"cursor_invalid","message":"The cursor cannot be used for this request.","request_id":"req_01J9Y70V6D4K","details":{}}}
```

A request is completed by `store-context` with `kind: "derived_summary"`, the
request's exact `source_snapshot_ids`, and optional `summary_request_id`.

Canonical completion request (the normal `store-context` success/error shapes
apply, and eligible Derived Summaries never create another Summary Request):

```json
{"kind":"derived_summary","custom_kind":null,"title":"Architecture summary","content":"The relational database is authoritative; indexes are rebuildable.","tags":["architecture"],"metadata":{"purpose":"session_recall"},"source_snapshot_ids":["snap_frag_0","snap_frag_1"],"summary_request_id":"srq_01J9Y6W1H3B9"}
```

<!-- example:http:decline-summary-request:request -->
`POST /d/api/v1/projects/prj_01J9Y6F3K2A1/summary-requests/srq_01J9Y6W1H3B9/decline` with `Idempotency-Key: idem-summary-001`
```json
{}
```

<!-- example:http:decline-summary-request:success -->
```json
{"summary_request_id":"srq_01J9Y6W1H3B9","project_id":"prj_01J9Y6F3K2A1","state":"declined","source_snapshot_ids":["snap_frag_0","snap_frag_1"],"updated_at":"2026-09-26T12:00:00Z"}
```

<!-- example:http:decline-summary-request:error -->
```json
{"error":{"code":"conflict","message":"The Summary Request is no longer pending.","request_id":"req_01J9Y70V6D4K","details":{}}}
```

<!-- example:http:search-context:request -->
`POST /d/api/v1/context-search`
```json
{"query":"how do we verify recovery","mode":"hybrid","project_ids":["prj_01J9Y6F3K2A1"],"kinds":["note","source_document","derived_summary"],"tags_any":["release","recovery"],"tags_all":[],"origins":["application_submitted","imported"],"created_from":null,"created_to":null,"prefer_summaries":true,"limit":20,"cursor":null}
```

<!-- example:http:search-context:success -->
```json
{"items":[{"result_id":"doc_01J9Y6J4N5P2","result_type":"document","project_id":"prj_01J9Y6F3K2A1","document_id":"doc_01J9Y6J4N5P2","fragment_set_id":null,"snapshot_id":"snap_01J9Y78AC2M4","kind":"note","title":"Release and restore decisions","origin":"application_submitted","tags":["release","recovery"],"excerpt":"Deploy only after a successful isolated restore.","source_snapshot_ids":[],"score":0.82}],"page":{"next_cursor":null,"limit":20},"mode":"hybrid","degraded":false,"partial":false}
```

<!-- example:http:search-context:error -->
```json
{"error":{"code":"cursor_expired","message":"The search cursor has expired.","request_id":"req_01J9Y70V6D4K","details":{}}}
```

Search results never contain full content. `score` is optional and comparable only
within one response. Hybrid embedding failure returns lexical items with
`degraded: true`; incomplete semantic candidates set `partial: true`.

## MCP examples

MCP inputs omit transport envelopes. Successful outputs are structured content.
Write results preserve the same idempotency behavior as HTTP.

### Project tools

<!-- example:mcp:list_projects:request -->
```json
{"limit":20,"cursor":null}
```
<!-- example:mcp:list_projects:success -->
```json
{"items":[{"project_id":"prj_01J9Y6F3K2A1","name":"Documentz","description":"Service delivery context","archived":false,"revision":3}],"page":{"next_cursor":null,"limit":20}}
```
<!-- example:mcp:list_projects:error -->
```json
{"error":{"code":"cursor_invalid","message":"The cursor cannot be used for this request.","request_id":"req_01J9Y70V6D4K","details":{}}}
```

<!-- example:mcp:create_project:request -->
```json
{"name":"Documentz","description":"Service delivery context","idempotency_key":"idem-project-001"}
```
<!-- example:mcp:create_project:success -->
```json
{"project_id":"prj_01J9Y6F3K2A1","name":"Documentz","description":"Service delivery context","archived":false,"revision":1}
```
<!-- example:mcp:create_project:error -->
```json
{"error":{"code":"invalid_request","message":"The request is invalid.","request_id":"req_01J9Y70V6D4K","details":{"fields":{"name":"must be unique"}}}}
```

<!-- example:mcp:update_project:request -->
```json
{"project_id":"prj_01J9Y6F3K2A1","name":"Documentz PoC","description":"Production PoC context","expected_revision":3,"idempotency_key":"idem-project-002"}
```
<!-- example:mcp:update_project:success -->
```json
{"project_id":"prj_01J9Y6F3K2A1","name":"Documentz PoC","description":"Production PoC context","archived":false,"revision":4}
```
<!-- example:mcp:update_project:error -->
```json
{"error":{"code":"conflict","message":"The resource changed since the supplied version.","request_id":"req_01J9Y70V6D4K","details":{"expected_revision":3}}}
```

### Context and snapshot tools

<!-- example:mcp:list_contexts:request -->
```json
{"project_id":"prj_01J9Y6F3K2A1","projection":"metadata","lifecycle_state":"active","kinds":["note"],"tags":["release"],"limit":20,"cursor":null}
```
<!-- example:mcp:list_contexts:success -->
```json
{"items":[{"document_id":"doc_01J9Y6J4N5P2","project_id":"prj_01J9Y6F3K2A1","snapshot_id":"snap_01J9Y6M6Q8V7","kind":"note","lifecycle_state":"active","title":"Release decisions","origin":"application_submitted","fragment_set_id":null,"custom_kind":null,"tags":["release"],"metadata":{"language":"en"},"source_snapshot_ids":[],"summary_freshness":null,"created_at":"2026-09-26T08:00:00Z","updated_at":"2026-09-26T08:00:00Z"}],"page":{"next_cursor":null,"limit":20},"content_trust":"untrusted"}
```
<!-- example:mcp:list_contexts:error -->
```json
{"error":{"code":"not_found","message":"The requested resource was not found.","request_id":"req_01J9Y70V6D4K","details":{}}}
```

<!-- example:mcp:store_context:request -->
```json
{"project_id":"prj_01J9Y6F3K2A1","kind":"note","custom_kind":null,"title":"Release decisions","content":"Deploy only after restore verification.","tags":["release"],"metadata":{"language":"en"},"source_snapshot_ids":[],"summary_request_id":null,"idempotency_key":"idem-context-001"}
```
<!-- example:mcp:store_context:success -->
```json
{"context":{"document_id":"doc_01J9Y6J4N5P2","project_id":"prj_01J9Y6F3K2A1","snapshot_id":"snap_01J9Y6M6Q8V7","kind":"note","lifecycle_state":"active","title":"Release decisions","origin":"application_submitted","fragment_set_id":null,"content":"Deploy only after restore verification.","created_at":"2026-09-26T08:00:00Z","updated_at":"2026-09-26T08:00:00Z"},"summary_request":null,"content_trust":"untrusted"}
```
<!-- example:mcp:store_context:error -->
```json
{"error":{"code":"content_too_large","message":"Content exceeds the allowed UTF-8 byte size.","request_id":"req_01J9Y70V6D4K","details":{"maximum_bytes":16384}}}
```

<!-- example:mcp:get_context:request -->
```json
{"project_id":"prj_01J9Y6F3K2A1","document_id":"doc_01J9Y6J4N5P2","projection":"full"}
```
<!-- example:mcp:get_context:success -->
```json
{"context":{"document_id":"doc_01J9Y6J4N5P2","project_id":"prj_01J9Y6F3K2A1","snapshot_id":"snap_01J9Y6M6Q8V7","kind":"note","lifecycle_state":"active","title":"Release decisions","origin":"application_submitted","fragment_set_id":null,"custom_kind":null,"tags":["release"],"metadata":{"language":"en"},"source_snapshot_ids":[],"summary_freshness":null,"content":"Deploy only after restore verification.","created_at":"2026-09-26T08:00:00Z","updated_at":"2026-09-26T08:00:00Z"},"content_trust":"untrusted"}
```
<!-- example:mcp:get_context:error -->
```json
{"error":{"code":"not_found","message":"The requested resource was not found.","request_id":"req_01J9Y70V6D4K","details":{}}}
```

<!-- example:mcp:update_context:request -->
```json
{"project_id":"prj_01J9Y6F3K2A1","document_id":"doc_01J9Y6J4N5P2","title":"Release and restore decisions","content":"Deploy only after a successful isolated restore.","tags":["release","recovery"],"metadata":{"language":"en"},"expected_snapshot_id":"snap_01J9Y6M6Q8V7","idempotency_key":"idem-context-002"}
```
<!-- example:mcp:update_context:success -->
```json
{"context":{"document_id":"doc_01J9Y6J4N5P2","project_id":"prj_01J9Y6F3K2A1","snapshot_id":"snap_01J9Y78AC2M4","kind":"note","lifecycle_state":"active","title":"Release and restore decisions","origin":"application_submitted","fragment_set_id":null,"content":"Deploy only after a successful isolated restore.","created_at":"2026-09-26T08:00:00Z","updated_at":"2026-09-26T09:00:00Z"},"summary_request":null,"content_trust":"untrusted"}
```
<!-- example:mcp:update_context:error -->
```json
{"error":{"code":"conflict","message":"The resource changed since the supplied version.","request_id":"req_01J9Y70V6D4K","details":{"expected_snapshot_id":"snap_01J9Y6M6Q8V7"}}}
```

<!-- example:mcp:change_context_lifecycle:request -->
```json
{"project_id":"prj_01J9Y6F3K2A1","document_id":"doc_01J9Y6J4N5P2","transition":"reject","expected_state":"active","idempotency_key":"idem-life-001"}
```
<!-- example:mcp:change_context_lifecycle:success -->
```json
{"document_id":"doc_01J9Y6J4N5P2","lifecycle_state":"rejected","updated_at":"2026-09-26T10:00:00Z"}
```
<!-- example:mcp:change_context_lifecycle:error -->
```json
{"error":{"code":"conflict","message":"The resource changed since the supplied state.","request_id":"req_01J9Y70V6D4K","details":{"expected_state":"active"}}}
```

<!-- example:mcp:list_document_snapshots:request -->
```json
{"project_id":"prj_01J9Y6F3K2A1","document_id":"doc_01J9Y6J4N5P2","projection":"metadata","limit":20,"cursor":null}
```
<!-- example:mcp:list_document_snapshots:success -->
```json
{"items":[{"document_id":"doc_01J9Y6J4N5P2","snapshot_id":"snap_01J9Y78AC2M4","kind":"note","title":"Release and restore decisions","origin":"application_submitted","custom_kind":null,"tags":["release","recovery"],"metadata":{"language":"en"},"source_snapshot_ids":[],"created_at":"2026-09-26T09:00:00Z"}],"page":{"next_cursor":"cur_snapshots_2","limit":20},"content_trust":"untrusted"}
```
<!-- example:mcp:list_document_snapshots:error -->
```json
{"error":{"code":"not_found","message":"The requested resource was not found.","request_id":"req_01J9Y70V6D4K","details":{}}}
```

<!-- example:mcp:get_document_snapshot:request -->
```json
{"project_id":"prj_01J9Y6F3K2A1","document_id":"doc_01J9Y6J4N5P2","snapshot_id":"snap_01J9Y6M6Q8V7","projection":"full"}
```
<!-- example:mcp:get_document_snapshot:success -->
```json
{"snapshot":{"document_id":"doc_01J9Y6J4N5P2","snapshot_id":"snap_01J9Y6M6Q8V7","kind":"note","title":"Release decisions","origin":"application_submitted","custom_kind":null,"tags":["release"],"metadata":{"language":"en"},"source_snapshot_ids":[],"content":"Deploy only after restore verification.","created_at":"2026-09-26T08:00:00Z"},"content_trust":"untrusted"}
```
<!-- example:mcp:get_document_snapshot:error -->
```json
{"error":{"code":"not_found","message":"The requested resource was not found.","request_id":"req_01J9Y70V6D4K","details":{}}}
```

### Fragment Set tools

`create_fragment_set` accepts initial fragments so MCP can create or resume a
draft without a separate fragment-write tool. A retry may add positions that were
not stored; changing an existing position's content is an idempotency conflict.

<!-- example:mcp:create_fragment_set:request -->
```json
{"project_id":"prj_01J9Y6F3K2A1","fragment_set_id":null,"fragment_count":2,"kind":"source_document","custom_kind":null,"title":"Architecture record","tags":["architecture"],"metadata":{"media_type":"text/markdown"},"fragments":[{"position":0,"content":"# Architecture\n"},{"position":1,"content":"PostgreSQL is authoritative.\n"}],"idempotency_key":"idem-fset-001"}
```
<!-- example:mcp:create_fragment_set:success -->
```json
{"fragment_set_id":"fset_01J9Y6R2C4T8","project_id":"prj_01J9Y6F3K2A1","state":"draft","fragment_count":2,"stored_positions":[0,1],"expires_at":"2026-09-27T10:00:00Z"}
```
<!-- example:mcp:create_fragment_set:error -->
```json
{"error":{"code":"invalid_request","message":"The request is invalid.","request_id":"req_01J9Y70V6D4K","details":{"fields":{"fragments.position":"must be unique and in range"}}}}
```

<!-- example:mcp:get_fragment_set:request -->
```json
{"project_id":"prj_01J9Y6F3K2A1","fragment_set_id":"fset_01J9Y6R2C4T8","start_position":0,"limit":20,"cursor":null,"projection":"content"}
```
<!-- example:mcp:get_fragment_set:success -->
```json
{"fragment_set":{"fragment_set_id":"fset_01J9Y6R2C4T8","project_id":"prj_01J9Y6F3K2A1","state":"draft","fragment_count":2,"stored_positions":[0,1],"expires_at":"2026-09-27T10:00:00Z"},"items":[{"position":0,"document_id":"doc_frag_0","snapshot_id":"snap_frag_0","content":"# Architecture\n"},{"position":1,"document_id":"doc_frag_1","snapshot_id":"snap_frag_1","content":"PostgreSQL is authoritative.\n"}],"page":{"next_cursor":null,"limit":20},"content_trust":"untrusted"}
```
<!-- example:mcp:get_fragment_set:error -->
```json
{"error":{"code":"not_found","message":"The requested resource was not found.","request_id":"req_01J9Y70V6D4K","details":{}}}
```

<!-- example:mcp:publish_fragment_set:request -->
```json
{"project_id":"prj_01J9Y6F3K2A1","fragment_set_id":"fset_01J9Y6R2C4T8","idempotency_key":"idem-fset-002"}
```
<!-- example:mcp:publish_fragment_set:success -->
```json
{"fragment_set_id":"fset_01J9Y6R2C4T8","state":"published","published_at":"2026-09-26T11:00:00Z","summary_request":{"summary_request_id":"srq_01J9Y6W1H3B9","project_id":"prj_01J9Y6F3K2A1","state":"pending","source_snapshot_ids":["snap_frag_0","snap_frag_1"]}}
```
<!-- example:mcp:publish_fragment_set:error -->
```json
{"error":{"code":"fragment_set_incomplete","message":"The Fragment Set is incomplete.","request_id":"req_01J9Y70V6D4K","details":{"missing_positions":[1]}}}
```

<!-- example:mcp:abandon_fragment_set:request -->
```json
{"project_id":"prj_01J9Y6F3K2A1","fragment_set_id":"fset_01J9Y6R2C4T8","idempotency_key":"idem-fset-003"}
```
<!-- example:mcp:abandon_fragment_set:success -->
```json
{"fragment_set_id":"fset_01J9Y6R2C4T8","abandoned":true}
```
<!-- example:mcp:abandon_fragment_set:error -->
```json
{"error":{"code":"conflict","message":"A published Fragment Set cannot be abandoned.","request_id":"req_01J9Y70V6D4K","details":{}}}
```

### Summary and search tools

<!-- example:mcp:list_summary_requests:request -->
```json
{"project_id":"prj_01J9Y6F3K2A1","state":"pending","limit":20,"cursor":null}
```
<!-- example:mcp:list_summary_requests:success -->
```json
{"items":[{"summary_request_id":"srq_01J9Y6W1H3B9","project_id":"prj_01J9Y6F3K2A1","state":"pending","source_snapshot_ids":["snap_frag_0","snap_frag_1"],"created_at":"2026-09-26T11:00:00Z"}],"page":{"next_cursor":null,"limit":20}}
```
<!-- example:mcp:list_summary_requests:error -->
```json
{"error":{"code":"cursor_invalid","message":"The cursor cannot be used for this request.","request_id":"req_01J9Y70V6D4K","details":{}}}
```

<!-- example:mcp:decline_summary_request:request -->
```json
{"project_id":"prj_01J9Y6F3K2A1","summary_request_id":"srq_01J9Y6W1H3B9","idempotency_key":"idem-summary-001"}
```
<!-- example:mcp:decline_summary_request:success -->
```json
{"summary_request_id":"srq_01J9Y6W1H3B9","project_id":"prj_01J9Y6F3K2A1","state":"declined","source_snapshot_ids":["snap_frag_0","snap_frag_1"],"updated_at":"2026-09-26T12:00:00Z"}
```
<!-- example:mcp:decline_summary_request:error -->
```json
{"error":{"code":"conflict","message":"The Summary Request is no longer pending.","request_id":"req_01J9Y70V6D4K","details":{}}}
```

MCP completes that request through `store_context` with this input variant:

```json
{"project_id":"prj_01J9Y6F3K2A1","kind":"derived_summary","custom_kind":null,"title":"Architecture summary","content":"The relational database is authoritative; indexes are rebuildable.","tags":["architecture"],"metadata":{"purpose":"session_recall"},"source_snapshot_ids":["snap_frag_0","snap_frag_1"],"summary_request_id":"srq_01J9Y6W1H3B9","idempotency_key":"idem-summary-002"}
```

<!-- example:mcp:search_context:request -->
```json
{"query":"how do we verify recovery","mode":"hybrid","project_ids":["prj_01J9Y6F3K2A1"],"kinds":["note","source_document","derived_summary"],"tags_any":["release","recovery"],"tags_all":[],"origins":["application_submitted","imported"],"created_from":null,"created_to":null,"prefer_summaries":true,"limit":20,"cursor":null}
```
<!-- example:mcp:search_context:success -->
```json
{"items":[{"result_id":"doc_01J9Y6J4N5P2","result_type":"document","project_id":"prj_01J9Y6F3K2A1","document_id":"doc_01J9Y6J4N5P2","fragment_set_id":null,"snapshot_id":"snap_01J9Y78AC2M4","kind":"note","title":"Release and restore decisions","origin":"application_submitted","tags":["release","recovery"],"excerpt":"Deploy only after a successful isolated restore.","source_snapshot_ids":[],"score":0.82}],"page":{"next_cursor":null,"limit":20},"mode":"hybrid","degraded":false,"partial":false,"content_trust":"untrusted"}
```
<!-- example:mcp:search_context:error -->
```json
{"error":{"code":"cursor_expired","message":"The search cursor has expired.","request_id":"req_01J9Y70V6D4K","details":{}}}
```

## Security and trust-boundary notes

- The examples contain synthetic IDs and text only. They contain no bearer tokens,
  client secrets, authorization codes, user identifiers, raw production queries,
  hostnames, or infrastructure credentials.
- Project IDs are explicit on MCP calls and nested in HTTP paths. Services must
  authorize the project before resolving child IDs; `not_found` prevents
  cross-project enumeration.
- Projection happens after authorization and eligibility checks. Historical
  snapshot access is explicit; ordinary reads never fall back to stale snapshots.
- Search excerpts and all content-bearing MCP fields are untrusted. Adapter code
  must preserve that annotation and must not concatenate content into tool
  instructions or error messages.
- Cursor payloads are opaque and integrity protected. They bind grant and filters,
  preventing replay across Applications or projects.
- Idempotency records compare a canonical request digest and retain no raw content.
  Conflict details expose only safe identifiers and expected version/state.
- Fragment drafts are visible only to authorized writers. Incomplete drafts do not
  appear in list, retrieval, or search operations for published content.
- Derived Summary source IDs are returned only after authorization to all sources.
  Effective access is computed by the service and is not accepted from callers.
- HTTP and MCP examples intentionally share field names, result shapes, and error
  codes. Transport-only differences are headers/ETags versus explicit MCP input
  fields, MCP's `content_trust` marker, and MCP's outer `CallToolResult.isError`.
  Project archival is an HTTP owner operation; `update_project` cannot change the
  `archived` field.
