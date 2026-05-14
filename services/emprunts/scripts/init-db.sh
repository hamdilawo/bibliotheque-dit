#!/bin/bash
# entrypoint.sh — Init DB
set -e

echo "==> Attente que PostgreSQL soit prêt..."
until pg_isready -h "$DB_HOST" -p "${DB_PORT:-5432}" -U "$DB_USER"; do
  sleep 1
done

echo "==> Création de la base de données si elle n'existe pas..."
psql -v ON_ERROR_STOP=1 --username "$DB_USER" --host "$DB_HOST" <<-EOSQL
  SELECT 'CREATE DATABASE $DB_NAME'
  WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$DB_NAME')\gexec

  GRANT ALL PRIVILEGES ON DATABASE "$DB_NAME" TO "$DB_USER";
EOSQL

echo "==> Application des migrations Django..."
uv run python manage.py migrate --noinput

echo "==> Démarrage du serveur..."
exec "$@"
