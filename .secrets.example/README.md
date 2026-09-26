# Local database secrets

Create `.secrets/postgres-development-password` and
`.secrets/postgres-test-password` as distinct, non-empty local-only values:

```sh
mkdir -m 700 .secrets
openssl rand -base64 32 > .secrets/postgres-development-password
openssl rand -base64 32 > .secrets/postgres-test-password
chmod 600 .secrets/postgres-*-password
```

The `.secrets` directory is ignored by Git. Alternatively, point
`DOCUMENTZ_DEV_POSTGRES_PASSWORD_FILE` and
`DOCUMENTZ_TEST_POSTGRES_PASSWORD_FILE` at files outside the checkout. Never
place production credentials in these development files.

## API and worker settings

The API and worker expose the same typed settings contract. With no settings
provided, both use local mode, `http://localhost:8000/d`, and a credential-free
localhost PostgreSQL URL. Override non-secret values with:

```sh
export DOCUMENTZ_ENVIRONMENT=local
export DOCUMENTZ_EXTERNAL_BASE_URL=http://localhost:8000/d
```

Database credentials may be mounted without placing them in an environment
variable. Point both processes at a directory containing the exact, case-sensitive
file name `DOCUMENTZ_DATABASE_URL`:

```sh
export DOCUMENTZ_SECRETS_DIR=/run/secrets/documentz
```

The file contains only the PostgreSQL URL value. Do not print it or commit an
example value. A lowercase or unprefixed filename is deliberately ignored.

Production additionally requires `DOCUMENTZ_ENVIRONMENT=production` and an
explicit `DOCUMENTZ_EXTERNAL_BASE_URL` and `DOCUMENTZ_DATABASE_URL` (the latter
may come from the mounted secret file). The database URL must use the PostgreSQL
psycopg driver and name a database. The external URL must be one absolute HTTPS URL
with the exact `/d` path. User information, a trailing slash, an explicit `:443`,
a query, and a fragment are rejected so every generated public link has one
canonical origin and prefix.
