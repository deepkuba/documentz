# Personal Context Service

This context describes durable personal information that can be used across AI clients, sessions, and personal projects without repeatedly placing the entire history into a prompt.

## Language

**Personal Context Service**:
A user-controlled source of durable information for reconstructing relevant context across AI-assisted work. Its public document contract remains stable independently of its storage and retrieval mechanisms.
_Avoid_: AI memory, notebook

**Personal Project**:
A user-defined boundary that groups context concerning one continuing area of work or activity. Context Documents are visible only within their owning Personal Project unless access is explicitly shared; an archived Personal Project is retained but omitted from ordinary project listings.
_Avoid_: Application, chat

**Application**:
An authenticated software client that uses the Personal Context Service on behalf of Users. An Application may access multiple Personal Projects, and a Personal Project may be accessed by multiple Applications.
_Avoid_: Project, user

**Application Authorization**:
A revocable User-approved grant allowing one Application a fixed set of operations on explicitly selected Personal Projects. Expanding its operations or project selection requires renewed explicit consent.
_Avoid_: User session, unrestricted client access

**User**:
A human principal whose identity and permissions constrain document operations performed through an Application.
_Avoid_: Application, token

**Context Document**:
A domain-neutral unit of text, limited to 16 KiB of UTF-8 content, exposed through the Personal Context Service's document contract. The service rejects oversized content; callers may represent it using multiple related Context Documents.
_Avoid_: Prompt, message

Every Context Document has one service-defined kind: `note`, `session_summary`, `source_document`, `derived_summary`, or `other`. Complete conversations are not Context Documents.

A Context Document's owning Personal Project, kind, and origin are fixed at creation. Active and rejected documents may acquire new snapshots; a soft-deleted document must be restored before it can be changed.

When the kind is `other`, the document has a required `custom_kind` describing its application-defined classification. A custom kind has no service-defined behavior.

Every Context Document has one lifecycle state: `active`, `rejected`, `soft_deleted`, or `purged`. Only active documents participate in ordinary search and MCP retrieval. Rejected documents may be reactivated indefinitely; soft-deleted documents may be restored during their recovery period.

**Document Fragment**:
A Context Document containing one caller-selected part of a larger logical body of text. Its immutable descriptor identifies the Fragment Set, zero-based position, and total fragment count; descriptive metadata belongs to the set rather than its individual fragments.
_Avoid_: Binary chunk, token window

**Fragment Set**:
One logical searchable body formed by an ordered group of same-kind Document Fragments in one Personal Project. It owns their shared title, tags, custom metadata, origin, access policy, and lifecycle; membership and ordering are immutable after atomic publication, although each fragment may acquire new snapshots.
_Avoid_: Search result set, partial upload

A draft Fragment Set is visible only to authorized writers and is permanently removed when abandoned or after 24 hours. A published Fragment Set appears as one result in ordinary search, and lifecycle changes apply atomically to every member.

**Document Snapshot**:
An immutable version of a Context Document's content-describing fields: content, title, kind, custom kind, tags, custom metadata, origin, and source-snapshot references. The stable Context Document identifies its current snapshot.
_Avoid_: Mutable document version

Only the current snapshot of an active Context Document participates in ordinary search. Historical snapshots may be browsed explicitly and do not have independent lifecycle states.

**Document Metadata**:
Structured information describing a Context Document or one of its snapshots, including classification, provenance, relationships, and lifecycle state. It is stored separately from document content.
_Avoid_: Front matter, embedded metadata

**Document Projection**:
A caller-selected subset of document content and metadata returned after authorization. Projections avoid transmitting fields unnecessary for the current operation.
_Avoid_: Complete document record, authorization filter

**Document Origin**:
The service-derived way a Context Document entered the system: `user_submitted`, `application_submitted`, `imported`, or `service_generated`. Callers cannot select it; origin is distinct from document kind and from the authenticated User and Application responsible for the operation.
_Avoid_: Document kind, application name

**Session Summary**:
A caller-authored primary record of a completed work session without formal source-snapshot dependencies. It may serve as a source for a Derived Summary.
_Avoid_: Conversation transcript, Derived Summary

**Derived Summary**:
A Context Document, limited to 2 KiB of UTF-8 content, supplied by a caller to summarize one or more exact source snapshots from the same Personal Project that are not themselves Derived Summaries. It inherits the intersection of its sources' access constraints; a Derived Summary cannot itself be a source of another Derived Summary.
_Avoid_: Authoritative source, current summary

Its source-snapshot set is fixed at creation, while multiple Derived Summaries may reference the same source. Regenerating a summary for newer source snapshots creates a new Derived Summary rather than changing the old one's provenance.

When storing an eligible active source, an agent is asked to summarize it and the caller supplies the resulting Derived Summary. Source documents and session summaries larger than 2 KiB are eligible; a Derived Summary may cover an entire published Fragment Set or selected Document Fragments, but fragment summarization remains optional.

A Derived Summary becomes stale and leaves ordinary search when any referenced snapshot stops being current or any source becomes rejected or soft-deleted. It may return to search or be regenerated after every source is active again, and is permanently purged when any contributing source is purged.

**Summary Request**:
A persistent invitation for a caller to supply an optional Derived Summary for eligible exact source snapshots. It is `pending`, `completed`, `declined`, or `superseded`; storing a replacement source snapshot supersedes requests for the replaced snapshot.
_Avoid_: Required summarization job, service-generated summary

**Management Portal**:
The first-party client through which authenticated Users and Application Owners browse and import documents, manage access and document lifecycle, and delete or purge data. It uses the same public service API and authorization rules as other clients.
_Avoid_: Administrative backdoor

**Soft-Deleted Document**:
A Context Document hidden from ordinary retrieval for a 30-day recovery period before permanent purging. It may be restored through the Management Portal during that period.
_Avoid_: Purged document

**Rejected Document**:
A Context Document marked as unsuitable or incorrect, excluded from ordinary retrieval but retained for inspection and indefinite reactivation.
_Avoid_: Soft-deleted document, purged document

**Purged Document**:
A Context Document whose content, snapshots, derived summaries, tags, and indexes have been permanently removed. Only a non-content audit tombstone remains.
_Avoid_: Soft-deleted document

**Context Recreation**:
Selecting and presenting relevant Context Documents so an AI session can continue useful work without receiving the user's entire stored history.
_Avoid_: Prompt stuffing

**Project Share**:
An explicit grant allowing one Personal Project to access Context Documents owned by another Personal Project. A Project Share does not transfer ownership of those documents.
_Avoid_: Public document, copied document

**Personal Access Token**:
A revocable credential carrying an immutable authorization grant for one User. Its permissions and resource selection cannot expand after issuance, and its expiry may only be shortened.
_Avoid_: API key, mutable role

**Role Template**:
A reusable permission template used when issuing a Personal Access Token. Changes to the template do not change previously issued tokens.
_Avoid_: Token role, live role
