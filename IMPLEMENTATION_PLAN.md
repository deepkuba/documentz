# Documentz Implementation Plan

## Objective

Deliver the production PoC described in [README.md](./README.md) and [CONTEXT.md](./CONTEXT.md): a self-hosted, single-user Personal Context Service supporting multiple OAuth-authorized Applications through MCP and HTTP, with a functional Management Portal, immutable document history, caller-provided summaries, atomic Fragment Sets, lifecycle-safe hybrid search, and recoverable production deployment.

Implementation is test-first. Each slice begins with the named failing test, ends with a runnable increment, and is committed independently after its acceptance gate passes.

The slices below are delivery milestones. Their executable task graph, including explicit `blocked-by` and `blocking` relationships, is maintained in [IMPLEMENTATION_TASKS.md](./IMPLEMENTATION_TASKS.md).

## Fixed scope

### Included

- Python/FastAPI API, MCP adapter, worker, and shared domain/application modules
- TypeScript/React Management Portal
- PostgreSQL, pgvector, Alembic migrations, and a PostgreSQL-backed job queue
- Configurable OIDC login, initially exercised with Google
- OAuth Authorization Code with PKCE for public and confidential Applications
- Versioned HTTP API under `/d/api/v1/`
- Remote MCP Streamable HTTP endpoint under `/d/mcp`
- Projects, Context Documents, immutable snapshots, Fragment Sets, Summary Requests, and Derived Summaries
- Lexical, semantic, and hybrid search
- Rejection, soft deletion, restoration, retention expiry, and cascading purge
- Audit records, metrics, production containers, shared-Caddy integration, NAS backups, restore, and re-indexing

### Deferred

- Multiple human users in one deployment
- Project Shares, Role Templates, and Personal Access Tokens
- OAuth client-credentials flow
- Server-generated summaries
- High availability and a separate search cluster
- PDF, office-document, URL, and archive extraction
- The `recreate_context` MCP tool

## Delivery principles

- PostgreSQL is authoritative; queues, lexical indexes, vectors, and excerpts are derived and rebuildable.
- MCP, HTTP, Portal, and workers call the same application services and policy layer.
- Authorization and retrieval eligibility are deny-by-default and checked against current database state.
- State changes and their outbox/job records commit atomically.
- Document content is treated as sensitive, untrusted data and never written to logs or audit records.
- Public contracts use stable error codes, opaque identifiers, explicit projections, idempotency, and optimistic concurrency.
- No production slice is complete without migration, rollback, security, and observability consideration.

## Target repository layout

```text
/
├── apps/
│   ├── api/                    # FastAPI HTTP, OAuth, OIDC, and MCP adapters
│   ├── worker/                 # indexing, retention, purge, and reconciliation jobs
│   └── portal/                 # React/TypeScript Management Portal
├── packages/
│   ├── domain/                 # pure domain types, policies, and errors
│   ├── application/            # use cases and ports
│   └── infrastructure/         # SQLAlchemy repositories and external adapters
├── migrations/                 # Alembic migrations
├── tests/
│   ├── contract/
│   ├── integration/
│   ├── security/
│   └── e2e/
├── deploy/                     # Compose, Caddy snippet, backup and restore tooling
├── CONTEXT.md
├── README.md
└── IMPLEMENTATION_PLAN.md
```

The exact Python packaging tool, React build tool, OAuth library, and PostgreSQL job library are selected in Slice 0 after small compatibility checks. Their selection must not alter the public design.

## Cross-cutting acceptance criteria

- [ ] Only authorized, active, current, published, and fresh content appears in ordinary search or MCP retrieval.
- [ ] Every mutating HTTP request and MCP write is safely idempotent for seven days.
- [ ] Every update detects concurrent modification through the expected current snapshot.
- [ ] No unauthorized response reveals whether another project or document exists.
- [ ] Rejection, soft deletion, source supersession, and purge affect retrieval immediately, even if index cleanup is delayed.
- [ ] All public routes and generated links honor the configurable external base URL and `/d` PoC prefix.
- [ ] Logs, metrics, traces, audits, and errors contain no document content, raw queries, tokens, codes, or client secrets.
- [ ] Every migration has a tested forward path; migrations that can be reversed safely include a downgrade path.
- [ ] The complete system operates inside the agreed 4-CPU, 16-GB RAM, and 100-GB storage reservation.

## Delivery milestones

### Slice 0 — Repository and executable foundation

**Depends on:** nothing

**First failing test:** a configuration test rejects startup when the canonical external base URL is absent or invalid.

- [x] Create the Python workspace, dependency lockfile, formatting, linting, type checking, and pytest configuration.
- [x] Create the React/TypeScript Portal workspace with formatting, linting, type checking, and component-test configuration.
- [ ] Add PostgreSQL/pgvector test infrastructure and Alembic.
- [ ] Add Docker Compose profiles for development, tests, and production-like local execution.
- [x] Select and record the OAuth library, PostgreSQL job library, and frontend build stack in short ADRs.
- [ ] Implement typed configuration with file-based secret support and startup validation.
- [ ] Add `/health/live`, `/health/ready`, structured logging, and request IDs.
- [ ] Add GitHub Actions for formatting, linting, types, unit tests, integration tests, migration checks, secret scanning, dependency scanning, and image builds.
- [ ] Add contributor commands for setup, test, lint, type-check, migrations, and local startup.

**Acceptance gate:** API and Portal boot locally; readiness verifies database connectivity; the database smoke test and all static checks pass in CI.

**Commit:** `chore(repo): establish Documentz application foundation`

### Slice 1 — Pure domain kernel

**Depends on:** Slice 0

**First failing test:** a string with fewer than 16,385 characters but more than 16,384 UTF-8 bytes is rejected.

- [ ] Define opaque UUIDv7 identifiers and UTC timestamp value types.
- [ ] Define document kinds, origins, lifecycle states, Summary Request states, and stable domain error codes.
- [ ] Implement UTF-8 byte limits for ordinary documents, Derived Summaries, and custom metadata.
- [ ] Implement title, tag, custom-kind, metadata-depth, and reserved-key validation.
- [ ] Implement normalized case-insensitive tag identity while preserving display spelling.
- [ ] Implement immutable project, kind, origin, fragment descriptor, and summary source-set invariants.
- [ ] Implement the lifecycle transition table and the independent summary-freshness policy.
- [ ] Implement named projections and field-selection policy.
- [ ] Add property-based tests for lifecycle sequences, byte boundaries, and prohibited Derived Summary graphs.

**Acceptance gate:** the domain package has no web/database imports and fully covers the invariants in `CONTEXT.md`.

**Commit:** `feat(domain): encode document and lifecycle invariants`

### Slice 2 — Relational model and transactional foundation

**Depends on:** Slice 1

**First failing integration test:** two transactions cannot both make different snapshots current for the same expected snapshot.

- [ ] Model the User, OIDC identity, Application, Application Authorization, project, authorization-project selection, and OAuth token records.
- [ ] Model Context Documents, immutable snapshots, tags, metadata, current-snapshot pointers, and origins.
- [ ] Model Fragment Sets and fragment positions.
- [ ] Model summary-source edges, Summary Requests, lifecycle deadlines, purge tombstones, audit events, idempotency records, and outbox/jobs.
- [ ] Add database constraints for unique project names, snapshot immutability, one current snapshot, fragment positions, same-project references, and no Derived Summary source edges.
- [ ] Implement transaction management, repository ports, optimistic concurrency, and idempotency replay/conflict behavior.
- [ ] Add database fixtures/builders and migration upgrade/downgrade tests.

**Acceptance gate:** a real PostgreSQL integration suite proves constraints, transaction rollback, concurrency conflicts, and seven-day idempotency semantics.

**Commit:** `feat(storage): add transactional context persistence`

### Slice 3 — Projects and Context Documents over HTTP

**Depends on:** Slice 2

**First failing contract test:** a stale `If-Match` update returns `conflict` and does not create a snapshot.

- [ ] Define the `/d/api/v1` OpenAPI contract, standard error envelope, projections, cursor envelope, ETags, and idempotency header.
- [ ] Implement project create, read, list, update, and archive use cases.
- [ ] Implement document create, read, list, patch, snapshot list, and snapshot read use cases.
- [ ] Enforce non-empty exact UTF-8 content and server-derived origin.
- [ ] Return active documents by default; support explicit rejected listing; exclude soft-deleted documents from Application reads.
- [ ] Add deterministic opaque cursor pagination with default 20 and maximum 50 items.
- [ ] Ensure unknown and unauthorized IDs produce indistinguishable safe errors.
- [ ] Generate and validate the OpenAPI artifact in CI.

**Acceptance gate:** an authorized test principal can create a project, version a document, and browse its immutable history through HTTP; concurrency and enumeration tests pass.

**Commit:** `feat(api): expose versioned projects and documents`

### Slice 4 — Portal OIDC login and owner control plane

**Depends on:** Slices 2–3

**First failing security test:** an authenticated OIDC subject not matching the configured allowlist cannot establish a Portal session.

- [ ] Integrate configurable OIDC discovery and Authorization Code login, initially tested with Google.
- [ ] Enforce exact issuer and allowlisted subject matching.
- [ ] Implement server-side Portal sessions using Secure, HttpOnly, SameSite cookies scoped to `/d`.
- [ ] Implement session rotation, CSRF protection, 12-hour inactivity, and seven-day absolute expiry.
- [ ] Add the Portal shell, login/logout, project list/create/edit/archive, and basic document list/detail/edit/history views.
- [ ] Render document content as text by default and strictly sanitize Markdown rendering.
- [ ] Deny cross-origin browser API requests in the PoC.

**Acceptance gate:** the owner can securely sign in and complete the core project/document workflow; OIDC, CSRF, session fixation, expiry, and XSS tests pass.

**Commit:** `feat(portal): add secure owner login and document management`

### Slice 5 — OAuth Applications and authorization policy

**Depends on:** Slices 3–4

**First failing security test:** a token granted one project cannot distinguish a missing document from a document in another project.

- [ ] Implement manual registration for public and confidential Applications.
- [ ] Validate exact redirect URIs, HTTPS remote URIs, loopback-native exceptions, and prohibit wildcards.
- [ ] Implement Authorization Code with mandatory PKCE S256.
- [ ] Issue 15-minute opaque access tokens and rotating refresh tokens stored only as hashes.
- [ ] Detect refresh-token reuse and revoke the affected authorization.
- [ ] Implement scopes, scope implication, explicit project selection, and renewed consent for expansion.
- [ ] Automatically add a project created by an authorized Application to that authorization.
- [ ] Implement immediate authorization/Application revocation and non-secret tombstones.
- [ ] Add OAuth authorization-server and protected-resource discovery required by the MCP resource URL.
- [ ] Add Portal pages for Application registration, redirect URIs, consent, project/scopes, rotation, usage, and revocation.

**Acceptance gate:** public and confidential reference clients complete OAuth, access only selected projects, refresh safely, and lose access immediately after revocation.

**Commit:** `feat(auth): authorize project-scoped applications with OAuth`

### Slice 6 — MCP adapter and tool contracts

**Depends on:** Slice 5

**First failing contract test:** an unauthenticated MCP request receives the protocol-required HTTP authorization challenge rather than a tool-level authorization error.

- [ ] Implement Streamable HTTP MCP with protocol-version negotiation at `/d/mcp`.
- [ ] Expose project tools: `list_projects`, `create_project`, `update_project`, and `archive_project`.
- [ ] Expose document tools: `list_contexts`, `store_context`, `get_context`, `update_context`, `change_context_lifecycle`, `list_document_snapshots`, and `get_document_snapshot`.
- [ ] Use explicit project IDs, named projections, cursor pagination, expected snapshots/states, and idempotency keys.
- [ ] Map MCP failures to the same stable domain errors as HTTP.
- [ ] Add accurate read-only, destructive, idempotent, and closed-world annotations.
- [ ] Mark returned document content as untrusted data, not instructions.
- [ ] Add parity tests proving HTTP and MCP enforce identical policy and behavior.

**Acceptance gate:** two independently registered MCP clients can complete project and versioned-document workflows without crossing grants.

**Commit:** `feat(mcp): expose authorized context operations`

### Slice 7 — Atomic Fragment Sets and Portal imports

**Depends on:** Slices 3 and 6

**First failing integration test:** a concurrent reader never observes a partly published Fragment Set.

- [ ] Implement create, inspect, publish, abandon, and expire use cases for draft Fragment Sets.
- [ ] Enforce same project/kind/custom kind, shared metadata, unique positions, maximum 256 fragments, and maximum 4 MiB total.
- [ ] Freeze membership and order at publication while allowing later fragment snapshots.
- [ ] Apply lifecycle changes atomically to every member.
- [ ] Expose `create_fragment_set`, `get_fragment_set`, `publish_fragment_set`, and `abandon_fragment_set` through MCP and corresponding HTTP endpoints.
- [ ] Support paginated and position-range fragment retrieval.
- [ ] Implement UTF-8 text and Markdown Portal import, digest duplicate warnings, split preview, and confirmed publication.
- [ ] Split on Markdown headings and paragraph boundaries before falling back to safe UTF-8 byte boundaries.
- [ ] Add a worker job that permanently removes abandoned/expired drafts after 24 hours.

**Acceptance gate:** interrupted uploads resume safely, incomplete sets never leak, publication is atomic, and oversized imports produce one logical searchable body.

**Commit:** `feat(fragments): publish large context atomically`

### Slice 8 — Summary Requests and Derived Summaries

**Depends on:** Slices 3 and 7

**First failing domain/integration test:** attempting to cite a Derived Summary as a source fails atomically with `summary_source_invalid`.

- [ ] Create persistent Summary Requests for eligible active source documents and session summaries above 2 KiB.
- [ ] Create set-level requests only after Fragment Set publication.
- [ ] Return structured optional summary requests from write operations.
- [ ] Implement pending, completed, declined, and superseded transitions.
- [ ] Allow authorized writers to list, complete, and decline project requests.
- [ ] Implement Derived Summary storage using exact, same-project, non-Derived source snapshot IDs.
- [ ] Fix source edges at creation and allow multiple summaries over the same sources.
- [ ] Compute effective access from sources rather than caller input.
- [ ] Expose `list_summary_requests` and `decline_summary_request` through MCP.
- [ ] Add Portal request and provenance views.

**Acceptance gate:** the complete two-step caller summarization flow works after ordinary writes and Fragment Set publication, including retry, decline, supersession, and multi-source cases.

**Commit:** `feat(summaries): add caller-provided derived summaries`

### Slice 9 — Lifecycle propagation, retention, and purge

**Depends on:** Slice 8

**First failing integration test:** purging one source of a multi-source summary removes that summary and every derived representation in the same committed operation or retry-safe workflow.

- [ ] Implement reject, reactivate, soft-delete, restore, and Portal-only purge use cases.
- [ ] Require expected lifecycle state and idempotency keys.
- [ ] Give each soft deletion a fresh 30-day recovery deadline.
- [ ] Mark dependent summaries stale synchronously on source rejection, deletion, or supersession.
- [ ] Restore eligibility only when every source is active and every referenced snapshot remains current.
- [ ] Cascade purge through source relationships, Fragment Sets, tags, metadata, jobs, and indexes.
- [ ] Retain only non-content audit/purge tombstones.
- [ ] Add retry-safe retention and purge workers.
- [ ] Add Portal rejected, recovery, dependency-preview, typed-confirmation, and purge-completion views.

**Acceptance gate:** exhaustive transition-table, race, retry, restoration, expiry, and cascade tests prove that ineligible content cannot be retrieved.

**Commit:** `feat(lifecycle): enforce recovery and cascading purge`

### Slice 10 — Lexical indexing and search

**Depends on:** Slices 7–9

**First failing end-to-end test:** rejecting a searchable source immediately removes both it and its Derived Summaries from results before queued index cleanup runs.

- [ ] Implement transactional outbox/job creation for index upsert and removal.
- [ ] Implement current-snapshot passage extraction and PostgreSQL lexical indexing.
- [ ] Implement query validation, project/kind/tag/origin/time filters, and tag-any/tag-all semantics.
- [ ] Return compact ranked results with excerpts and provenance, collapsing Fragment Sets into one logical result.
- [ ] Implement opaque cursors bound to query, filters, authorization, and index version; return `cursor_expired` after incompatible changes.
- [ ] Re-check authorization, publication, lifecycle, currency, and summary freshness in PostgreSQL for every candidate.
- [ ] Exclude raw queries from logs and audits.
- [ ] Add reconciliation and full lexical-rebuild jobs.

**Acceptance gate:** lexical search remains correct during worker lag, duplicate delivery, index drift, lifecycle changes, authorization changes, and rebuilds.

**Commit:** `feat(search): add lifecycle-safe lexical retrieval`

### Slice 11 — Local semantic and hybrid retrieval

**Depends on:** Slice 10

**First failing acceptance test:** representative cross-language queries retrieve their relevant fixtures when exact query terms are absent.

- [ ] Define the replaceable embedding-provider port and internal-only HTTP adapter.
- [ ] Benchmark compact CPU-friendly multilingual models using Polish, English, and cross-language fixtures.
- [ ] Record the chosen model, version, dimensions, passage parameters, and benchmark in an ADR.
- [ ] Build and resource-limit the embedding container.
- [ ] Store model-versioned passage embeddings in pgvector.
- [ ] Implement semantic and hybrid ranking, document deduplication, and optional `prefer_summaries`.
- [ ] Treat numeric scores as optional non-comparable diagnostics.
- [ ] Implement hybrid lexical fallback with `degraded: true` and semantic partial results with `partial: true`.
- [ ] Add parallel model-version re-indexing and atomic index activation.
- [ ] Add Portal indexing status and administrative rebuild controls.

**Acceptance gate:** relevance fixtures pass, model downtime never blocks durable writes, and a complete model/index loss can be rebuilt without document loss.

**Commit:** `feat(search): add multilingual hybrid retrieval`

### Slice 12 — Complete Portal workflows and audit visibility

**Depends on:** Slices 8–11

**First failing browser test:** a User can reject a document from search results, observe its immediate disappearance, inspect it in the rejected view, and reactivate it.

- [ ] Complete search mode/filter/pagination UI and document projections.
- [ ] Complete Fragment Set detail, import provenance, source/summary graph, and indexing-status views.
- [ ] Complete Summary Request completion/decline status views.
- [ ] Add soft-deleted recovery and purge-impact workflows.
- [ ] Add append-only audit storage and Portal viewer for authentication, authorization, project, document, lifecycle, summary, and purge events.
- [ ] Ensure audit events contain safe identifiers and change metadata but no content, queries, tokens, codes, or secrets.
- [ ] Add accessible loading, empty, validation, conflict, expired-session, and degraded-search states.

**Acceptance gate:** browser-level tests cover every Portal workflow listed in the README, including errors and destructive confirmations.

**Commit:** `feat(portal): complete context administration workflows`

### Slice 13 — Operational hardening

**Depends on:** Slices 5–12

**First failing operational test:** a dead embedding service causes bounded retries and an alert without blocking document storage or exhausting the job queue.

- [ ] Add bounded retries, backoff, dead-letter state, reconciliation, and safe administrative retry controls.
- [ ] Add per-Application read/search and write limits, OAuth abuse limits, and one active import per User.
- [ ] Add payload, timeout, connection, pagination, and dependency-resource bounds.
- [ ] Add metrics for HTTP, OAuth, job lag, indexing, dead letters, purge, capacity, and database health.
- [ ] Add external readiness semantics and graceful shutdown for API and workers.
- [ ] Add disk/database capacity alerts and an external uptime check.
- [ ] Run authorization, CSRF, XSS, redirect, token, SQL injection, SSRF, unsafe deserialization, log-leakage, and dependency reviews.
- [ ] Run concurrency tests for snapshot updates, publication, summary completion, restoration versus purge, and duplicate jobs.
- [ ] Load-test the agreed 10,000-document, 100-write/day, and three-Application envelope.

**Acceptance gate:** security tests pass, overload degrades safely, no sensitive data appears in telemetry, and load remains within the reserved resources.

**Commit:** `feat(ops): harden service limits and observability`

### Slice 14 — Production packaging, deployment, and recovery

**Depends on:** Slice 13

**First failing deployment test:** the production Compose configuration refuses to start without mounted secrets and a valid canonical `/d` base URL.

- [ ] Produce pinned, non-root, health-checked images for API, worker, Portal, database, and embedding service.
- [ ] Define CPU/memory limits and private networks; expose application ports only to the shared host Caddy.
- [ ] Provide the host-Caddy route snippet for `/d`, standards-required OAuth discovery routes, forwarded headers, request limits, and TLS.
- [ ] Mount production secrets from root-owned files and document rotation.
- [ ] Implement CI-built versioned images and an approval-gated pull/migrate/rollout deployment.
- [ ] Add health-based rollback and a database migration rollback/runbook decision point.
- [ ] Implement encrypted Restic backup of consistent PostgreSQL dumps and required configuration to the NAS through Tailscale.
- [ ] Retain up to seven encrypted local backups during NAS outages, enforce a disk floor, and alert on transfer failure.
- [ ] Apply 30-day remote retention and document separate secret recovery.
- [ ] Implement restore tooling that replays purge tombstones before reopening and then rebuilds indexes.
- [ ] Perform and record a production-like backup, destructive sandbox restore, and complete index rebuild.

**Acceptance gate:** the service deploys behind the shared Caddy, survives restart, rolls back a failed release, restores from NAS backup, reapplies purges, and rebuilds search.

**Commit:** `feat(deploy): add recoverable production deployment`

### Slice 15 — Production PoC acceptance

**Depends on:** all previous slices

**First failing end-to-end test:** a newly authorized Application cannot yet store context in one session and retrieve it through hybrid MCP search in a fresh session.

- [ ] Exercise Google OIDC owner login.
- [ ] Register and authorize at least three Applications with different project grants.
- [ ] Store, update, list, and retrieve ordinary documents through both HTTP and MCP.
- [ ] Import and publish a multi-fragment Markdown source through the Portal.
- [ ] Complete a Summary Request from an Application and retrieve its Derived Summary later.
- [ ] Prove English, Polish, and cross-language hybrid retrieval.
- [ ] Prove optimistic concurrency and idempotent retry behavior.
- [ ] Reject/reactivate and soft-delete/restore sources while checking immediate summary/search behavior.
- [ ] Purge a source through the Portal and verify cascading removal across every interface and index.
- [ ] Review audit records and verify telemetry contains no prohibited data.
- [ ] Restore the production dataset into an isolated environment and rebuild all derived indexes.
- [ ] Run the full quality, contract, security, browser, load, migration, container, and deployment suites.
- [ ] Reconcile README claims and OpenAPI/MCP documentation with observed behavior.

**Acceptance gate:** all README success criteria have linked evidence, no release-blocking security findings remain, and the owner signs off on the deployed workflow.

**Commit:** `release: validate Documentz production PoC`

## Test strategy

### Unit and property tests

- UTF-8 byte boundaries and exact content preservation
- Metadata/tag validation and normalization
- Lifecycle transition sequences
- Summary graph constraints and freshness
- Fragment completeness and ordering
- Projection and scope policy
- Cursor and idempotency semantics

### PostgreSQL integration tests

- Schema constraints and migrations
- Transaction rollback and optimistic concurrency
- Idempotency replay under concurrent requests
- Atomic Fragment Set publication and lifecycle propagation
- Summary invalidation and cascading purge
- Outbox/job atomicity, retries, and duplicate delivery
- Lexical/vector eligibility rechecks

### Contract tests

- OpenAPI schema and backward compatibility
- Stable error codes and non-enumerating failures
- OAuth discovery, authorization, refresh, and revocation
- MCP initialization, authorization challenge, tools, annotations, and schemas
- HTTP/MCP behavioral parity

### Browser tests

- OIDC session lifecycle and CSRF
- Projects, documents, history, and search
- Import and Fragment Set preview/publication
- Summary Requests and provenance
- Application consent/revocation
- Reject, recovery, and purge confirmation
- Audit and degraded-index states

### Security tests

- Cross-project and cross-Application authorization
- OAuth redirect and PKCE attacks, token replay, and refresh reuse
- XSS through Markdown/content/metadata
- SQL injection and malformed JSON
- SSRF through configurable URLs and Application metadata
- Oversized/deep payloads and resource exhaustion
- Sensitive-data leakage in logs, errors, metrics, backups, and audit events

### Production tests

- Container health, non-root execution, private networking, and resource limits
- Shared-Caddy routing and canonical URL generation under `/d`
- Upgrade, failed migration, rollback, restart, and graceful shutdown
- NAS outage, local backup retention, restore, purge replay, and re-indexing
- Capacity and latency at and beyond the expected PoC envelope

## Security review gates

Perform a focused security review before merging Slices 5, 9, 11, 13, and 14. Each review must document:

- assets and trust boundaries changed by the slice;
- authorization and project-boundary checks;
- attacker-controlled inputs and output encoding;
- secrets/token handling and log redaction;
- concurrency, replay, retry, and partial-failure behavior;
- resource-exhaustion limits;
- discovered issues, fixes, and residual risks.

Release is blocked by unresolved critical/high findings or by any path that can return ineligible content.

## Verification commands

Slice 0 will establish stable commands equivalent to:

```text
format-check
lint
type-check
unit-test
integration-test
contract-test
security-test
portal-test
e2e-test
migration-check
container-build
```

Every slice runs the narrowest failing test first, its affected suites next, and the complete CI suite before commit. Deployment-related slices additionally validate Compose rendering and production startup in an isolated environment.

## Commit and progress policy

- Use one coherent commit per accepted slice; use smaller commits within a slice when they remain independently passing and reviewable.
- Keep schema migration, production behavior, tests, and contract changes in the same logical delivery.
- Review the complete diff before every commit for unrelated files, generated artifacts, secrets, debug code, and accidental content fixtures.
- Update this plan as discoveries alter dependencies or acceptance criteria; do not silently change the behavior defined by README or CONTEXT.
- Record PoC evidence beside the acceptance criteria rather than relying on an unstructured final test report.

## Definition of done

The project is implementation-complete for the PoC only when:

- all 16 slices pass their acceptance gates;
- every README success criterion is demonstrated in the production deployment;
- HTTP, MCP, Portal, worker, and restored-backup behavior agree on authorization and lifecycle eligibility;
- the security review has no unresolved release-blocking findings;
- recovery and full index reconstruction have been exercised, not merely documented;
- operating limits, known residual risks, and deferred capabilities are documented;
- the owner confirms the deployed system supports the intended cross-session context workflow.
