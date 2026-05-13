# 📚 Service Livres

Microservice de gestion du catalogue de livres de la **Bibliothèque Numérique DIT**.

Développé avec **Litestar** + **Piccolo ORM** + **PostgreSQL** + **MinIO**.

---

## 🏗️ Architecture

```
services/livres/
├── core/
│   ├── database.py       ← Connexion Piccolo ORM
│   ├── docs_auth.py      ← Configuration Swagger
│   ├── exceptions.py     ← Exceptions personnalisées
│   ├── guards.py         ← Protection des routes (JWT)
│   ├── settings.py       ← Variables d'environnement
│   └── storage.py        ← Gestion des images (MinIO)
├── features/
│   ├── __init__.py
│   └── books/
│       ├── __init__.py
│       ├── migrations/   ← Migrations Piccolo
│       ├── controller.py ← Routes Litestar
│       ├── piccolo_app.py← Config migrations
│       ├── schemas.py    ← Validation Pydantic
│       ├── service.py    ← Logique métier
│       └── tables.py     ← Modèles Piccolo ORM (UUID)
├── tests/
│   ├── test_endpoints.py
│   ├── test_schemas.py
│   ├── test_tables.py
│   └── conftest.py
├── app.py                ← Point d'entrée Litestar
├── entrypoint.sh         ← Démarrage Docker
├── mypy.ini              ← Configuration mypy
├── seed.py               ← Données initiales
├── Dockerfile
└── requirements.txt
```

---

## 🚀 Démarrage

### Prérequis
- Docker & Docker Compose

### Lancer le service

```bash
# Depuis la racine du projet
docker compose up -d
```

L'`entrypoint.sh` s'occupe automatiquement de :
1. Attendre que PostgreSQL soit prêt
2. Appliquer les migrations
3. Peupler la base (50 livres, 5 catégories)
4. Démarrer Uvicorn sur le port **8001**

### Arrêter le service

```bash
docker compose down
```

### Reconstruire les images (après modification du Dockerfile ou requirements.txt)

```bash
docker compose up livres db --build
```

---

## 🗃️ Migrations

### Vérifier l'état des migrations

```bash
docker compose exec livres piccolo migrations check
```

### Appliquer les migrations

```bash
docker compose exec livres piccolo migrations forward all
```

### Vérifier les tables en base

```bash
docker compose exec db psql -U postgres -d livres_db -c "\dt"
```

### Vérifier le contenu des tables

```bash
docker compose exec db psql -U postgres -d livres_db -c "SELECT id, nom FROM categories;"
docker compose exec db psql -U postgres -d livres_db -c "SELECT id, titre, auteur, langue FROM livres LIMIT 5;"
```

---

## 🌱 Seed

### Peupler la base

```bash
docker compose exec livres python seed.py
```

### Repartir de zéro

```bash
docker compose exec livres python seed.py --reset
```

---

## 🔌 Endpoints API

| Méthode | URL | Description |
|---|---|---|
| `GET` | `/api/livres` | Liste paginée des livres |
| `POST` | `/api/livres` | Créer un livre (multipart/form-data) |
| `GET` | `/api/livres/{livre_id}` | Détail d'un livre |
| `PATCH` | `/api/livres/{livre_id}` | Modification partielle |
| `DELETE` | `/api/livres/{livre_id}` | Désactiver (soft delete) |
| `GET` | `/api/livres/{livre_id}/disponibilite` | Disponibilité et couverture |
| `GET` | `/api/livres/search` | Recherche multi-critères |
| `GET` | `/api/categories` | Liste des catégories |
| `GET` | `/health` | Health check |

### Documentation interactive

```
http://localhost:8001/schema/swagger
```

---

## 📖 Exemples de requêtes

### Health check
```bash
curl http://localhost:8001/health
```

### Lister les livres
```bash
curl http://localhost:8001/api/livres
```

### Lister avec pagination et tri
```bash
curl "http://localhost:8001/api/livres?page=1&page_size=10&sort=auteur"
```

### Détail d'un livre
```bash
curl http://localhost:8001/api/livres/{livre_id}
```

### Rechercher par titre, auteur ou ISBN
```bash
curl "http://localhost:8001/api/livres/search?q=python"
curl "http://localhost:8001/api/livres/search?langue=fr"
curl "http://localhost:8001/api/livres/search?q=python&langue=en&annee_min=2015"
```

### Créer un livre (multipart/form-data)
```bash
curl -X POST http://localhost:8001/api/livres \
  -F "titre=L'étranger" \
  -F "auteur=Albert Camus" \
  -F "isbn=9782070360024" \
  -F "langue=fr" \
  -F "annee_publication=1942" \
  -F "quantite_totale=10"
```

### Créer un livre avec couverture
```bash
curl -X POST http://localhost:8001/api/livres \
  -F "titre=L'étranger" \
  -F "auteur=Albert Camus" \
  -F "isbn=9782070360024" \
  -F "couverture=@/chemin/vers/image.jpg"
```

### Modifier partiellement un livre
```bash
curl -X PATCH http://localhost:8001/api/livres/{livre_id} \
  -H "Content-Type: application/json" \
  -d '{"quantite_totale": 5}'
```

### Supprimer un livre (soft delete)
```bash
curl -X DELETE http://localhost:8001/api/livres/{livre_id}
```

### Consulter la disponibilité d'un livre
```bash
curl http://localhost:8001/api/livres/{livre_id}/disponibilite
```

### Lister les catégories
```bash
curl http://localhost:8001/api/categories
```

### PowerShell — Créer un livre
```powershell
curl -Uri "http://localhost:8001/api/livres" -Method POST -Form @{titre="Test Livre"; auteur="Test Auteur"; isbn="9782100790319"}
```

---

## 🧪 Vérification du code

### Vérification des types
```bash
mypy .
```

### Vérification du style
```bash
ruff check .
```

### Correction automatique
```bash
ruff check . --fix
```

---

## 🧪 Tests

```bash
docker compose exec livres pytest tests/ -v
```

---

## 🔁 Git

### Push sur la branche de travail
```bash
git add .
git commit -m "votre message"
git push origin books/develop
```

### Changer de branche avec modifications en cours
```bash
git stash
git checkout books/develop
git stash pop
```

---

## 🗄️ Données initiales

Le `seed.py` crée automatiquement **50 livres** en **5 catégories** :

| Catégorie | Livres |
|---|---|
| Intelligence Artificielle | 15 |
| Informatique | 15 |
| Mathématiques | 10 |
| Sciences | 5 |
| Littérature | 5 |

---

## ✅ Validations

- **ISBN-13** : vérification des 13 chiffres + clé de contrôle (algorithme officiel)
- **Année** : entre 1000 et l'année courante
- **UUID** : identifiants aléatoires (`uuid4`) pour livres et catégories, non incrémentés
- **ISBN unique** : 409 Conflict si doublon
- **Soft delete** : les livres supprimés restent en base (`actif=False`)
- **PATCH** : l'ISBN ne peut pas être modifié après création
- **Couverture** : upload optionnel via multipart/form-data, stockée dans MinIO

---

## 🔧 Variables d'environnement

```bash
cp .env.example .env
```

| Variable | Défaut | Description |
|---|---|---|
| `DB_HOST` | `db` | Hôte PostgreSQL |
| `DB_PORT` | `5432` | Port PostgreSQL |
| `DB_NAME` | `livres_db` | Nom de la base |
| `DB_USER` | `postgres` | Utilisateur |
| `DB_PASSWORD` | `postgres` | Mot de passe |
| `DEBUG` | `True` | Mode debug |
| `MINIO_ENDPOINT` | `minio:9000` | Endpoint MinIO |
| `MINIO_ACCESS_KEY` | `minioadmin` | Clé d'accès MinIO |
| `MINIO_SECRET_KEY` | `minioadmin123` | Clé secrète MinIO |
| `MINIO_BUCKET_COUVERTURES` | `couvertures` | Bucket des couvertures |
| `MINIO_USE_SSL` | `false` | SSL MinIO |
| `MINIO_PUBLIC_URL` | `http://localhost:9090` | URL publique MinIO |

---

## 🛠️ Technologies

| Technologie | Version | Rôle |
|---|---|---|
| Litestar | 2.8.3 | Framework ASGI |
| Piccolo ORM | 1.6.0 | ORM async PostgreSQL |
| Pydantic | 2.7.0 | Validation des données |
| Uvicorn | 0.29.0 | Serveur ASGI |
| PostgreSQL | 16.13 | Base de données |
| MinIO | latest | Stockage des couvertures |
| pytest | 8.2.0 | Tests unitaires |