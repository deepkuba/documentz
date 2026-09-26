# Database migrations

The revision chain begins empty so infrastructure connectivity can be proven
before S01 introduces application tables. Run migrations only with a dedicated
migration identity in production. Local development and test use:

```sh
DOCUMENTZ_DATABASE_URL=postgresql+psycopg://documentz:<local-password>@localhost/documentz \
  alembic upgrade head
```

The Compose databases deliberately publish no host port. The smoke script runs
Alembic in a temporary container attached to the private database network.
