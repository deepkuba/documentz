# Documentz Security Threat Model

## Purpose and scope

This model covers the production proof of concept described by `README.md`,
`CONTEXT.md`, and `IMPLEMENTATION_PLAN.md`. It is the baseline for design and
security reviews, not proof that a later implementation is secure. Every slice
that changes an asset, boundary, data flow, privilege, or destructive action
must update this document and its security tests.

The deployment serves one owner and several independently authorized
Applications. The host, owner-operated deployment tooling, and root-owned
secret files are trusted administratively. Application clients, browsers,
document content, metadata, search text, imported files, OAuth/OIDC messages,
network traffic, job payloads, model responses, backups in transit, and restored
data are untrusted until authenticated and validated. A compromised authorized
Application remains constrained to its granted scopes and Personal Projects.

## Assets

| Asset | Security property |
| --- | --- |
| Context Documents, snapshots, fragments, summaries, metadata, tags, excerpts, embeddings, and provenance | Confidentiality; project isolation; integrity; lifecycle eligibility; complete purge |
| Owner identity and Portal session | Strong OIDC binding; allowlisting; fixation/replay resistance; timely logout and expiry |
| Application registrations and authorizations | Exact redirect and project/scope integrity; explicit consent; immediate revocation |
| Authorization codes, access/refresh tokens, client secrets, cookies, and encryption material | Confidentiality; hashes at rest where specified; rotation; replay resistance; absence from telemetry |
| PostgreSQL authoritative state, migrations, outbox, jobs, idempotency records, audits, and purge tombstones | Integrity; availability; transactionality; append-only audit behavior; retry safety |
| Search indexes and embedding vectors | Confidentiality; model/version integrity; rebuildability; never authoritative for access |
| Backups, retained local backup buffer, restore configuration, and NAS copies | Confidentiality; integrity; recoverability; retention and purge replay |
| Service availability and shared-host resources | Bounded CPU, memory, disk, request size, retries, and concurrency |
| Logs, metrics, traces, errors, and audit views | Operational usefulness without content, queries, credentials, codes, or secrets |

## Security objectives and non-goals

- Deny access unless the current User, Application Authorization, scope, and
  explicit Personal Project grant permit the operation.
- Never reveal through status, timing, errors, cursors, counts, or search results
  whether an unauthorized project or document exists.
- Return ordinary content only when it is active, current, published, authorized,
  and—where applicable—fresh. PostgreSQL rechecks this after candidate search.
- Preserve immutable history and provenance while preventing stale or purged
  material from leaking through caches, queues, indexes, backups, or derived data.
- Keep all supplied content untrusted; it is data and never an instruction to an
  agent, renderer, worker, embedding model, or operator.
- Keep secrets and sensitive content out of source control and telemetry.

Protection against a malicious host root administrator, a malicious NAS
administrator holding both backup data and its separately stored decryption
material, hardware attacks, and high availability are outside the PoC scope.
Their residual risk must be recorded in production review rather than silently
treated as solved.

## Trust boundaries and data flows

Each row is a boundary where authentication, validation, minimization, and safe
failure must be tested. Internal network placement alone is not authorization.

| Boundary | Untrusted flow | Required controls and safe failure |
| --- | --- | --- |
| **Management Portal** browser ↔ service | OIDC responses, cookies, form fields, Markdown/text import, search, lifecycle and purge requests | Allowlisted issuer/subject; server-side Secure/HttpOnly/SameSite session; rotation/expiry; CSRF and same-origin enforcement; CSP and safe rendering; typed destructive confirmation; same policy layer as public clients |
| **OAuth and OIDC** provider/client ↔ authorization endpoints | Discovery documents, redirect URIs, state, nonce, authorization codes, PKCE values, client credentials, tokens, consent changes | Exact redirect matching; PKCE S256; state/nonce binding; short-lived single-use codes; hashed opaque tokens/secrets; rotating refresh tokens with reuse revocation; renewed consent for expansion; no open redirects |
| **MCP adapter** ↔ Application | Protocol negotiation, bearer token, tool names/arguments, cursors, idempotency keys, returned content | Standards-compliant HTTP challenge; schema/size validation; project/scope enforcement; identical domain policy/error mapping to HTTP; expected state/snapshot checks; label returned content as untrusted |
| **HTTP API** ↔ Application or Portal | Paths, headers, bearer tokens, JSON, filters, cursors, ETags, idempotency keys | Versioned schemas; bounded inputs; authentication before lookup disclosure; non-enumerating errors; projections; opaque authorization-bound cursors; `If-Match`; replay-safe idempotency |
| API/application services ↔ **PostgreSQL database** | Queries, transaction values, migration state, concurrent writes | Parameterized access; least-privilege database role; constraints; unit of work; optimistic concurrency; database is authoritative; private network; encrypted/controlled storage; tested migrations |
| Application services ↔ **background worker** through outbox/jobs | Job types and payloads, retries, stale/duplicate delivery, lifecycle races | Transactional enqueue; authenticated/allowlisted job types; minimal identifiers rather than content; retry limits/backoff/dead letter; idempotent claims/handlers; current eligibility and authorization-state rechecks |
| Worker ↔ **embedding service** | Document passages, model/version selection, responses, timeouts and malformed vectors | Private network; strict size/type/dimension checks; resource/time limits; bounded retry/circuit breaking; no credentials or instructions; durable writes survive outage; vectors remain derived |
| Internet ↔ **shared Caddy reverse proxy** ↔ containers | TLS traffic, forwarded headers, host/path, request bodies, discovery routes | TLS; canonical host/base URL; trusted proxy configuration; `/d` and discovery allowlist; request/body/rate limits; strip untrusted forwarding headers; expose only Caddy; private service networks |
| Backup process ↔ Tailscale ↔ **NAS backup target** | Encrypted PostgreSQL dumps/configuration, repository metadata, retention and transfer status | Encryption before transfer; separate key recovery; authenticated Tailscale path; integrity verification; least NAS permissions; 30-day retention; bounded local fallback; alerts; no vectors required |
| Backup/NAS ↔ isolated **restore environment** ↔ production | Potentially stale or tampered dumps, configuration and purge tombstones | Isolated destructive rehearsal; verify/decrypt; restore authoritative data; replay purge tombstones before readiness; rebuild indexes; validate configuration/secrets separately; health gate before traffic |

### Principal data flows

1. The owner authenticates through OIDC, receives a server-side Portal session,
   and uses the Portal through Caddy and the HTTP API.
2. The owner registers an Application and approves fixed scopes and explicit
   Personal Projects. OAuth issues short-lived access and rotating refresh tokens.
3. An Application calls HTTP or MCP through Caddy. Both adapters create the same
   authenticated request context and invoke the same services and policy layer.
4. A write commits authoritative state plus outbox/job records atomically.
   Workers consume minimal job data and call the internal embedding service.
5. Search obtains lexical/vector candidates, then PostgreSQL rechecks current
   authorization, publication, lifecycle, snapshot, and summary freshness.
6. Backup tooling encrypts consistent authoritative dumps before Tailscale/NAS
   transfer. Restore remains unavailable until tombstones replay and indexes rebuild.

## Threat actors and abuse cases

- An unauthenticated internet attacker probes routes, discovery, identifiers,
  parsers, request limits, login callbacks, and error/timing differences.
- A malicious or compromised Application replays tokens/idempotency keys, expands
  scopes, guesses cross-project IDs, poisons content, or races lifecycle updates.
- A malicious web origin attempts CSRF, CORS abuse, clickjacking, session fixation,
  reflected/stored XSS, unsafe Markdown, or OAuth redirect manipulation.
- Crafted content attempts prompt injection, HTML/script execution, parser abuse,
  SQL injection, log forging, denial of service, or embedding-resource exhaustion.
- Duplicate, stale, reordered, or poisoned jobs try to restore ineligible content
  to search or cause repeated destructive work.
- A network attacker targets forwarded headers, TLS assumptions, internal service
  exposure, backup transfer, OAuth/OIDC metadata, or dependency traffic.
- An operator mistake deploys wrong paths/secrets, exposes a port, restores stale
  data, skips purge replay, retains backups too long, or logs sensitive values.
- A compromised dependency, container, CI job, registry artifact, or backup target
  attempts code execution, secret theft, or artifact substitution.

## Attacker-controlled inputs

| Input | Validation/handling requirement |
| --- | --- |
| Document titles/content, tags, custom metadata/kinds, summary sources, fragment descriptors, imported text/Markdown | UTF-8 byte/count/depth limits; exact domain validation; safe rendering/encoding; immutable ownership/kind/origin rules; content never logged or executed |
| Project/Application names, redirect URIs, requested scopes/projects, OAuth/OIDC parameters | Length/format allowlists; exact redirect matching; canonical issuer and base URL; consent bound to the exact request |
| IDs, paths, filters, projections, ranges, cursors, ETags, expected states/snapshots | Opaque parsing; strict enum/range limits; authorization before disclosure; cursor binding; optimistic concurrency |
| Authorization headers, cookies, codes, tokens, client secrets, PKCE, state and nonce | Bounded parsing; constant-time secret comparison where applicable; one-time/expiry/replay rules; redaction from all outputs and telemetry |
| Idempotency keys and request IDs | Bounded safe format; authenticated-operation binding; conflict detection; server-generated request IDs when invalid |
| Search queries and embedding passages/results | Size/rate limits; query parameterization; no logs/audits; vector type/dimension/model validation; eligibility recheck |
| HTTP headers, forwarded headers, host/origin, content types, compressed/request bodies | Caddy trust allowlist; canonical host; origin policy; body/decompression limits; reject ambiguous encodings and unsupported media |
| Job records and restored database/backup data | Allowlisted versioned job schema; idempotency; integrity checks; migration compatibility; tombstone replay; no readiness until verified |

## Authorization boundaries

- The single human User is authenticated separately from an Application. A Portal
  session is not an unrestricted database administrator and uses public rules.
- Every Application Authorization combines immutable approved operation scopes
  with explicit Personal Project IDs. Expanding either requires renewed consent;
  revocation takes effect for already issued tokens immediately.
- Project creation by an authorized Application may add only the newly created
  project to that same authorization. It cannot select unrelated projects.
- Unknown and unauthorized identifiers return indistinguishable responses.
- Permanent purge, soft-deleted browsing, audit access, and destructive project
  removal are Portal-only. MCP and public Application operations cannot acquire
  these capabilities through a broader input value.
- Workers and indexes carry no independent user authority. They re-evaluate the
  authoritative current state and cannot make content retrievable.
- A Derived Summary is usable only when all exact source snapshots are current,
  active, same-project, non-Derived sources and their access intersection permits it.
- Historical snapshots, draft Fragment Sets, rejected documents, soft-deleted
  documents, stale summaries, and purged data never enter ordinary retrieval.

## Destructive actions

| Action | Threat | Required safeguard |
| --- | --- | --- |
| Reject/reactivate | Incorrect or raced eligibility change | Authorized lifecycle scope; expected current state/snapshot; atomic propagation; audit without content |
| Soft-delete/restore | Data hidden/restored by stale request or wrong principal | Portal/policy authorization; recovery deadline; concurrency check; immediate search eligibility recheck |
| Permanent purge | Irreversible unintended loss, incomplete cascade, resurrection from retry/restore | Portal-only dependency preview; explicit typed confirmation; idempotent transaction/job; tombstone retained without content; cascade sources/summaries/fragments/indexes/caches; backup restore replay |
| Abandon/expire Fragment Set | Published or another owner's data removed | Writer authorization; draft-only invariant; age/state check; idempotent worker |
| Revoke Application/authorization or rotate credentials | Existing token remains effective or valid client is locked out | Immediate authoritative revocation check; refresh-reuse response; explicit owner action; safe audit and recovery path |
| Archive/remove project | Cross-project or accidental broad destruction | Portal-only destructive removal where applicable; impact preview; exact project binding; typed confirmation; dependency checks |
| Migration/deploy/rollback | Schema/data corruption or incompatible rollback | Tested forward migration; explicit rollback decision point; backup; health gate; no unsafe automatic database downgrade |
| Backup retention/restore | Required recovery lost or erased content resurrected | Retention policy and alerts; separate key recovery; isolated rehearsal; tombstone replay before readiness |

## Backup and restore exposure

Backups contain sensitive authoritative state, including content and hashed
credentials. They are encrypted before leaving the host and travel only through
the authenticated Tailscale path to the NAS backup target. The NAS account gets
only the required repository permissions. Encryption keys and recovery material
are stored and tested separately from the repository and backup destination;
neither values nor recovery answers appear in this repository, telemetry, or issue
comments.

Failed NAS transfers may retain at most the planned bounded local encrypted
buffer, subject to a disk floor and alerting. Remote retention is 30 days. Backup
logs expose status, sizes, safe identifiers, and timings—not filenames derived
from content, queries, plaintext, secrets, or tokens. Integrity checks and restore
drills detect truncation, tampering, wrong keys, incompatible migrations, and
missing configuration.

A restore occurs in an isolated restore environment. It must restore PostgreSQL,
apply compatible migrations, replay every purge tombstone that postdates or is
otherwise required for the restored snapshot, and rebuild lexical/vector indexes.
External readiness stays false until lifecycle and authorization checks pass.
Restored tokens/secrets remain subject to expiry/revocation; separately managed
production secrets are re-provisioned rather than recovered from source control.

Residual exposure: any retained backup can contain data that was live when the
backup was taken. Tombstone replay prevents service-level resurrection after
restore, while encryption, retention, access control, and eventual expiry bound
offline copies. Physical destruction guarantees depend on the host/NAS provider.

## Required security tests

Each requirement names an observable boundary; implementation slices add the
test at the closest public seam and retain it in CI.

### Identity, browser, OAuth, and session

- Reject an authenticated OIDC subject or issuer outside the owner allowlist.
- Cover login state/nonce, callback failure, fixation, rotation, expiry, logout,
  Secure/HttpOnly/SameSite cookie scope, CSRF, same-origin CORS, and clickjacking.
- Prove stored/reflected Markdown and metadata cannot execute script.
- Test exact redirect matching, PKCE downgrade, code replay/expiry, consent request
  binding, scope/project expansion, hashed credentials, refresh rotation/reuse,
  revocation, and discovery paths under the configured `/d` base URL.

### Authorization and interface parity

- Exercise every scope against granted, ungranted, archived, unknown, and revoked
  projects; unauthorized and nonexistent resources must be indistinguishable.
- Prove existing access tokens stop working immediately after authorization,
  Application, scope, or project revocation.
- Run identical use cases through HTTP and MCP and compare state, policy, stable
  errors, projections, audit IDs, and redaction.
- Verify permanent purge, soft-deleted browsing, audit access, and destructive
  project removal cannot be invoked through Application HTTP or MCP.

### Input, content, and protocol safety

- Test UTF-8 byte and collection/depth limits, malformed JSON/UTF-8, oversized and
  compressed bodies, unsafe deserialization, SQL injection, header ambiguity,
  cursor tampering/expiry, SSRF inputs, redirect attacks, and rate/resource limits.
- Test Markdown/HTML sanitization and mark retrieved content as untrusted data.
- Fuzz HTTP/MCP schemas, OAuth parameters, cursor envelopes, import splitting,
  fragment positions, metadata, and embedding response dimensions/types.

### Lifecycle, concurrency, jobs, and search

- Race snapshot updates, Fragment Set publication, summary completion, reject,
  restore versus purge, revocation, and duplicate jobs using real PostgreSQL.
- Prove rejection, deletion, source supersession, revocation, and purge disappear
  from retrieval immediately even with stale indexes or delayed cleanup.
- Exercise retry/dead-letter limits, poison messages, stale/duplicate delivery,
  atomic outbox creation, idempotent cascade, and graceful worker shutdown.
- Confirm a failed/slow/malformed embedding service cannot block durable writes,
  exhaust workers, expose content, or prevent lexical degraded search.

### Telemetry, supply chain, deployment, and recovery

- Seed sentinel content, query, code, token, secret, cookie, and metadata values;
  assert none appears in logs, metrics, traces, errors, audits, CI artifacts, or
  backup status output.
- Run dependency, lockfile, container, secret, and image vulnerability/integrity
  scans; pin images/dependencies according to the foundation ADRs.
- Verify only Caddy is public; direct database/embedding/API/worker access fails;
  spoofed forwarded headers and invalid host/base paths are rejected.
- Test request, CPU, memory, disk, queue, retry, and concurrency exhaustion with
  alerts and bounded degradation.
- Perform an isolated destructive restore from encrypted NAS data, including
  corrupted/wrong-key failures, migration compatibility, purge replay before
  readiness, authorization checks, and complete index rebuild.

## Security review workflow

Perform focused security review before merging the OAuth/authorization,
lifecycle/purge, semantic retrieval, operational hardening, and production
deployment slices identified in `IMPLEMENTATION_PLAN.md`. Also review any change
that introduces or changes a boundary listed here.

The review records:

1. assets, actors, trust boundaries, data flows, and assumptions changed;
2. authorization and Personal Project isolation checks;
3. attacker-controlled inputs, parsing, output encoding, and resource bounds;
4. secret/token storage, rotation, transport, and telemetry redaction;
5. destructive/race/retry behavior, rollback, backup, and restore consequences;
6. exact security tests and commands run, failures and resolutions, residual
   risks, owner decisions, and follow-up issue links.

Release-blocking findings remain open until fixed and re-tested. Accepted
residual risk requires explicit owner sign-off and a linked issue; it is never
silently converted into an implementation assumption.
