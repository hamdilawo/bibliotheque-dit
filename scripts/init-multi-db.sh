#!/bin/bash
# Crée les 3 bases de données PostgreSQL au démarrage du conteneur
set -e

create_db() {
  local db=$1
  echo "Création de la base : $db"
  psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE $db;
    GRANT ALL PRIVILEGES ON DATABASE $db TO $POSTGRES_USER;
EOSQL
}

for db in livres_db utilisateurs_db emprunts_db; do
  create_db "$db"
done

echo "Toutes les bases de données créées."
