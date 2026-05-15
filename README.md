# Bibliothèque Numérique DIT

Plateforme de gestion de bibliothèque académique en architecture microservices avec système de recommandation ML.  
Projet d'examen — Master 2 Intelligence Artificielle, Dakar Institute of Technology.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│                     http://localhost:3000                    │
└───────────┬─────────────┬──────────────┬────────────────────┘
            │             │              │
    ┌───────▼──────┐ ┌────▼──────┐ ┌────▼──────────┐ ┌──────────────┐
    │   Livres     │ │Utilisateurs│ │   Emprunts    │ │Recommandation│
    │  (Litestar)  │ │  (Django) │ │   (Django)    │ │  (FastAPI)   │
    │ :8003→:8001  │ │ :8002     │ │ :8008→:8000   │ │ :8004→:8000  │
    └──────┬───────┘ └────┬──────┘ └────┬──────────┘ └──────┬───────┘
           │              │              │                    │
    ┌──────▼──────┐ ┌─────▼──────┐ ┌────▼──────┐     ┌──────▼───────┐
    │  book-db    │ │  users-db  │ │  loans-db  │     │  model.pkl   │
    │ (Postgres)  │ │ (Postgres) │ │ (Postgres) │     │  (volume)    │
    └─────────────┘ └────────────┘ └────────────┘     └──────────────┘
                                              ┌──────────────────────┐
                                              │  MinIO (couvertures) │
                                              │  :9090 / :9091       │
                                              └──────────────────────┘
```

**5 microservices** — communication REST — 3 bases PostgreSQL — orchestration Docker Compose.

---

## Prérequis

- [Docker](https://www.docker.com/) ≥ 24
- [Docker Compose](https://docs.docker.com/compose/) ≥ 2.20

---

## Lancement rapide

### 1. Cloner le dépôt

```bash
git clone -b prod/v2 https://github.com/hamdilawo/bibliotheque-dit.git
cd bibliotheque-dit
```

### 2. Lancer en mode développement

```bash
docker compose --profile dev up --build
```

Tous les services démarrent automatiquement (bases de données, migrations, seed des livres).

### 3. Accéder à l'application

| Service | URL |
|---|---|
| **Frontend** | http://localhost:3000 |
| **API Livres** | http://localhost:8003/api/livres/ |
| **API Utilisateurs** | http://localhost:8002/api/users/ |
| **API Emprunts** | http://localhost:8008/api/emprunts/ |
| **API Recommandation** | http://localhost:8004/health |
| **MinIO Console** | http://localhost:9091 |

### 4. Générer les données d'entraînement ML

```bash
docker exec loans-api uv run python manage.py seed_loans
```

### 5. Entraîner le modèle

```bash
curl -X POST http://localhost:8004/train
```

### 6. Vérifier que le modèle est prêt

```bash
curl http://localhost:8004/health
# {"status":"ok","modele_charge":true,"entrainement_en_cours":false}
```

### 7. Créer un compte de test

```bash
curl -X POST http://localhost:8002/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@dit.sn","password":"dit2024!","first_name":"Test","last_name":"User","role":"STUDENT"}'
```

---

## Arrêter les services

```bash
docker compose down

# Reset complet (supprime aussi les volumes)
docker compose down -v
```

---

## Services et endpoints

### Livres — `http://localhost:8003`

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/api/livres/` | Liste paginée (`?page=1&page_size=20`) |
| `GET` | `/api/livres/{id}/` | Détail d'un livre |
| `GET` | `/api/livres/search/` | Recherche (`?q=python`) |
| `POST` | `/api/livres/` | Créer un livre |
| `PATCH` | `/api/livres/{id}/` | Modifier un livre |
| `DELETE` | `/api/livres/{id}/` | Supprimer un livre |

### Utilisateurs — `http://localhost:8002`

| Méthode | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/login/` | Connexion → JWT |
| `POST` | `/api/auth/token/refresh/` | Rafraîchir le token |
| `POST` | `/api/users/` | Créer un compte |
| `GET` | `/api/users/me/` | Profil connecté |

### Emprunts — `http://localhost:8008`

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/api/emprunts/` | Historique des emprunts |
| `POST` | `/api/emprunts/emprunter/` | Emprunter un livre |
| `POST` | `/api/emprunts/retourner/` | Retourner un livre |
| `POST` | `/api/emprunts/rate/` | Noter un emprunt (1-5) |
| `GET` | `/api/emprunts/export-csv/` | Export CSV (pipeline ML) |

### Recommandation — `http://localhost:8004`

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Santé + état du modèle |
| `GET` | `/recommendations/{user_id}` | Recommandations personnalisées |
| `GET` | `/popular` | Livres populaires (fallback) |
| `POST` | `/train` | Ré-entraîner le modèle |
| `GET` | `/metric` | RMSE et MAE du modèle |

---

## Système de recommandation

Le modèle utilise **SVD (Singular Value Decomposition)** — filtrage collaboratif basé sur l'historique des emprunts.

### Flux complet

```
Emprunts utilisateurs → export CSV → SVD training → model.pkl
                                                         ↓
Utilisateur connecté → GET /recommendations/{id} → scores personnalisés
Utilisateur non connecté → GET /popular → livres les plus empruntés
```

### Métriques

```bash
curl http://localhost:8004/metric
# {"rmse": 0.21, "mae": 0.04}
```

- **RMSE** : écart moyen entre note prédite et note réelle (0.21 = très précis)
- **MAE** : erreur absolue moyenne (0.04 = quasi parfait)

### Ré-entraînement automatique

Le modèle se ré-entraîne automatiquement **toutes les heures** via le service `dit-ml-cron`.  
Déclenchement manuel :

```bash
curl -X POST http://localhost:8004/train
```

### Cold start

Un nouvel utilisateur sans emprunt voit les **livres populaires** en attendant d'avoir un historique. Dès qu'il emprunte et que le modèle est ré-entraîné, il reçoit des recommandations personnalisées.

---

## Variables d'environnement

Fichier `.env` à la racine :

```dotenv
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123
JWT_SECRET_KEY=dit-library-shared-secret-key-2024
JWT_ALGORITHM=HS256
JWT_COOKIE_NAME=access_token
```

---

## Structure du projet

```
bibliotheque-dit/
├── docker-compose.yml          # Orchestration (profils dev/prod)
├── Caddyfile                   # Reverse proxy production (Azure)
├── .env                        # Variables d'environnement
│
├── services/
│   ├── livres/                 # Litestar + Piccolo ORM
│   ├── utilisateurs/           # Django REST Framework + JWT
│   ├── emprunts/               # Django (architecture hexagonale)
│   │   └── src/loans/
│   │       ├── app/            # Handlers, domain
│   │       └── adapters/       # HTTP, DB, services
│   ├── recommandation/         # FastAPI + SVD (scikit-learn)
│   │   └── app/
│   │       ├── main.py         # Endpoints
│   │       └── model.py        # SVD training
│   └── frontend/               # TanStack Start (React 19) + Bun
│
└── .github/workflows/
    └── deploy.yml              # CI/CD → Azure VM
```

---

## Technologie

| Service | Framework | Port |
|---|---|---|
| Livres | Litestar 2.x + Piccolo ORM | 8003 |
| Utilisateurs | Django REST Framework | 8002 |
| Emprunts | Django REST Framework (hexagonal) | 8008 |
| Recommandation | FastAPI + SVD scikit-learn | 8004 |
| Frontend | TanStack Start + React 19 + Tailwind | 3000 |
| Base de données | PostgreSQL 16 | — |
| Stockage | MinIO (S3-compatible) | 9090 |
| Proxy | Caddy (production) | 443 |
