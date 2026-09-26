# Documentz

Documentz is a self-hosted personal context service for AI-assisted work. It gives multiple applications and agents one durable, user-controlled place to store project knowledge, retrieve it in later sessions, and remove it safely when it is no longer valid.

Instead of treating an entire chat transcript as memory, Documentz stores small, explicit Context Documents with provenance, immutable history, project boundaries, and predictable lifecycle rules. Applications access the same model through MCP or a versioned HTTP API, while the owner manages it through a web Portal.

> **Project status:** the product and domain design are complete enough to begin implementation. The service itself has not been implemented yet. See [CONTEXT.md](./CONTEXT.md) for the canonical domain language.

## Why Documentz?

AI clients are good at working with context but poor at carrying trustworthy context across applications and sessions. Copying whole conversations is expensive, difficult to inspect, and likely to preserve obsolete or unwanted information.

Documentz is designed around a few stronger properties:

- **User-controlled:** one owner decides which Applications can access which Personal Projects.
- **Application-neutral:** MCP, HTTP clients, and the Management Portal share one authorization and document model.
- **Versioned:** edits create immutable snapshots instead of silently replacing history.
- **Provenance-aware:** caller-provided summaries identify the exact source snapshots they describe.
- **Lifecycle-safe:** rejected, deleted, stale, and purged content cannot leak through ordinary retrieval.
- **Searchable:** lexical and semantic retrieval work together across multilingual content.
- **Context-efficient:** callers can retrieve concise summaries or selected source documents rather than entire histories.
- **Self-hosted:** the PoC runs as a portable Docker Compose deployment on a Linux server.

## Core workflow

```text
Application stores context
          │
          ▼
Documentz commits an immutable snapshot
          │
          ├── queues lexical and semantic indexing
          │
          └── optionally creates a Summary Request
                         │
                         ▼
              caller supplies a Derived Summary

Later session ── search_context ──► ranked context
                                      │
                                      ▼
                                  get_context
```

Summarization deliberately stays with the caller. Documentz tells an agent when a source would benefit from a summary, but it does not choose a model, silently rewrite content, or make model-generated text authoritative.

## Document model

Every Context Document belongs permanently to one Personal Project and has one immutable kind:

| Kind | Purpose |
| --- | --- |
| `note` | A concise piece of durable context |
| `session_summary` | A caller-authored primary record of a completed work session |
| `source_document` | Authoritative source material that may be summarized |
| `derived_summary` | A concise, traceable summary of exact source snapshots |
| `other` | An application-defined kind identified by `custom_kind` |

Ordinary documents are limited to 16 KiB of UTF-8 content. Derived Summaries are limited to 2 KiB. Larger logical bodies are represented as Fragment Sets rather than hidden storage chunks.

Edits create immutable Document Snapshots. The stable document ID points to the current snapshot, while authorized callers can explicitly inspect older snapshots. Only the current, active, eligible version participates in ordinary retrieval.

## Trustworthy summaries

A Derived Summary is useful only while its provenance remains true. Documentz therefore records the exact source snapshot IDs and enforces the following rules:

- A Derived Summary may summarize source documents, session summaries, or published fragments.
- It may not use another Derived Summary as a source.
- All sources must belong to the same Personal Project.
- Its source set cannot change after creation.
- Several purpose-specific summaries may describe the same source.
- Replacing a source snapshot immediately makes dependent summaries stale.
- Rejecting or soft-deleting any source immediately removes dependent summaries from search.
- Reactivating unchanged sources can restore summary eligibility.
- Purging any source permanently purges every summary derived from it.

Eligible sources create optional, persistent Summary Requests. Applications may complete or decline them, and a newer source snapshot supersedes an older pending request.

### Why caller-provided summaries?

The caller already has the agent, model, task context, and user intent needed to produce an appropriate summary. Keeping generation outside the service:

- avoids coupling storage to one model provider;
- keeps model costs and credentials out of the context service;
- makes the submitted text explicit and inspectable;
- permits different summaries for different purposes;
- prevents background generation from becoming an invisible source of truth.

## Fragment Sets

Fragment Sets preserve a large logical document without pretending each storage-sized part is unrelated.

- A set contains at most 256 fragments and 4 MiB in total.
- Every fragment has the same document kind and shared descriptive metadata.
- Drafts remain private to authorized writers and expire after 24 hours.
- Publication is atomic and requires every declared position.
- Membership and ordering become immutable after publication.
- Individual fragments may still receive new snapshots.
- Search returns one logical result for the set instead of flooding results with fragments.
- Lifecycle changes apply to the complete set atomically.

The Portal can split large UTF-8 text and Markdown imports at headings, paragraphs, and safe byte boundaries, show the proposed set, and publish only after confirmation.

## Lifecycle guarantees

Documents use four lifecycle states:

| State | Meaning | Ordinary retrieval |
| --- | --- | --- |
| `active` | Current usable context | Included |
| `rejected` | Known but unsuitable or incorrect | Excluded; inspectable and indefinitely reversible |
| `soft_deleted` | Intended for removal | Excluded; Portal recovery for 30 days |
| `purged` | Permanently removed | Impossible; only a non-content audit tombstone remains |

Rejection and deletion are intentionally different. Rejection records that information is wrong or unsuitable without erasing the decision. Soft deletion starts a recovery window. Purge is irreversible and cascades through dependent summaries, indexes, caches, and derived records.

Permanent purge is Portal-only. Before confirming it, the owner sees which Derived Summaries will also disappear.

## Search

Documentz provides three search modes:

- **Lexical:** deterministic full-text matching.
- **Semantic:** multilingual vector retrieval using a local embedding provider.
- **Hybrid:** combines both and is the default.

Search supports project, kind, tag, origin, and time filters. Results contain compact metadata and an excerpt; callers retrieve full content explicitly. Long documents are indexed as internal overlapping passages and deduplicated back into document-level results.

The relational database remains authoritative. Search indexes only produce candidates: every result is checked again against current authorization, publication, lifecycle, snapshot, and summary-freshness state. This prevents stale index entries from exposing rejected or deleted content.

Semantic indexing is asynchronous. If it is temporarily unavailable, hybrid search returns lexical results marked as degraded rather than blocking durable writes or silently changing behavior.

### Why PostgreSQL and pgvector?

The initial target is roughly 10,000 documents, 100 writes per day, and three connected Applications. At that scale, PostgreSQL can provide:

- authoritative relational storage;
- immutable snapshot and provenance constraints;
- full-text search;
- vector retrieval through pgvector;
- a durable background-job queue;
- transactional lifecycle propagation.

A separate search cluster would add operational cost before it solves a demonstrated problem. Embeddings and indexes remain rebuildable derived data, so the design can migrate later.

## Interfaces

### MCP

The remote MCP server uses Streamable HTTP and OAuth. Its planned tools cover:

- project listing, creation, and updates;
- document storage, listing, retrieval, and editing;
- lexical, semantic, and hybrid search;
- lifecycle changes except permanent purge;
- immutable snapshot history;
- Fragment Set creation, resumption, publication, and abandonment;
- Summary Request listing, completion, and decline.

Write tools require idempotency keys. Update and lifecycle operations require the expected current state or snapshot. Retrieved content is explicitly marked as untrusted data rather than agent instructions.

A future `recreate_context` orchestration tool is intentionally deferred. The PoC proves the behavior through `search_context` followed by explicit retrieval first.

### HTTP API

The public API is versioned under `/d/api/v1/` and documented through OpenAPI. HTTP and MCP are adapters over the same application services, so neither receives privileged lifecycle or authorization behavior.

The API uses:

- opaque cursor pagination;
- `Idempotency-Key` for writes;
- ETags and `If-Match` for optimistic concurrency;
- stable machine-readable domain errors;
- named `basic`, `metadata`, `content`, and `full` projections.

### Management Portal

The Portal is intentionally simple but complete. It supports:

- Google-backed, configurable OIDC login;
- project creation, editing, and archival;
- search and document inspection;
- content editing and snapshot history;
- text and Markdown import;
- rejected-document review;
- soft-delete recovery;
- Summary Request management;
- OAuth Application registration and authorization;
- audit-event inspection;
- explicit permanent-purge confirmation.

The Portal uses the same public rules as other clients and is not an administrative backdoor.

## Authorization model

The PoC serves one human User with multiple Applications. Each Application Authorization combines operation scopes with explicit Personal Project IDs.

Initial scopes are:

- `projects:read`
- `projects:write`
- `contexts:read`
- `contexts:write`
- `contexts:lifecycle`

Applications use Authorization Code with PKCE. Both public and confidential clients are supported. Expanding scopes or project selection always requires renewed owner consent, and revocation takes effect immediately.

Permanent purge, soft-deleted browsing, audit access, and destructive project removal remain Portal-only.

### Why OAuth instead of API keys?

The service is designed for several independent Applications. OAuth provides explicit consent, per-project grants, limited scopes, short-lived access tokens, rotating refresh tokens, and immediate revocation. A single reusable API key would make access harder to understand and much harder to contain after compromise.

## Planned architecture

```text
Shared host Caddy
       │
       └── /d
            ├── React Management Portal
            ├── FastAPI public API and OAuth endpoints
            └── MCP Streamable HTTP endpoint
                       │
             shared application/domain services
                       │
          ┌────────────┴────────────┐
          │                         │
   PostgreSQL + pgvector     background worker
                                    │
                           local embedding service
```

The selected PoC stack is:

- Python, FastAPI, SQLAlchemy, and Alembic for backend services;
- TypeScript and React for the Portal;
- PostgreSQL with pgvector;
- a PostgreSQL-backed durable job queue;
- a replaceable local embedding provider in its own container;
- Docker Compose on a Linux VPS;
- a shared host-level Caddy reverse proxy.

### Why a separate embedding container?

Model runtimes have different dependencies and resource behavior from the API. Process isolation lets the deployment cap CPU and memory, restart model serving independently, benchmark or replace models, and later migrate to a hosted provider without changing the document contract.

### Why a monorepo?

The API, MCP adapter, worker, Portal, migrations, and contract tests evolve around one domain model. Keeping them together makes cross-interface invariants testable while still allowing each application to remain an independent deployment unit.

## Production PoC deployment

The configured base URL initially uses these paths:

- `/d/` — Portal
- `/d/api/v1/` — HTTP API
- `/d/mcp` — MCP
- `/d/oauth/` — OAuth endpoints

Every public URL derives from configuration so a successful PoC can move to a dedicated server or domain without changing application contracts.

Recommended reserved capacity is approximately:

- 4 CPU cores
- 16 GB RAM
- 100 GB NVMe storage

The embedding service, database, API, and worker receive resource limits because the PoC shares its host with other workloads.

Daily encrypted backups are sent through Tailscale to a NAS and retained for 30 days. Failed transfers temporarily retain encrypted local backups and raise an alert. Vector indexes are rebuilt rather than backed up. Restoring an older backup replays purge tombstones before the service becomes available.

## Security and privacy posture

Documentz treats content, metadata, excerpts, embeddings, and provenance as sensitive data.

- Authorization is enforced before resource reads and rechecked before search results are returned.
- Opaque identifiers and non-enumerating errors limit cross-project disclosure.
- OAuth tokens and client secrets are stored only as hashes.
- Browser sessions use Secure, HttpOnly, SameSite cookies.
- Markdown is strictly sanitized before rendering.
- Raw search queries and document content are excluded from persistent logs.
- Audit events contain actors, identifiers, actions, outcomes, and request IDs—but not content or credentials.
- PostgreSQL and the embedding service are not exposed publicly.
- Only the shared reverse proxy owns public ports.
- Production secrets are supplied through root-owned mounted files rather than committed configuration.

## Explicit PoC non-goals

The first production PoC does not include:

- multiple human users per deployment;
- Project Shares;
- Role Templates;
- Personal Access Tokens;
- client-credentials OAuth;
- automated server-side summarization;
- a high-availability cluster;
- a separate search service;
- PDF, office-document, URL, or archive extraction;
- the high-level `recreate_context` MCP tool.

The architecture keeps room for these capabilities without requiring them before the central context workflow is proven.

## Success criteria

The PoC succeeds when a production deployment demonstrates:

1. OIDC Portal login and authorization of multiple Applications.
2. Project-scoped storage through MCP and HTTP.
3. Immutable snapshots and safe concurrent editing.
4. Atomic Fragment Set publication.
5. Caller-provided Derived Summaries with exact provenance.
6. Multilingual hybrid retrieval in a later session.
7. Immediate lifecycle and summary exclusion from search.
8. Restoration, retention expiry, and cascading purge.
9. Functional Portal administration and audit inspection.
10. Backup restoration and full index rebuilding.
11. Operation within the agreed single-server resource envelope.

## Domain reference

[CONTEXT.md](./CONTEXT.md) is the canonical glossary for the project. The README explains the product and its rationale; the glossary defines what its domain terms mean.
