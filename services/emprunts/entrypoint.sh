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
  echo "==> Attente du service livres (book-api)..."
  for i in $(seq 1 24); do
    if curl -sf http://book-api:8001/api/livres/ > /dev/null 2>&1; then
      echo "  book-api prêt."
      break
    fi
    echo "  ... tentative $i/24"
    sleep 5
  done
  echo "==> SEED_LOANS=true — génération des données d'entraînement ML..."
  uv run python manage.py seed_loans || echo "==> Seed échoué."
fi

echo "==> Démarrage..."
exec "$@"