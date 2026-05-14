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
python manage.py migrate --noinput

echo "==> Création des comptes par défaut..."
python manage.py shell -c "
from users.models import User

accounts = [
    dict(email='mamadou.diallo@dit.sn', password='dit2024!',
         first_name='Mamadou', last_name='Diallo', role='STUDENT'),
    dict(email='admin@dit.sn', password='admin2024!',
         first_name='Admin', last_name='DIT', role='STAFF',
         is_staff=True, is_superuser=True),
]

for data in accounts:
    password = data.pop('password')
    if not User.objects.filter(email=data['email']).exists():
        User.objects.create_user(password=password, **data)
        print(f'Créé : {data[\"email\"]}')
    else:
        print(f'Existe déjà : {data[\"email\"]}')
"

echo "==> Démarrage..."
exec "$@"