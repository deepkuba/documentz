# Production and recovery inventory

This is the non-secret handoff contract for the Documentz production PoC. It
records every external value or dependency required by deployment and recovery.
It does not claim that the production environment exists or is ready.

**Inventory structurally complete:** Yes

**Deployment ready:** No

The owner must supply and verify every `owner-required` row. A later implementation
task must create and verify every `dependent-task` row. A `confirmed` row records a
project constraint already fixed by repository documentation; it does not confirm
that a host currently satisfies that constraint.

Status meanings:

- `confirmed` — a non-secret design value is fixed by README/implementation plan.
- `owner-required` — the production owner must provide and verify the value.
- `dependent-task` — a named later task must create the artifact or evidence.

Never add passwords, tokens, private keys, recovery phrases, credential contents,
or secret-manager exports here. Secret rows identify only purpose, custodian, and
the location or mechanism from which runtime mounts obtain a secret.

## Host and capacity

| Item | Non-secret value or requirement | Status | Owner/provider | Source of truth / location | Verification method | Collection or next action |
| --- | --- | --- | --- | --- | --- | --- |
<!-- inventory:host-provider -->
| Host provider and instance identifier | Owner-provided provider name and non-secret instance ID | `owner-required` | Production owner / hosting provider | Provider console inventory | Match console ID to `hostnamectl` identity without copying account data | Owner records provider and instance ID before R01 |
<!-- inventory:host-os -->
| Host operating system | Owner-provided supported Linux distribution and release | `owner-required` | Host administrator | `/etc/os-release` on production host | `cat /etc/os-release` and record only distribution/version | Host administrator captures OS name and release |
<!-- inventory:host-architecture -->
| Host architecture | Owner-provided architecture supported by built images | `owner-required` | Host administrator | Production kernel/hardware inventory | `uname -m`; compare with R01 image platforms | Record architecture before image selection |
<!-- inventory:host-cpu -->
| Available CPU | At least the documented 4-core reserved envelope; actual allocatable count owner-provided | `owner-required` | Host administrator | Host capacity plan and production scheduler | `nproc`; confirm four cores can be reserved after existing workloads | Record total and reserved CPU, then resolve any shortfall |
<!-- inventory:host-memory -->
| Available memory | At least the documented 16 GiB reserved envelope; actual allocatable memory owner-provided | `owner-required` | Host administrator | Host capacity plan | `free -h`; confirm 16 GiB can be reserved after existing workloads | Record total/reserved memory and headroom |
<!-- inventory:host-disk -->
| Available persistent disk | At least the documented 100 GB NVMe envelope; mount, filesystem, and free bytes owner-provided | `owner-required` | Host administrator | Host storage inventory | `lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS` and `df -h`; verify persistent NVMe-backed target | Record mount and capacity without device credentials |
<!-- inventory:host-administrator -->
| Host administrator | Owner-provided accountable person/team and escalation channel | `owner-required` | Production owner | Operations ownership register | Named owner acknowledges patching, capacity, restart, and incident duties | Record role/contact in private operations register; link its non-secret location here |

The 4 CPU / 16 GiB / 100 GB values are reservation targets, not observed host
facts. Capacity remains unverified until the commands above are run on the target.

## Shared Caddy, routing, DNS, and TLS

| Item | Non-secret value or requirement | Status | Owner/provider | Source of truth / location | Verification method | Collection or next action |
| --- | --- | --- | --- | --- | --- | --- |
<!-- inventory:shared-caddy-owner -->
| Shared Caddy owner | Owner-provided person/team controlling host Caddy and public ports | `owner-required` | Production owner | Host reverse-proxy operations register | Owner confirms change/reload/rollback authority | Record accountable owner and escalation location |
<!-- inventory:shared-caddy-config -->
| Shared Caddy configuration | Owner-provided absolute include/site-file location and reload mechanism | `owner-required` | Shared Caddy owner | Host Caddy service definition and configuration tree | `systemctl cat caddy` plus `caddy validate --config <owner-provided-path>` | Record path and safe validate/reload command; never copy unrelated site secrets |
<!-- inventory:public-port-ownership -->
| Public ports | Only shared host Caddy owns public 80/443; application containers remain private | `confirmed` | Shared Caddy owner | README security posture; R01 Compose/Caddy evidence | `ss -ltnp` on host and external port scan during R01 | R01 captures evidence that no application/database/model port is public |
<!-- inventory:route-prefix -->
| Application route prefix | `/d`: Portal `/d/`, API `/d/api/v1/`, MCP `/d/mcp`, OAuth `/d/oauth/` | `confirmed` | Documentz release owner | README production paths | R01 route smoke tests through Caddy | Preserve prefix and forwarded path in every generated URL |
<!-- inventory:discovery-routes -->
| Standards discovery routes | OAuth authorization-server and protected-resource metadata routes required by the selected OAuth/MCP integration | `dependent-task` | R01/A01 implementers and Caddy owner | A01 protocol ADR plus R01 Caddy snippet | Reference-client discovery tests from the public origin | A01 fixes exact paths; R01 routes them without redirect/path rewriting errors |
<!-- inventory:dns-owner -->
| DNS owner/provider | Owner-provided DNS provider, zone owner, and change/rollback contact | `owner-required` | Production owner / DNS provider | DNS zone management register | Provider console plus authoritative `dig` response | Record provider/zone/contact only; do not record account credentials |
<!-- inventory:dns-name -->
| Production DNS name | Owner-provided fully qualified host name | `owner-required` | DNS owner | Authoritative DNS zone | `dig +short A <name>` and/or `AAAA`; compare with target ingress | Owner allocates name and confirms propagation before OIDC/OAuth registration |
<!-- inventory:canonical-base-url -->
| Canonical external base URL | `https://<owner-provided-dns-name>/d`; exact value owner-provided after DNS allocation | `owner-required` | Production owner | Mounted non-secret production configuration | Startup validation plus external URL-generation and callback tests | Record exact HTTPS `/d` URL; use one normalized form without a conflicting alias |
<!-- inventory:tls-owner -->
| TLS certificate ownership | Owner-provided issuer/automation mechanism and renewal owner; private key value excluded | `owner-required` | Shared Caddy owner | Caddy TLS configuration and certificate automation state | External TLS probe, expiry check, and renewal dry run | Record issuer/mechanism and alert owner, never key material |

Routing constraints: preserve the external scheme/host/prefix through trusted
forwarded headers; do not expose upstream ports; do not strip `/d` inconsistently;
set request limits at Caddy and application layers; validate configuration before
reload and retain a rollback copy under the Caddy owner's normal process.

## Tailscale and NAS backup destination

| Item | Non-secret value or requirement | Status | Owner/provider | Source of truth / location | Verification method | Collection or next action |
| --- | --- | --- | --- | --- | --- | --- |
<!-- inventory:tailscale-tailnet -->
| Tailscale network | Owner-provided tailnet name/organization and network owner; auth material excluded | `owner-required` | Network owner | Tailscale admin console | `tailscale status` and admin-console device check | Record tailnet label and accountable owner only |
<!-- inventory:tailscale-host-identity -->
| Production host Tailscale identity | Owner-provided stable device name and approved tags/ACL role | `owner-required` | Network owner / host administrator | Tailscale device inventory and ACL policy | `tailscale status --json` inspected locally; ACL connectivity test to NAS | Enroll host through approved mechanism; do not record reusable auth keys |
<!-- inventory:nas-owner -->
| NAS owner | Owner-provided administrator and recovery escalation contact | `owner-required` | Production owner | Private operations ownership register | Owner acknowledges storage, retention, capacity, and restore support | Link non-secret register location and escalation procedure |
<!-- inventory:nas-endpoint -->
| NAS endpoint | Owner-provided Tailscale DNS name or stable tailnet address; no public endpoint | `owner-required` | NAS owner / network owner | NAS and Tailscale inventories | Resolve over tailnet and perform authorized connection health check | Record endpoint only after ACL-restricted reachability is verified |
<!-- inventory:nas-backup-path -->
| NAS backup repository path | Owner-provided dedicated Restic repository location; credential excluded | `owner-required` | NAS owner / backup operator | NAS storage allocation record and Restic non-secret config | `restic snapshots` using mounted credentials; verify repository identity and write/read/delete test fixture | Allocate isolated path with quota; do not reuse an unrelated repository |
<!-- inventory:nas-retention -->
| Remote retention | 30 days | `confirmed` | Backup operator / NAS owner | README and implementation plan | R03 retention-policy dry run followed by snapshot listing | R03 implements and records prune policy without deleting the only verified recovery point |

## Container registry and release inputs

| Item | Non-secret value or requirement | Status | Owner/provider | Source of truth / location | Verification method | Collection or next action |
| --- | --- | --- | --- | --- | --- | --- |
<!-- inventory:container-registry -->
| Container registry | Owner-provided registry hostname/provider supporting immutable versioned images | `owner-required` | Release owner / registry provider | Registry organization settings | Anonymous metadata probe where supported, authenticated push/pull with test image in isolated namespace | Select provider and record hostname, retention, and availability owner |
<!-- inventory:registry-namespace -->
| Registry namespace | Owner-provided organization/repository prefix for API, worker, Portal, and embedding images | `owner-required` | Release owner | Registry repository inventory | Confirm repositories exist and immutable tag/digest policy is enabled | Allocate least-privilege repositories before R02 |
<!-- inventory:registry-publish-identity -->
| Registry publisher credential | CI identity name, secret-store reference, scopes, and rotation owner only | `owner-required` | CI/release owner | CI environment/secret manager metadata | Publish and sign a disposable test image; inspect scopes without printing credential | Create write-only CI identity scoped to Documentz repositories |
<!-- inventory:registry-pull-identity -->
| Registry pull credential | Production identity name, mounted/managed location, scopes, and rotation owner only | `owner-required` | Host administrator / registry owner | Host credential helper or root-owned secret reference | Pull by digest as deployment user; verify it cannot push | Create read-only identity and document rotation/revocation |

## Deployment ownership and credentials

| Item | Non-secret value or requirement | Status | Owner/provider | Source of truth / location | Verification method | Collection or next action |
| --- | --- | --- | --- | --- | --- | --- |
<!-- inventory:deployment-operator -->
| Deployment operator | Owner-provided person/team responsible for release, rollback, and evidence | `owner-required` | Production owner | Private operations ownership register | Operator acknowledges R02 approval and rollback duties | Record role/contact and backup operator |
<!-- inventory:deployment-access -->
| Deployment host access | Identity name, access mechanism, privilege boundary, revocation owner; no SSH key/token value | `owner-required` | Host administrator | SSH/identity-provider policy and sudo configuration | Login and least-privilege preflight as deployment identity; review effective sudo rules | Provision dedicated identity with auditable access and documented revocation |
<!-- inventory:deployment-approval -->
| Production approval authority | Owner-provided approver role and CI environment/rule location | `owner-required` | Production owner / release owner | Repository/CI protected-environment settings | Attempt a no-op release and confirm approval gate blocks until authorized | Configure named approval and emergency rollback authority before R02 |
<!-- inventory:production-config-location -->
| Non-secret production configuration | Owner-provided absolute directory, ownership, mode, and configuration owner | `owner-required` | Host administrator / release owner | Production host configuration directory | `stat` names/modes and startup config validation; do not dump adjacent secrets | Allocate versioned or change-controlled non-secret config location |
<!-- inventory:mounted-secret-directory -->
| Mounted secret directory | Owner-provided absolute directory or secret-mount mechanism; root-owned and unreadable by unrelated users | `owner-required` | Host administrator / secret custodian | Host mount/service definition | `stat` directory/files, access tests as service and unrelated user; never `cat` values | Allocate secret files with one purpose per file and documented rotation |
<!-- inventory:database-credential -->
| PostgreSQL runtime credentials | Separate API and worker role names (or an explicit, reviewed decision to share), secret references, scopes, rotation and recovery owners only | `owner-required` | Database/secret custodian | Mounted secret metadata and PostgreSQL role catalog | Connect as each runtime role; verify only required DML/job privileges and denied schema/superuser capabilities | Define the API/worker role boundary, generate credentials, and document rotation without recording values |
<!-- inventory:database-migration-credential -->
| PostgreSQL migration credential | Dedicated role and secret reference with schema-migration privileges, unavailable to API and worker runtimes | `owner-required` | Database/secret custodian / release owner | Release secret metadata and PostgreSQL role catalog | Apply migrations as release identity; prove runtime identities cannot perform DDL or assume the role | Provision only to the gated migration step and document rotation/revocation |
<!-- inventory:database-backup-credential -->
| PostgreSQL backup credential | Dedicated role and secret reference with the minimum consistent-dump privileges, unavailable to application containers | `owner-required` | Database/secret custodian / backup operator | Backup service secret metadata and PostgreSQL role catalog | Produce and restore a consistent disposable dump; prove the role cannot mutate application data or perform DDL | Provision to the root-owned backup service and document rotation/revocation |
<!-- inventory:oidc-credential -->
| OIDC client credential | Provider registration ID, secret reference, redirect/base URL binding, rotation owner; secret value excluded | `owner-required` | Identity owner / OIDC provider | Provider application registration and mounted secret metadata | Complete test login for allowlisted owner and reject mismatched subject/redirect | Register after canonical base URL is fixed; store secret only in approved secret location |
<!-- inventory:oauth-signing-key -->
| OAuth signing/encryption key material | Key identifier/reference, algorithm policy, custodian, rotation and recovery procedure only | `dependent-task` | A01/A02 implementer and secret custodian | Selected OAuth library ADR and mounted secret metadata | Protocol tests plus key-rotation rehearsal without logging/exporting key | A01 determines exact key purposes; custodian creates and escrows them |
<!-- inventory:session-signing-key -->
| Portal session key material | Secret reference, custodian, rotation and invalidation procedure only | `dependent-task` | P01 implementer and secret custodian | Session design and mounted secret metadata | Session issuance/rotation/logout tests; secret-leak scan | P01 fixes exact requirement; custodian provisions independent key material |

Deployment credentials are separate identities: registry publisher, registry puller,
host deployer, database runtime, migration, and backup roles, OIDC client, and
cryptographic keys must not share a reusable credential. Every credential requires
least privilege, rotation, revocation, and an accountable custodian.

## Backup keys, scheduling, and recovery dependencies

| Item | Non-secret value or requirement | Status | Owner/provider | Source of truth / location | Verification method | Collection or next action |
| --- | --- | --- | --- | --- | --- | --- |
<!-- inventory:restic-repository-credential -->
| Restic repository access credential | Identity/reference, scopes, mount location, rotation/revocation owner only | `owner-required` | Backup operator / NAS owner | Secret manager or root-owned mounted-file metadata | Backup and restore a disposable fixture; confirm access is limited to dedicated repository | Provision repository-specific credential; exclude its value from logs and inventory |
<!-- inventory:restic-encryption-key -->
| Restic encryption password/key | Secret reference and custodian only; value must be recoverable independently of production host | `owner-required` | Backup key custodian | Approved secret manager/off-host escrow metadata | Recovery custodian retrieves it in isolated drill and successfully opens repository; never print it | Generate high-entropy value and escrow before first authoritative backup |
<!-- inventory:backup-key-escrow -->
| Off-host backup-key escrow | Owner-provided escrow system/location label, primary/backup custodians, access/recovery process | `owner-required` | Production owner / security custodian | Organization recovery register | Two-custodian retrieval drill from an isolated recovery environment | Establish off-host escrow; host-local-only storage is not acceptable |
<!-- inventory:backup-schedule-owner -->
| Daily backup schedule | Daily consistent PostgreSQL dump and Restic transfer; actual timer/job location and owner owner-provided | `owner-required` | Backup operator | Host scheduler/service inventory | Inspect timer history and backup evidence, then verify most recent snapshot age | R03 installs schedule; owner records operational responsibility |
<!-- inventory:backup-alert-destination -->
| Backup/capacity alert destination | Owner-provided monitored channel/service and acknowledgement owner; webhook/token excluded | `owner-required` | Operations owner | Alerting service configuration metadata | Send synthetic failure and low-disk alerts; record acknowledgement evidence | Configure route before relying on unattended backups |
<!-- inventory:local-backup-buffer -->
| NAS-outage local buffer | Up to seven encrypted local backups with a disk safety floor; exact mount/floor owner-provided | `owner-required` | Host administrator / backup operator | Host storage plan and R03 configuration | Simulate NAS outage, verify bounded retention and refusal/alert before disk exhaustion | Allocate mount and numeric floor based on measured dump size |
<!-- inventory:restore-operator -->
| Restore operator | Owner-provided primary/backup operators with database, Restic, purge replay, and readiness duties | `owner-required` | Production owner | Private recovery ownership register | Operators complete destructive isolated restore drill using runbook only | Assign before R03 and record escalation path |
<!-- inventory:restore-sandbox -->
| Isolated restore environment | Owner-provided non-production host/project with capacity and network isolation | `owner-required` | Recovery owner / hosting provider | Recovery environment inventory | Confirm production ingress/DNS cannot target sandbox; perform destructive restore there | Allocate sandbox before first recovery certification |
<!-- inventory:purge-tombstone-source -->
| Purge tombstone replay source | Database tombstones plus a write-ahead monotonic append/checkpoint in the independent purge ledger; restored data is never its own sole replay source | `dependent-task` | L02/R03 implementers | Database migration, purge-ledger protocol, and recovery-runbook artifacts | Crash at each append/acknowledge/delete/checkpoint/client-ack boundary; restore backup N, replay ledger entries after N's checkpoint, and prove later-purged content remains unavailable | L02 defines durable-append-before-delete and idempotent reconciliation semantics; R03 integrates replay ordering and evidence |
<!-- inventory:purge-ledger-storage -->
| Independent purge ledger storage | Append-only, integrity-protected non-content ledger outside the PostgreSQL backup generation it repairs; dedicated writer and read-only restore identities, deployment lineage, retention, monotonic sequence, record digest/authenticator, durable acknowledgement, and last checkpoint | `dependent-task` | L02/R03 implementers / backup security owner | Separate restricted NAS repository/object namespace and recovery metadata | Deny mutation by application/database roles; reject forged valid-looking entries, rollback, gaps, digest conflicts, and acknowledgement loss; retain ledger at least as long as every recoverable backup; withhold purge/readiness when unavailable | L02 defines conditional append and durable acknowledgement before irreversible deletion plus retry reconciliation; R03 provisions it and rehearses writer compromise, loss, tamper, rollback, and gap failures |
<!-- inventory:index-rebuild-capacity -->
| Full index rebuild dependency | Embedding image/model digest availability, CPU/RAM headroom, estimated duration, and operator | `dependent-task` | V03/R03 implementers and host administrator | Model registry/cache policy, benchmark evidence, recovery runbook | Delete derived indexes in sandbox and rebuild from authoritative data within measured envelope | V03 records model/version/resources; R03 proves from-zero rebuild after restore |

Authoritative backups include consistent PostgreSQL data and required non-secret
configuration. The independently durable append-only purge ledger is retained at
least as long as every backup it may need to repair and records a monotonic backup
checkpoint/watermark. Vector/lexical indexes are rebuilt. Recovery cannot open
readiness until schema migration is valid, the ledger is present and gap-free,
every tombstone after the restored backup's checkpoint is replayed, authorization
is current, and required indexes are either safely rebuilt or explicitly degraded
per the implemented readiness policy.

## Dependency and readiness order

1. Production owner assigns host, Caddy, DNS/TLS, network, NAS, registry, release,
   secret, backup, and restore owners.
2. Host and restore sandbox capacity are measured against the reserved envelope.
3. DNS name and canonical HTTPS `/d` base URL are fixed; OIDC/OAuth registrations
   and discovery routes are then bound to that value.
4. Tailscale ACLs and the dedicated NAS repository are allocated and tested.
5. Registry namespaces and separate publish/pull identities are provisioned.
6. Host access, approval gates, config paths, and mounted-secret paths are created.
7. R01/R02 produce container, Caddy, deployment, health, and rollback evidence.
8. L02/V03 produce purge-replay and rebuild dependencies.
9. R03 provisions backup credentials/key escrow, runs backup/outage/alert tests,
   performs an isolated destructive restore, replays purges, and rebuilds indexes.
10. Only R04 evidence can change **Deployment ready** to `Yes`.

## Collection and verification runbook

The production owner should copy this checklist into private operational evidence.
Record non-secret outputs or hashes/evidence links; redact unrelated host/service
details. Never paste command output containing environment variables or secrets.

### 1. Owner interview

- Assign one accountable owner and one escalation route for every row.
- Resolve every `owner-required` value in the private environment record, then add
  only its non-secret value or source-of-truth location to this inventory.
- Confirm each secret has a separate custodian, rotation, revocation, and recovery
  procedure. Confirm the inventory names references only, never values.

### 2. Host evidence

Run on the intended host:

```text
hostnamectl
cat /etc/os-release
uname -m
nproc
free -h
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS
df -h
ss -ltnp
```

Capture OS/architecture and capacity. Review listening sockets for unexpected
public services; do not paste unrelated process arguments into the repository.

### 3. Caddy, DNS, and TLS evidence

- Inspect the system service to identify the active config location and owner.
- Validate the candidate Caddy file before reload and record validation outcome.
- Query authoritative A/AAAA records and test HTTPS from outside the host.
- Exercise `/d/`, `/d/api/v1/`, `/d/mcp`, `/d/oauth/`, and finalized discovery
  routes; verify redirects and generated links keep the canonical origin/prefix.
- Check certificate chain, hostname, expiry, automated renewal, and alert ownership.

### 4. Private backup path evidence

- Confirm the production host and NAS are approved Tailscale devices and ACLs allow
  only required traffic.
- Confirm the repository path is dedicated and capacity-monitored.
- Use mounted credentials to initialize/open the repository; never place a Restic
  password in command history, process arguments, CI logs, or this document.
- Back up and restore a disposable fixture, test 30-day retention dry-run output,
  NAS outage buffering, disk floor, and synthetic alert delivery.

### 5. Release and secret-reference evidence

- Push/sign and pull a disposable image by digest with separate identities.
- Verify the production pull identity cannot push.
- Verify approval blocks a no-op deployment until an authorized approver acts.
- Use `stat` and access attempts to verify root-owned secret paths; never display
  file contents. Verify services can read only their required secret files.
- Exercise credential rotation/revocation one identity at a time with rollback.

### 6. Recovery evidence

- Retrieve backup access and encryption material from off-host escrow into an
  isolated recovery session without exposing values.
- Restore the authoritative database into the sandbox, apply migrations, replay
  tombstones before readiness, and confirm purged data remains unavailable.
- Rebuild lexical/vector indexes from zero with pinned model/image digests.
- Measure time, peak disk/memory, and failures; update capacity requirements.
- Record RPO/RTO observations, evidence links, operator names, and follow-up items.

## Readiness blockers at inventory creation

Deployment is intentionally blocked until all `owner-required` rows are supplied
and verified, all `dependent-task` rows have passing evidence, and R04 completes.
Specifically, no target host facts, DNS/base URL, Caddy owner/config location,
Tailscale/NAS details, registry identities, deployment access/approval, secret
references, backup-key escrow, alert destination, or recovery sandbox have been
provided in repository documentation. This explicit state prevents placeholder
values from being mistaken for deployable configuration.
