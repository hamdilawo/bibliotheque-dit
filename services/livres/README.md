# 📚 Service Livres

Microservice de gestion du catalogue de livres de la **Bibliothèque Numérique DIT**.

Développé avec **Litestar** + **Piccolo ORM** + **PostgreSQL**.

---

## 🏗️ Architecture

```
services/livres/
├── core/
│   ├── database.py       ← Connexion Piccolo ORM
│   ├── docs_auth.py      ← Configuration OpenAPI / Scalar
│   ├── exceptions.py     ← Exceptions personnalisées
│   ├── guards.py         ← Protection des routes (JWT)
│   ├── settings.py       ← Variables d'environnement
│   └── storage.py        ← Gestion des images
├── features/books/
│   ├── migrations/       ← Migrations Piccolo
│   ├── controller.py     ← Routes Litestar
│   ├── piccolo_app.py    ← Config migrations
│   ├── schemas.py        ← Validation Pydantic
│   ├── service.py        ← Logique métier
│   └── tables.py         ← Modèles Piccolo ORM
├── tests/
│   ├── test_endpoints.py ← 22 tests HTTP
│   ├── test_schemas.py   ← 16 tests validation
│   ├── test_tables.py    ← 12 tests métier
│   └── conftest.py
├── app.py                ← Point d'entrée Litestar
├── entrypoint.sh         ← Démarrage Docker
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
docker compose up livres db
```

L'`entrypoint.sh` s'occupe automatiquement de :
1. Attendre que PostgreSQL soit prêt
2. Créer les tables
3. Peupler la base (50 livres, 5 catégories)
4. Démarrer Uvicorn sur le port **8001**

---

## 🔌 Endpoints API

| Méthode | URL | Description |
|---|---|---|
| `GET` | `/api/livres/` | Liste paginée des livres |
| `POST` | `/api/livres/` | Créer un livre |
| `GET` | `/api/livres/{id}/` | Détail d'un livre |
| `PUT` | `/api/livres/{id}/` | Modifier complètement |
| `PATCH` | `/api/livres/{id}/` | Modification partielle |
| `DELETE` | `/api/livres/{id}/` | Désactiver (soft delete) |
| `GET` | `/api/livres/search/` | Recherche multi-critères |
| `GET` | `/api/livres/disponibles/` | Livres disponibles |
| `POST` | `/api/livres/{id}/disponibilite/` | Réserver / retourner |
| `GET` | `/api/categories/` | Liste des catégories |
| `POST` | `/api/categories/` | Créer une catégorie |
| `GET` | `/api/categories/{id}/` | Détail d'une catégorie |
| `GET` | `/health/` | Health check |

### Documentation interactive

```
http://localhost:8001/schema/scalar
```

---

## 📖 Exemples de requêtes

### Lister les livres
```bash
curl http://localhost:8001/api/livres/
```

### Rechercher par titre, auteur ou ISBN
```bash
curl "http://localhost:8001/api/livres/search?q=python"
curl "http://localhost:8001/api/livres/search?langue=fr&disponible=true"
```

### Créer un livre
```bash
curl -X POST http://localhost:8001/api/livres/ \
  -H "Content-Type: application/json" \
  -d '{
    "titre": "L'\''étranger",
    "auteur": "Albert Camus",
    "isbn": "9782070360024",
    "langue": "fr",
    "annee_publication": 1942,
    "categorie": 5,
    "quantite_totale": 10
  }'
```

### Réserver un livre (appelé par le service Emprunts)
```bash
curl -X POST http://localhost:8001/api/livres/1/disponibilite/ \
  -H "Content-Type: application/json" \
  -d '{"action": "reserver", "quantite": 1}'
```

### Health check
```bash
curl http://localhost:8001/health
# {"status": "ok", "service": "livres", "db": "connected", "version": "2.0.0"}
```

---

## 🧪 Tests

```bash
# Lancer tous les tests
docker compose exec livres pytest tests/ -v

# Résultat attendu : 63/63 tests passent
```

### Couverture des tests

| Fichier | Tests | Description |
|---|---|---|
| `test_endpoints.py` | 22 | Tous les endpoints HTTP |
| `test_schemas.py` | 16 | Validation Pydantic (ISBN, année, stock) |
| `test_tables.py` | 12 | Méthodes métier (reserver, retourner) |
| **Total** | **63** | |

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
- **Stock** : `quantite_disponible` ≤ `quantite_totale`
- **ISBN unique** : 409 Conflict si doublon
- **Soft delete** : les livres supprimés restent en base (`actif=False`)
- **PATCH** : l'ISBN ne peut pas être modifié après création

---

## 🔧 Variables d'environnement

Copier `.env.example` en `.env` :

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

---

## 🛠️ Technologies

| Technologie | Version | Rôle |
|---|---|---|
| Litestar | 2.8.3 | Framework ASGI |
| Piccolo ORM | 1.6.0 | ORM async PostgreSQL |
| Pydantic | 2.7.0 | Validation des données |
| Uvicorn | 0.29.0 | Serveur ASGI |
| PostgreSQL | 16.13 | Base de données |
| pytest | 8.2.0 | Tests unitaires |
