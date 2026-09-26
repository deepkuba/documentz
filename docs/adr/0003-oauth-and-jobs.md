# Use Authlib and Procrastinate at infrastructure boundaries

Documentz will use Authlib 1.8.0 for OAuth 2.0/OIDC protocol primitives and Procrastinate 3.10.0 for PostgreSQL-backed durable jobs. Authlib supplies standards primitives including Authorization Code, PKCE, revocation, and discovery while leaving consent, opaque token persistence, project grants, and policy in Documentz services; Procrastinate keeps job storage in PostgreSQL and supports transaction-aware deferral without introducing a second broker. Slice A01 must still prove configurable `/d` paths, custom consent and persistence hooks, MCP discovery, and opaque tokens before production OAuth work proceeds.

Compatibility evidence (checked 2026-09-26): [Authlib supported protocols and Python versions](https://pypi.org/project/Authlib/1.8.0/), [Authlib OAuth 2.0 documentation](https://docs.authlib.org/en/stable/oauth2/), the [Procrastinate PostgreSQL/Python support metadata](https://pypi.org/project/procrastinate/3.10.0/), and [atomic deferral on an external transaction](https://procrastinate.readthedocs.io/en/stable/howto/production/external_connection.html).

## Consequences

Authlib is a protocol toolkit rather than a ready-made FastAPI authorization server, so A01 is a mandatory compatibility gate. Jobs must be deferred on the same PostgreSQL connection/transaction as authoritative state changes; workers receive identifiers, never document content, OAuth tokens, or client secrets as job arguments.
