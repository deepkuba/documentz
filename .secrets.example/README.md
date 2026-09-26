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
