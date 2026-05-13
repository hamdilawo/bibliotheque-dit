#!/bin/sh
# ============================================================
#  entrypoint.sh — Script de démarrage du service Livres
# ============================================================
set -e

echo "🚀 Démarrage du service Livres..."

# ─── Attendre que PostgreSQL soit prêt ───────────────────────
echo "⏳ Attente de PostgreSQL..."
while ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; do
    sleep 1
done
echo "✓ PostgreSQL prêt"


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

    GRANT ALL PRIVILEGES ON DATABASE "$DB_NAME" TO "$POSTGRES_USER";
EOSQL



# ─── Créer les tables directement ────────────────────────────
echo "📦 Création des tables..."
python - <<'EOF'
import asyncio, os
from piccolo.engine.postgres import PostgresEngine
DB = PostgresEngine(config={
    'host': os.getenv('DB_HOST', 'db'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'livres_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres'),
})
from features.books.tables import Categorie, Livre
async def create():
    await Categorie.create_table(if_not_exists=True).run()
    await Livre.create_table(if_not_exists=True).run()
    print('Tables créées.')
asyncio.run(create())
EOF
echo "✓ Tables prêtes"

# ─── Lancer le seed si la base est vide ──────────────────────
echo "🌱 Vérification des données initiales..."
python seed.py
echo "✓ Données vérifiées"

# ─── Démarrer Uvicorn ────────────────────────────────────────
echo "✅ Lancement de l'API sur le port 8001..."
exec uvicorn app:app \
    --host 0.0.0.0 \
    --port 8001 \
    --workers 2 \
    --access-log