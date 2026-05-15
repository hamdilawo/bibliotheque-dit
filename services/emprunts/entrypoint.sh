#!/bin/bash
set -e

echo "DEBUG => USER=$POSTGRES_USER | PASS=${POSTGRES_PASSWORD:0:3}*** | HOST=$DB_HOST | DB=$DB_NAME"

echo "==> Attente que PostgreSQL soit prêt..."
until pg_isready -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "$POSTGRES_USER"; do
  sleep 1
done

echo "==> Création de la base si elle n'existe pas..."
PGPASSWORD="$POSTGRES_PASSWORD" psql \
  --username "$POSTGRES_USER" \
  --host "$DB_HOST" \
  --port "${DB_PORT:-5432}" \
  --dbname "postgres" \
  <<-EOSQL
    SELECT 'CREATE DATABASE "$DB_NAME"'
    WHERE NOT EXISTS (
      SELECT FROM pg_database WHERE datname = '$DB_NAME'
    )\gexec

    GRANT ALL PRIVILEGES ON DATABASE "$DB_NAME" TO "$POSTGRES_USER";
EOSQL

echo "==> Migrations Django..."
uv run python manage.py migrate --noinput

if [ "${SEED_LOANS:-false}" = "true" ]; then
  (
    for i in $(seq 1 24); do
      if curl -sf http://book-api:8001/api/livres/ > /dev/null 2>&1; then
        echo "==> [seed] book-api prêt — lancement du seed..."
        uv run python manage.py seed_loans && echo "==> [seed] Terminé." || echo "==> [seed] Échoué."
        exit 0
      fi
      echo "==> [seed] tentative $i/24 — book-api pas encore prêt"
      sleep 5
    done
    echo "==> [seed] book-api inaccessible après 2 min — seed annulé."
  ) &
fi

echo "==> Démarrage..."
exec "$@"