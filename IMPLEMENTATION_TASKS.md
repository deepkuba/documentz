# Documentz Implementation Tasks

This is the executable task graph for the milestones in [IMPLEMENTATION_PLAN.md](./IMPLEMENTATION_PLAN.md). The milestone document owns scope and acceptance criteria; this file determines what can be worked on safely and in parallel.

## Execution rules

- A task may start only when every task in its `blocked-by` tag is complete.
- `blocked-by: none` means the task can be taken immediately and in parallel with every other ready task.
- `blocking` lists direct dependents, not every transitive descendant.
- A task is complete only when its binary gate passes and its artifacts are committed or otherwise made available to dependent tasks.
- If implementation changes a dependency, update both sides of the graph before starting affected work.
- Within a task: write the named/focused failing test, confirm the failure, implement the smallest behavior, run targeted checks, then run the task gate.
- The first-failure registry below is part of each task's scope. A task may refine the eventual test filename to match the selected framework, but may not weaken the stated failing behavior.
- A completion gate is binary: every clause must have automated evidence unless the gate explicitly calls for recorded manual evidence. Partial completion does not unblock dependents.

## First-failure registry

| Task | First failing test or executable check |
| --- | --- |
| `F01` | `architecture_decisions_are_complete` fails because required toolchain ADRs and pinned choices do not exist. |
| `F02` | `python_workspace_smoke` fails because the backend package and test entry point do not exist. |
| `F03` | `portal_workspace_smoke` fails because the Portal shell cannot render or build. |
| `F04` | `postgres_pgvector_smoke` fails because no test database enables pgvector or accepts migrations. |
| `F05` | `production_config_requires_canonical_base_url` fails because invalid production configuration currently starts. |
| `D01` | `rejects_multibyte_content_over_utf8_limit` fails because document byte limits are not encoded. |
| `D02` | `purged_document_has_no_outgoing_transition` fails because lifecycle policy does not exist. |
| `D03` | `derived_summary_rejects_derived_source` fails because source-graph policy does not exist. |
| `D04` | `fragment_set_rejects_duplicate_position` fails because Fragment Set invariants do not exist. |
| `D05` | `context_invariants_have_test_coverage` fails because the traceability manifest is incomplete. |
| `S01` | `database_allows_only_one_current_snapshot` fails because core persistence and its constraint do not exist. |
| `S02` | `stored_oauth_secret_is_not_recoverable` fails because Application persistence does not exist. |
| `S03` | `database_rejects_cross_project_summary_source` fails because relationship constraints do not exist. |
| `S04` | `state_change_and_outbox_job_commit_atomically` fails because transactional jobs do not exist. |
| `S05` | `competing_snapshot_updates_have_one_winner` fails because the unit of work does not enforce optimistic concurrency. |
| `C00` | `canonical_examples_are_complete` fails because one or more planned resources/tools lack request, success, and error examples. |
| `C01` | `openapi_accepts_canonical_examples` fails because the versioned contract has not been defined. |
| `H01` | `stale_document_patch_creates_no_snapshot` fails because application services do not exist. |
| `H02` | `unauthorized_and_missing_document_errors_match` fails because HTTP policy/error mapping does not exist. |
| `H03` | `published_openapi_has_no_unapproved_break` fails because the core contract has not been certified. |
| `P01` | `non_allowlisted_oidc_subject_cannot_create_session` fails because owner session handling does not exist. |
| `P02` | `owner_edits_document_with_current_etag` fails because the core Portal workflow does not exist. |
| `P03` | `stored_markdown_script_does_not_execute` fails because rendering/session security has not been certified. |
| `A01` | `reference_client_completes_pkce_under_base_path` fails because OAuth library integration is absent. |
| `A02` | `reused_refresh_token_revokes_authorization` fails because token rotation/reuse detection is absent. |
| `A03` | `revoked_project_grant_stops_existing_token` fails because discovery and complete authorization enforcement are absent. |
| `M01` | `unauthenticated_mcp_request_returns_http_challenge` fails because authenticated MCP transport is absent. |
| `M02` | `store_context_retry_returns_original_result` fails because core MCP tools and idempotency binding are absent. |
| `M03` | `http_and_mcp_same_use_case_have_equal_policy_result` fails because parity certification is absent. |
| `G01` | `reader_never_observes_partly_published_set` fails because atomic Fragment Set services are absent. |
| `G02` | `interrupted_fragment_upload_resumes_across_adapters` fails because public Fragment Set adapters are absent. |
| `G03` | `expired_draft_is_removed_but_concurrently_published_set_survives` fails because expiry processing is absent. |
| `G04` | `fragment_acceptance_matrix_is_complete` fails because milestone certification evidence is incomplete. |
| `I01` | `markdown_split_preserves_exact_utf8_content` fails because import splitting is absent. |
| `I02` | `portal_publishes_confirmed_split_only` fails because the import UI is absent. |
| `U01` | `eligible_source_creates_one_pending_request` fails because Summary Request services are absent. |
| `U02` | `second_application_completes_project_summary_request_once` fails because public summary workflows are absent. |
| `U03` | `fresh_session_retrieves_caller_provided_summary_with_provenance` fails because end-to-end summary behavior is uncertified. |
| `P04` | `portal_displays_stale_summary_and_exact_sources` fails because summary/provenance views are absent. |
| `L01` | `rejecting_source_immediately_invalidates_dependents` fails because lifecycle propagation is absent. |
| `L02` | `purging_one_source_removes_multi_source_summary_once` fails because retry-safe cascading purge is absent. |
| `L03` | `application_cannot_purge_through_http_or_mcp` fails because lifecycle adapter boundaries are absent. |
| `L04` | `generated_lifecycle_sequences_never_expose_ineligible_content` fails because lifecycle certification is incomplete. |
| `X01` | `duplicate_outbox_delivery_produces_one_lexical_entry` fails because lexical indexing is absent. |
| `X02` | `rejected_candidate_is_filtered_before_return` fails because authoritative eligibility rechecks are absent. |
| `X03` | `search_query_is_absent_from_logs_and_audit` fails because public search adapters and redaction are absent. |
| `X04` | `lexical_results_remain_correct_during_full_rebuild` fails because rebuild certification is absent. |
| `E00` | `relevance_fixture_set_has_required_language_coverage` fails because judged fixtures do not exist. |
| `E01` | `selected_model_meets_relevance_and_resource_thresholds` fails because no benchmarked selection exists. |
| `E02` | `embedding_timeout_does_not_block_durable_write` fails because the provider boundary is absent. |
| `V01` | `new_model_index_build_does_not_replace_active_index_early` fails because versioned vector indexing is absent. |
| `V02` | `hybrid_search_returns_lexical_results_when_embeddings_fail` fails because hybrid degradation is absent. |
| `V03` | `cross_language_acceptance_queries_meet_threshold` fails because multilingual hybrid retrieval is uncertified. |
| `O01` | `telemetry_contains_no_content_query_or_token` fails because safe telemetry enforcement is absent. |
| `P05` | `owner_rejects_search_result_and_reactivates_it` fails because the complete Portal workflows are absent. |
| `P06` | `portal_critical_journey_uses_public_policy_only` fails because complete browser certification is absent. |
| `Q00` | `threat_model_covers_every_declared_trust_boundary` fails because the threat model does not exist. |
| `O02` | `dead_embedding_service_has_bounded_retries_and_alert` fails because operational limits are absent. |
| `O03` | `expected_load_stays_inside_reserved_resources` fails because hardening/load certification is absent. |
| `R00` | `production_inventory_has_all_required_nonsecret_values` fails because the host/recovery inventory is incomplete. |
| `R01` | `production_stack_exposes_only_shared_caddy` fails because hardened packaging/routing is absent. |
| `R02` | `failed_release_restores_previous_healthy_version` fails because deployment rollback is absent. |
| `R03` | `restored_backup_replays_purges_before_readiness` fails because recovery tooling is absent. |
| `R04` | `production_runbook_completes_without_undocumented_repair` fails because deployment certification is incomplete. |
| `Z01` | `production_poc_acceptance_matrix_is_complete` fails until every success criterion has linked evidence and owner sign-off. |

## Initial parallel frontier

The following tasks have `blocked-by: none` and may begin together:

- `F01` — record foundation technology decisions
- `C00` — draft public contract examples
- `E00` — assemble multilingual relevance fixtures
- `R00` — inventory the production host and recovery dependencies
- `Q00` — create the security threat model

## Milestone 0 — Repository and executable foundation

### F01 — Record foundation technology decisions

Select the Python packaging tool, supported runtime versions, React build/test stack, OAuth library, PostgreSQL job library, and lint/type/test tools. Record concise ADRs and lock the initial versions.

- `blocked-by: none`
- `blocking: F02, F03, F04, A01`
- **Gate:** ADRs name one supported toolchain with compatibility evidence; bootstrap commands are unambiguous.

### F02 — Scaffold the Python workspace

Create the API, worker, domain, application, and infrastructure packages with locked dependencies and baseline formatting, linting, typing, and pytest commands.

- `blocked-by: F01`
- `blocking: F05, D01`
- **Gate:** a trivial unit test passes and formatting, linting, and type checking succeed from a clean checkout.

### F03 — Scaffold the Portal workspace

Create the React/TypeScript application with locked dependencies, formatting, linting, type checking, component tests, and a production build.

- `blocked-by: F01`
- `blocking: F05, P01`
- **Gate:** a shell component test and production build pass from a clean checkout.

### F04 — Add local PostgreSQL and Compose infrastructure

Add PostgreSQL with pgvector, private networks, persistent development volumes, test isolation, and Alembic connectivity.

- `blocked-by: F01`
- `blocking: F05, S01`
- **Gate:** the database smoke test enables pgvector and applies an empty migration chain in development and test profiles.

### F05 — Add configuration, health, logging, and CI

Implement typed configuration, mounted-secret support, canonical-base-URL validation, request IDs, structured logging, health/readiness endpoints, and CI jobs for all established checks.

- `blocked-by: F02, F03, F04`
- `blocking: D01, A01, E02, M01, O01`
- **Gate:** missing/invalid production configuration fails startup; local services become ready; the complete foundation CI workflow passes.

## Milestone 1 — Pure domain kernel

### D01 — Implement document primitives and validation

Add UUIDv7 identifiers, UTC timestamps, document kinds/origins, stable errors, UTF-8 byte limits, titles, tags, custom kinds, metadata bounds, and exact-content preservation.

- `blocked-by: F02, F05`
- `blocking: D02, D03, D04`
- **Gate:** boundary and property tests pass, including multibyte content exceeding the byte limit below the character limit.

### D02 — Implement lifecycle and freshness policies

Encode valid lifecycle transitions, editing rules by state, soft-delete deadlines, stale-summary eligibility, and terminal purge behavior as pure policies.

- `blocked-by: D01`
- `blocking: D05`
- **Gate:** exhaustive state-transition and generated event-sequence tests prove invalid states cannot become ordinarily retrievable.

### D03 — Implement summary policies

Encode Summary Request eligibility/states, exact source-set rules, same-project enforcement, prohibited Derived-to-Derived edges, access intersection, and regeneration behavior.

- `blocked-by: D01`
- `blocking: D05`
- **Gate:** graph/property tests cover allowed session summaries, forbidden chains, multiple summaries, staleness, decline, completion, and supersession.

### D04 — Implement Fragment Set and projection policies

Encode set completeness, position/order rules, size limits, shared metadata, immutable membership, named projections, and lifecycle/search collapsing semantics.

- `blocked-by: D01`
- `blocking: D05`
- **Gate:** pure tests cover incomplete, duplicate, oversized, reordered, and projection/redaction cases.

### D05 — Certify the domain package

Map every invariant in `CONTEXT.md` to a unit/property test and confirm the package has no framework, database, HTTP, or MCP imports.

- `blocked-by: D02, D03, D04`
- `blocking: S01, C01, E01`
- **Gate:** the domain traceability checklist is complete and the isolated domain suite passes.

## Milestone 2 — Relational and transactional foundation

### S01 — Add core project, document, and snapshot persistence

Create initial migrations and repositories for the owner, projects, documents, immutable snapshots, current pointers, tags, metadata, and archived projects.

- `blocked-by: F04, D05`
- `blocking: S02, S03, S04`
- **Gate:** migrations apply cleanly and database constraints prevent duplicate normalized project names and multiple current snapshots.

### S02 — Add Application and authorization persistence

Create Application, redirect URI, authorization, selected-project, scope, authorization-code, access-token, refresh-token, and revocation records without implementing protocol endpoints.

- `blocked-by: S01`
- `blocking: S05, A02`
- **Gate:** repository tests prove secret/token hashes, exact redirect storage, grant replacement, and immediate revocation queries.

### S03 — Add fragments, summaries, requests, and lifecycle persistence

Create Fragment Set/member, summary-source, Summary Request, lifecycle deadline, purge tombstone, and dependency-query structures with database constraints.

- `blocked-by: S01`
- `blocking: S05`
- **Gate:** the database rejects cross-project sources, Derived Summary sources, invalid fragment positions, duplicate edges, and mutable immutable fields.

### S04 — Add idempotency, jobs, outbox, and audit persistence

Create seven-day idempotency records, transactional outbox/jobs, retry/dead-letter state, append-only safe audit events, and cleanup queries.

- `blocked-by: S01`
- `blocking: S05, G03, L02, O01, X01`
- **Gate:** concurrent integration tests prove one idempotent outcome, atomic job creation, retry-safe claiming, and append-only audits.

### S05 — Certify transactional persistence

Implement shared unit-of-work/repository ports, optimistic concurrency, rollback behavior, fixture builders, and migration checks across all persistence modules.

- `blocked-by: S02, S03, S04`
- `blocking: H01, A02, G01, U01`
- **Gate:** the real-PostgreSQL suite passes under competing writes, rollback, duplicate delivery, and migration upgrade/downgrade scenarios.

## Milestone 3 — HTTP projects and documents

### C00 — Draft public contract examples

Turn the confirmed design into example HTTP requests/responses, MCP inputs/results, projection shapes, cursor envelopes, and stable error examples without committing framework-specific schemas.

- `blocked-by: none`
- `blocking: C01`
- **Gate:** examples cover every planned resource/tool and contain no unresolved product choices or contradictory field names.

### C01 — Define the versioned HTTP contract

Create `/d/api/v1` schemas for projects, documents, snapshots, projections, cursors, errors, idempotency, and ETags; add generated OpenAPI compatibility checking.

- `blocked-by: C00, D05`
- `blocking: H01, A02`
- **Gate:** schema tests accept every canonical example, reject invalid variants, and generate one deterministic OpenAPI document.

### H01 — Implement project and document application services

Add project create/list/update/archive and document create/list/get/patch/history use cases using repositories, policies, projections, expected snapshots, and server-derived origins.

- `blocked-by: S05, C01`
- `blocking: H02`
- **Gate:** service tests pass for success, authorization-policy hooks, conflicts, rejected visibility, soft-deleted exclusion, and idempotent replay.

### H02 — Expose project and document HTTP endpoints

Bind H01 to FastAPI, including ETags, `If-Match`, `Idempotency-Key`, opaque cursors, default/maximum page sizes, request IDs, and non-enumerating errors.

- `blocked-by: H01`
- `blocking: H03, P02`
- **Gate:** HTTP integration tests complete project and snapshot workflows and prove invalid/unauthorized IDs are indistinguishable.

### H03 — Certify the core HTTP API

Run contract, migration, concurrency, error, projection, pagination, and backward-compatibility tests; publish the first OpenAPI artifact.

- `blocked-by: H02`
- `blocking: A02, M02, G02`
- **Gate:** all Milestone 3 acceptance criteria pass and the OpenAPI artifact is checked into/generated by CI as decided in F01.

## Milestone 4 — Portal owner login and core control plane

### P01 — Implement OIDC owner sessions and Portal shell

Add configurable OIDC discovery/login, issuer and subject allowlisting, server-side sessions, secure cookie policy, rotation, expiry, logout, and the authenticated Portal layout.

- `blocked-by: F03, A01`
- `blocking: P02, A03`
- **Gate:** OIDC/session tests reject every non-allowlisted identity and cover fixation, expiry, logout, cookie attributes, and callback failures.

### P02 — Implement core project and document screens

Add project list/create/edit/archive and document list/detail/edit/history screens using the public API contract, including loading, empty, validation, and conflict states.

- `blocked-by: P01, H02`
- `blocking: P03`
- **Gate:** component/browser tests complete the core owner workflow without privileged backdoor endpoints.

### P03 — Certify Portal session and rendering security

Add CSRF enforcement, same-origin CORS policy, sanitized Markdown, safe text defaults, CSP/security headers, and browser security regressions.

- `blocked-by: P02, Q00`
- `blocking: I02, P04`
- **Gate:** CSRF, stored/reflected XSS, session, CORS, and security-header tests pass.

## Milestone 5 — OAuth Applications

### A01 — Prove the OAuth/OIDC library integration

Build a narrow spike covering Authorization Code, PKCE S256, opaque token hooks, custom consent, configurable base paths, and MCP-compatible discovery. Record limitations in the ADR.

- `blocked-by: F01, F05, Q00`
- `blocking: A02, P01`
- **Gate:** an automated reference-client test completes the spike flow under `/d` without custom protocol shortcuts.

### A02 — Implement Application registration, consent, and tokens

Implement public/confidential registration, redirect validation, scope/project grants, consent expansion, project auto-add, authorization codes, 15-minute opaque access tokens, rotating refresh tokens, reuse detection, and revocation.

- `blocked-by: S02, S05, C01, H03, A01`
- `blocking: A03`
- **Gate:** protocol integration tests cover public/confidential clients, exact redirects, PKCE downgrade attempts, refresh rotation/reuse, grant expansion, and immediate revocation.

### A03 — Add discovery, Portal management, and authorization security gate

Expose authorization/protected-resource metadata and owner pages for registration, secrets, redirects, consent, usage, scope/project changes, and revocation; finish cross-project security tests.

- `blocked-by: A02, P01`
- `blocking: M01, O02`
- **Gate:** reference Applications discover and authorize correctly, while enumeration and cross-project tests pass for every scope combination.

## Milestone 6 — MCP adapter

### M01 — Implement authenticated Streamable HTTP transport

Add `/d/mcp`, protocol negotiation, OAuth challenges, bearer-token validation, request context, resource metadata integration, and shared error mapping.

- `blocked-by: A03, F05`
- `blocking: M02`
- **Gate:** MCP transport tests cover initialization, supported/unsupported versions, missing/invalid tokens, and standards-compliant HTTP authorization failures.

### M02 — Implement core project and document tools

Add `list_projects`, `create_project`, `update_project`, `list_contexts`, `store_context`, `get_context`, `update_context`, `list_document_snapshots`, and `get_document_snapshot` with exact schemas and annotations. The lifecycle tool is deliberately deferred to `L03`, where its underlying policy exists.

- `blocked-by: H03, M01`
- `blocking: M03`
- **Gate:** tool contract tests cover projections, cursors, idempotency, expected snapshots/states, safe errors, and untrusted-content labeling.

### M03 — Certify HTTP/MCP parity

Run identical use-case fixtures through HTTP and MCP and compare policy, state, errors, audit IDs, and redacted outputs.

- `blocked-by: M02`
- `blocking: G02, U02, L03, X03`
- **Gate:** the parity matrix contains no unexplained interface-specific behavior.

## Milestone 7 — Fragment Sets and imports

### G01 — Implement Fragment Set repositories and services

Add draft creation/status, fragment storage, atomic publication, range retrieval, immutable membership/order, set-level lifecycle hooks, abandonment, and expiry eligibility.

- `blocked-by: S05`
- `blocking: G02, G03`
- **Gate:** application/database tests cover interrupted upload, duplicate/missing positions, limits, concurrent publication, updates, and one logical result identity.

### G02 — Expose Fragment Sets through HTTP and MCP

Add HTTP resources and `create_fragment_set`, `get_fragment_set`, `publish_fragment_set`, and `abandon_fragment_set` tools with authorization, cursors/ranges, idempotency, and annotations.

- `blocked-by: G01, H03, M03`
- `blocking: G04`
- **Gate:** cross-interface tests resume and publish the same draft without exposing incomplete content.

### G03 — Implement draft expiry worker

Add retry-safe scheduled cleanup that permanently removes abandoned or 24-hour-expired drafts without creating recoverable deletion state.

- `blocked-by: G01, S04`
- `blocking: G04`
- **Gate:** clock-controlled worker tests cover expiry boundaries, concurrent publication, retries, and backup-visible live drafts.

### G04 — Certify Fragment Set behavior

Run atomicity, concurrency, lifecycle-hook, authorization, size, recovery, and cleanup suites for complete and incomplete sets.

- `blocked-by: G02, G03`
- `blocking: I01, U01`
- **Gate:** every Milestone 7 invariant passes against real PostgreSQL and both public adapters.

### I01 — Implement text and Markdown import services

Add UTF-8 validation, SHA-256 provenance, duplicate warnings, boundary-aware splitting, previews, and confirmed Fragment Set publication.

- `blocked-by: G04`
- `blocking: I02`
- **Gate:** fixture tests cover headings, paragraphs, multibyte boundaries, invalid encodings, duplicates, maximum set size, and exact text preservation.

### I02 — Implement and certify Portal import

Add text/Markdown upload, metadata selection, split preview, duplicate confirmation, publication progress, interruption recovery, and browser tests.

- `blocked-by: I01, P03`
- `blocking: P05`
- **Gate:** browser tests import small and fragmented documents without unsafe rendering or partial publication.

## Milestone 8 — Summary Requests and Derived Summaries

### U01 — Implement Summary Request and Derived Summary services

Add request creation after eligible writes/publication, state transitions, supersession, exact source validation, fixed source sets, access intersection, and multi-summary support.

- `blocked-by: S05, G04`
- `blocking: U02`
- **Gate:** service/database tests cover ordinary, session, whole-set, selected-fragment, multi-source, forbidden-chain, decline, completion, and supersession cases.

### U02 — Expose summary workflows through HTTP and MCP

Return structured requests from writes; add request list/decline endpoints and tools; complete requests through `store_context`; expose safe provenance projections.

- `blocked-by: U01, M03`
- `blocking: U03`
- **Gate:** two Applications can resume the same project request safely, while authorization, idempotency, and one-request/one-completion rules hold.

### U03 — Certify caller-provided summaries

Run end-to-end source storage, request, caller summarization, completion, retrieval, retry, and provenance scenarios across HTTP and MCP.

- `blocked-by: U02`
- `blocking: L01, P04`
- **Gate:** every Summary Request/Derived Summary acceptance criterion has an automated passing scenario.

### P04 — Implement Portal summary and provenance views

Add pending/completed/declined/superseded request views plus source, Derived Summary, stale-state, and replacement relationships.

- `blocked-by: P03, U03`
- `blocking: P05`
- **Gate:** component/browser tests display all request and provenance states without exposing unauthorized source content.

## Milestone 9 — Lifecycle, retention, and purge

### L01 — Implement lifecycle and dependency propagation services

Add reject, reactivate, soft-delete, restore, deadline reset, synchronous summary invalidation/restoration, expected-state conflicts, and Fragment Set propagation.

- `blocked-by: U03`
- `blocking: L02, L03`
- **Gate:** transition-table and concurrent service/database tests prove immediate eligibility changes and valid recovery only.

### L02 — Implement retention and cascading purge worker

Add deadline claims, dependency previews, retry-safe cascading purge, tombstones, content/metadata removal, and hooks for derived-store cleanup.

- `blocked-by: L01, S04`
- `blocking: L04, R03`
- **Gate:** worker tests cover multi-source summaries, duplicate delivery, partial retry, retention boundaries, and terminal tombstones with no retained content.

### L03 — Expose lifecycle through HTTP, MCP, and Portal service endpoints

Add Application lifecycle operations excluding purge, including the MCP `change_context_lifecycle` tool; add Portal recovery/purge endpoints, expected-state/idempotency handling, and dependency-preview responses.

- `blocked-by: L01, M03`
- `blocking: L04`
- **Gate:** interface tests prove rejected visibility, MCP soft-delete invisibility, known-ID restoration, Portal-only purge, and non-enumerating failures.

### L04 — Certify lifecycle safety

Run exhaustive transition, source/summarization, Fragment Set, race, retention, purge, and authorization suites before search indexing begins.

- `blocked-by: L02, L03`
- `blocking: X01, P05, R03`
- **Gate:** no tested event sequence can make ineligible or purged content readable through repositories or services.

## Milestone 10 — Lexical search

### X01 — Implement transactional lexical indexing

Add current-snapshot passage extraction, lexical index tables/configuration, outbox consumers, upsert/removal jobs, index-version state, and idempotent reconciliation.

- `blocked-by: L04, S04`
- `blocking: X02`
- **Gate:** worker tests handle duplicate/out-of-order jobs, source changes, lifecycle cleanup, Fragment Set collapsing, and complete rebuild.

### X02 — Implement lifecycle-safe lexical query service

Add query validation, ranking, excerpts, filters, tag-any/all, time ranges, opaque cursor binding, and authoritative eligibility/authorization rechecks.

- `blocked-by: X01`
- `blocking: X03`
- **Gate:** service tests prove deterministic pagination and immediate exclusion during index lag, authorization changes, and cursor expiry.

### X03 — Expose lexical search through HTTP and MCP

Add search schemas, endpoints, `search_context`, fixed compact result fields, raw-query log redaction, and Portal-consumable indexing state.

- `blocked-by: X02, M03`
- `blocking: X04`
- **Gate:** contract/parity tests cover filters, pagination, excerpts, scores, source/summary coexistence, and safe degraded/error responses.

### X04 — Certify lexical retrieval and rebuilding

Run correctness, drift, lifecycle, concurrency, privacy, and full-rebuild suites against representative documents and Fragment Sets.

- `blocked-by: X03`
- `blocking: V01, V02, P05`
- **Gate:** lexical search remains correct before, during, and after a from-zero index rebuild.

## Milestone 11 — Semantic and hybrid retrieval

### E00 — Assemble multilingual relevance fixtures

Create non-sensitive English, Polish, and cross-language source/query relevance judgments, including paraphrases, distractors, summaries, and multi-topic long documents.

- `blocked-by: none`
- `blocking: E01`
- **Gate:** fixtures have explicit expected relevant/non-relevant documents and can score model output reproducibly.

### E01 — Benchmark and select the PoC embedding model

Benchmark compact CPU-friendly multilingual candidates, passage sizes, overlaps, latency, memory, and retrieval quality against E00; record the decision and model license.

- `blocked-by: E00, D05`
- `blocking: E02`
- **Gate:** one pinned model and passage policy meet documented relevance and resource thresholds on representative hardware.

### E02 — Implement the isolated embedding provider

Build the internal-only, resource-limited model container and replaceable provider adapter with health, timeout, batching, and safe failure behavior.

- `blocked-by: E01, F05`
- `blocking: V01, O02`
- **Gate:** provider contract tests pass for normal, slow, unavailable, malformed, and restarted model service states.

### V01 — Implement vector indexing and model versions

Add pgvector schema, versioned embeddings, semantic job consumers, partial-state tracking, parallel rebuild, and atomic active-version switching.

- `blocked-by: E02, X04`
- `blocking: V02`
- **Gate:** integration tests rebuild a new model version without disrupting the active index or durable writes.

### V02 — Implement semantic and hybrid ranking

Add semantic queries, hybrid fusion, document deduplication, `prefer_summaries`, optional diagnostic scores, lexical degradation, and semantic partial-result signaling.

- `blocked-by: V01, X04`
- `blocking: V03`
- **Gate:** relevance, lifecycle, authorization, pagination, provider-outage, and source/summary ranking tests pass.

### V03 — Certify multilingual hybrid retrieval

Run benchmark thresholds, API/MCP parity, model loss, complete re-index, performance, and resource-envelope tests.

- `blocked-by: V02`
- `blocking: P05, O03, R01`
- **Gate:** English, Polish, and cross-language acceptance queries pass and model/index loss is recoverable without document loss.

## Milestone 12 — Complete Portal and audit workflows

### O01 — Implement audit and operational telemetry foundations

Emit safe audit events, metrics, and indexing/job status from existing services; add redaction tests and query/content/token leak detection.

- `blocked-by: F05, S04`
- `blocking: O02, P05`
- **Gate:** every implemented state-changing workflow emits the required safe audit event and telemetry redaction tests pass.

### P05 — Complete lifecycle, search, import, summary, and audit UI

Integrate rejected review, recovery, purge preview/typed confirmation, lexical/hybrid search, filters, indexing state, summary relationships, imports, and the audit viewer.

- `blocked-by: I02, P04, L04, X04, V03, O01`
- `blocking: P06`
- **Gate:** all README Portal pages and their loading/empty/error/conflict/degraded states have browser coverage.

### P06 — Certify the complete Portal

Run full browser journeys, accessibility checks, session/security regressions, responsive smoke tests, and API-only-policy verification.

- `blocked-by: P05`
- `blocking: O03, R01`
- **Gate:** critical journeys pass without privileged database or internal-service access.

## Milestone 13 — Operational and security hardening

### Q00 — Create the security threat model

Document assets, trust boundaries, attacker-controlled inputs, authorization boundaries, destructive actions, backup exposure, and required security tests before sensitive implementation begins.

- `blocked-by: none`
- `blocking: A01, P03, O02`
- **Gate:** the threat model covers Portal, OAuth, MCP, API, worker, database, embedding service, reverse proxy, NAS, and restore paths.

### O02 — Implement limits, retries, and security hardening

Add per-Application and OAuth rate limits, upload concurrency limits, payload/time/resource bounds, retry/backoff/dead-letter controls, graceful shutdown, capacity alerts, and fixes from security review.

- `blocked-by: A03, E02, O01, Q00`
- `blocking: O03`
- **Gate:** abuse/failure tests prove bounded work, safe recovery, immediate authorization enforcement, and no sensitive telemetry.

### O03 — Certify concurrency, security, and expected load

Run authorization, OAuth, CSRF, XSS, SSRF, SQL injection, deserialization, log-leakage, race, duplicate-job, and 10,000-document load suites.

- `blocked-by: O02, P06, V03`
- `blocking: R01`
- **Gate:** no critical/high issue remains, all races preserve invariants, and the system stays within the reserved resource envelope.

## Milestone 14 — Production deployment and recovery

### R00 — Inventory production host and recovery dependencies

Record host OS/architecture, shared Caddy ownership, `/d` routing constraints, DNS/base URL, available CPU/RAM/disk, Tailscale/NAS path, container registry, and deployment credentials needed later.

- `blocked-by: none`
- `blocking: R01, R03`
- **Gate:** the inventory contains no secrets but identifies every required external dependency and owner-provided value.

### R01 — Build hardened production containers and shared-Caddy integration

Create pinned non-root images, production Compose networks/volumes/limits/health checks, mounted-secret validation, canonical URL handling, and the host Caddy route/discovery snippet.

- `blocked-by: R00, V03, P06, O03`
- `blocking: R02, R03`
- **Gate:** an isolated production-like host exposes only Caddy, routes every `/d` and discovery endpoint correctly, and enforces container limits.

### R02 — Implement the approval-gated release pipeline

Build/sign/version images in CI; implement pull, migration preflight, rollout, health verification, failure rollback, and release evidence capture.

- `blocked-by: R01`
- `blocking: R04`
- **Gate:** a deliberately broken release rolls back automatically while the previous version remains usable.

### R03 — Implement and exercise backup/restore

Create consistent PostgreSQL dumps, encrypted Restic transfer over Tailscale, 30-day NAS retention, seven-local-backup outage buffering, disk floors, alerts, secret-recovery instructions, purge replay, and index rebuild.

- `blocked-by: R00, R01, L02, L04`
- `blocking: R04`
- **Gate:** an isolated destructive restore recovers authoritative data, reapplies tombstones before opening, and rebuilds all indexes.

### R04 — Certify the production deployment

Deploy behind the real shared Caddy, validate OAuth/OIDC callbacks and MCP discovery, exercise restart/rollback/backup/restore/re-index, and capture operational evidence.

- `blocked-by: R02, R03`
- `blocking: Z01`
- **Gate:** the deployed service survives the complete production runbook with no undocumented manual repair.

## Milestone 15 — Production PoC acceptance

### Z01 — Execute and sign off the PoC acceptance matrix

Run the complete cross-session scenario with at least three differently authorized Applications; verify imports, summaries, multilingual hybrid search, concurrency, rejection/restoration, soft deletion, cascading purge, audits, telemetry privacy, backup restore, and resource usage. Reconcile README, CONTEXT, OpenAPI, MCP schemas, and observed behavior.

- `blocked-by: R04`
- `blocking: none`
- **Gate:** every README success criterion links to passing automated evidence or a recorded production verification, and the owner explicitly accepts the PoC.

## Milestone completion mapping

| Milestone | Complete when |
| --- | --- |
| 0 | `F01`–`F05` complete |
| 1 | `D01`–`D05` complete |
| 2 | `S01`–`S05` complete |
| 3 | `C00`, `C01`, and `H01`–`H03` complete |
| 4 | `P01`–`P03` complete |
| 5 | `A01`–`A03` complete |
| 6 | `M01`–`M03` complete |
| 7 | `G01`–`G04` and `I01`–`I02` complete |
| 8 | `U01`–`U03` and `P04` complete |
| 9 | `L01`–`L04` complete |
| 10 | `X01`–`X04` complete |
| 11 | `E00`–`E02` and `V01`–`V03` complete |
| 12 | `O01` and `P05`–`P06` complete |
| 13 | `Q00` and `O02`–`O03` complete |
| 14 | `R00`–`R04` complete |
| 15 | `Z01` complete |
