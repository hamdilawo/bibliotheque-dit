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

echo "==> Vérification des données d'emprunts..."
LOAN_COUNT=$(uv run python manage.py shell -c "from loans.adapters.database.models.emprunt import Emprunt; print(Emprunt.objects.count())" 2>/dev/null || echo "0")
if [ "$LOAN_COUNT" = "0" ]; then
  echo "==> Aucun emprunt trouvé — seed automatique..."
  uv run python manage.py seed_loans || echo "==> Seed ignoré (service livres pas encore prêt ?)"
else
  echo "==> $LOAN_COUNT emprunts existants — seed ignoré."
fi

echo "==> Démarrage..."
exec "$@"