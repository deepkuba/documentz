# Local PostgreSQL and pgvector

The Compose file has two opt-in profiles:

- `development` uses a named volume so data survives container replacement;
- `test` uses a memory-backed data directory and a separate internal network and
  password, so test state cannot persist or reach the development database.

Neither database publishes a host port. Both use the Linux AMD64 manifest from
the `pgvector/pgvector:0.8.1-pg17` release, pinned by digest for the repository's
supported Linux x86-64 bootstrap target. The initialization script enables
`vector` on first database creation.

Create local secret files as described in [the secret template](../../.secrets.example/README.md),
then start a profile:

```sh
docker compose --profile development up --detach --wait postgres
docker compose --profile test up --detach --wait postgres-test
```

After bootstrapping the pinned Python workspace (which supplies Alembic,
SQLAlchemy, and psycopg), exercise the complete public integration seam:

```sh
scripts/postgres_pgvector_smoke.sh development
scripts/postgres_pgvector_smoke.sh test
```

The script connects over the profile's private Docker network, verifies the
`vector` extension, applies the empty Alembic revision, and confirms the applied
revision. Override `COMPOSE_PROJECT_NAME` when running concurrent checkouts.

Stop services without removing the persistent development volume:

```sh
docker compose --profile development --profile test down
```

Removing `postgres-development-data` destroys local development data and must be
an explicit operator action. The test profile has no persistent volume.
