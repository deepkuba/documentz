#!/bin/sh
set -eu

profile=${1:-}
case "$profile" in
  development)
    service=postgres
    password_file=${DOCUMENTZ_DEV_POSTGRES_PASSWORD_FILE:-.secrets/postgres-development-password}
    ;;
  test)
    service=postgres-test
    password_file=${DOCUMENTZ_TEST_POSTGRES_PASSWORD_FILE:-.secrets/postgres-test-password}
    ;;
  *)
    echo "usage: $0 development|test" >&2
    exit 2
    ;;
esac

if [ ! -s "$password_file" ]; then
  echo "database password file is missing or empty: $password_file" >&2
  exit 1
fi

docker compose --profile "$profile" up --detach --wait "$service"
container_id=$(docker compose --profile "$profile" ps --quiet "$service")
database_host=$(docker inspect \
  --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' \
  "$container_id")
if [ -z "$database_host" ]; then
  echo "could not resolve the private database address" >&2
  exit 1
fi

PGPASSWORD=$(tr -d '\r\n' < "$password_file")
export PGPASSWORD
export DOCUMENTZ_DATABASE_URL="postgresql+psycopg://documentz@${database_host}:5432/documentz"

docker compose --profile "$profile" exec --no-TTY "$service" \
  psql --username documentz --dbname documentz --set ON_ERROR_STOP=1 \
  --command "SELECT extversion FROM pg_extension WHERE extname = 'vector';"
.tools/uv-0.12.19/uv run --frozen alembic -c alembic.ini upgrade head
docker compose --profile "$profile" exec --no-TTY "$service" \
  psql --username documentz --dbname documentz --set ON_ERROR_STOP=1 \
  --command "SELECT version_num FROM alembic_version WHERE version_num = '0001_empty_foundation';"
