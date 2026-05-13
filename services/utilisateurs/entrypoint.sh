#!/bin/bash
set -e

echo "DEBUG => USER=$DB_USER | PASS=${DB_PASSWORD:0:3}*** | HOST=$DB_HOST | DB=$DB_NAME"

echo "==> Attente que PostgreSQL soit prêt..."
until pg_isready -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "$DB_USER"; do
  sleep 1
done

echo "==> Création de la base si elle n'existe pas..."
PGPASSWORD="$DB_PASSWORD" psql \
  --username "$DB_USER" \
  --host "$DB_HOST" \
  --port "${DB_PORT:-5432}" \
  --dbname "postgres" \
  <<-EOSQL
    SELECT 'CREATE DATABASE "$DB_NAME"'
    WHERE NOT EXISTS (
      SELECT FROM pg_database WHERE datname = '$DB_NAME'
    )\gexec

    GRANT ALL PRIVILEGES ON DATABASE "$DB_NAME" TO "$DB_USER";
EOSQL

echo "==> Migrations Django..."
uv run python manage.py migrate --noinput

echo "==> Démarrage..."
exec "$@"