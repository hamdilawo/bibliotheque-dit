# Bibliothèque Numérique DIT

Plateforme de gestion de bibliothèque académique en architecture microservices.
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
                                                  ┌──────────────────┐
                                                  │  MinIO (stockage │
                                                  │  couvertures)    │
                                                  │  :9090 / :9091   │
                                                  └──────────────────┘
```

**5 microservices** — communication REST — 3 bases PostgreSQL dédiées — orchestration Docker Compose.

---

## Prérequis

- [Docker](https://www.docker.com/) ≥ 24
- [Docker Compose](https://docs.docker.com/compose/) ≥ 2.20
- [Python](https://python.org/) ≥ 3.11 *(pipeline DVC uniquement, en local)*
- [DVC](https://dvc.org/) *(pipeline ML uniquement)*

---

## Lancement rapide

### Mode développement (hot-reload)

```bash
# Cloner le dépôt
git clone <url-du-repo>
cd bibliotheque-dit

# Lancer tous les services en mode dev
docker compose --profile dev up --build

# Ou en arrière-plan
docker compose --profile dev up --build -d
```

### Mode production (build statique)

```bash
docker compose --profile prod up --build -d
```

### Arrêter les services

```bash
docker compose down

# Supprimer aussi les volumes (reset complet)
docker compose down -v
```

---

## Services et URLs

| Service | URL | Description |
|---|---|---|
| **Frontend** | http://localhost:3000 | Interface utilisateur |
| **Livres** | http://localhost:8003 | Catalogue de livres |
| **Utilisateurs** | http://localhost:8002 | Auth & gestion utilisateurs |
| **Emprunts** | http://localhost:8008 | Gestion des emprunts |
| **Recommandation** | http://localhost:8004 | Recommandations ML |
| **MinIO Console** | http://localhost:9091 | Stockage des couvertures |
| **MinIO API** | http://localhost:9090 | Accès S3-compatible |

---

## Initialisation de la base de données

Les bases de données sont **initialisées automatiquement** au démarrage via les entrypoints de chaque service :

1. Attente que PostgreSQL soit prêt (`pg_isready`)
2. Création de la base si elle n'existe pas
3. Application des migrations
4. Seed des données initiales (50 livres, 5 catégories)

Pour vérifier l'état :

```bash
# Vérifier que tous les services sont sains
docker compose ps

# Logs d'un service spécifique
docker compose logs book-api -f
docker compose logs utilisateurs -f
docker compose logs loans-api -f
```

### Comptes de test

Créer les comptes manuellement après le premier lancement :

```bash
# Compte étudiant
curl -X POST http://localhost:8002/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "mamadou.diallo@dit.sn",
    "password": "dit2024!",
    "first_name": "Mamadou",
    "last_name": "Diallo",
    "role": "STUDENT"
  }'

# Compte administrateur (via shell Django)
docker exec utilisateurs python manage.py shell -c "
from users.models import User
User.objects.create_user(
    email='admin@dit.sn', password='admin2024!',
    first_name='Admin', last_name='DIT',
    role='STAFF', is_staff=True, is_superuser=True
)"
```

| Rôle | Email | Mot de passe |
|---|---|---|
| Étudiant | `mamadou.diallo@dit.sn` | `dit2024!` |
| Admin (STAFF) | `admin@dit.sn` | `admin2024!` |

---

## Endpoints API

### Service Livres — `http://localhost:8003`

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/api/livres` | Liste paginée (`?page=1&page_size=20&sort=titre`) |
| `POST` | `/api/livres` | Créer un livre (multipart/form-data) |
| `GET` | `/api/livres/{id}` | Détail d'un livre |
| `PATCH` | `/api/livres/{id}` | Modification partielle |
| `DELETE` | `/api/livres/{id}` | Soft delete |
| `GET` | `/api/livres/search` | Recherche (`?q=python&langue=fr`) |
| `GET` | `/api/livres/{id}/disponibilite` | Disponibilité |
| `GET` | `/api/categories` | Liste des catégories |
| `GET` | `/health` | Health check |

```bash
# Lister les livres
curl http://localhost:8003/api/livres

# Rechercher par titre/auteur
curl "http://localhost:8003/api/livres/search?q=python"

# Créer un livre
curl -X POST http://localhost:8003/api/livres \
  -F "titre=Clean Code" -F "auteur=Robert Martin" \
  -F "isbn=9780132350884" -F "langue=en" \
  -F "annee_publication=2008" -F "quantite_totale=3"
```

### Service Utilisateurs — `http://localhost:8002`

| Méthode | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/login/` | Connexion → `access` + `refresh` JWT |
| `POST` | `/api/auth/token/refresh/` | Rafraîchir le token |
| `POST` | `/api/users/` | Créer un utilisateur (public) |
| `GET` | `/api/users/` | Liste des utilisateurs (admin) |
| `GET` | `/api/users/{id}/` | Profil d'un utilisateur |
| `PATCH` | `/api/users/{id}/` | Modifier un utilisateur |
| `PATCH` | `/api/users/{id}/password/` | Changer le mot de passe |
| `DELETE` | `/api/users/{id}/deactivate/` | Désactiver (soft delete) |

```bash
# Connexion
curl -X POST http://localhost:8002/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "mamadou.diallo@dit.sn", "password": "dit2024!"}'
# Réponse : { "access": "...", "refresh": "...", "id": "...", "full_name": "...", "role": "STUDENT" }

# Liste des utilisateurs (admin seulement)
curl http://localhost:8002/api/users/ \
  -H "Authorization: Bearer <access_token>"
```

### Service Emprunts — `http://localhost:8008`

> Auth : cookie `access_token` contenant le JWT (émis par le service utilisateurs).

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/api/emprunts/` | Historique de tous les emprunts |
| `POST` | `/api/emprunts/emprunter/` | Emprunter un livre |
| `POST` | `/api/emprunts/retourner/` | Retourner un livre |
| `POST` | `/api/emprunts/rate/` | Noter un emprunt (1-5) |
| `POST` | `/api/emprunts/notify-users-before-3-days-before-loan-due/` | Rappels J-3 |
| `POST` | `/api/emprunts/notify-users-on-loan-overdue/` | Notifier les retards |

```bash
# Emprunter (avec cookie access_token)
curl -X POST http://localhost:8008/api/emprunts/emprunter/ \
  -H "Content-Type: application/json" \
  -b "access_token=<jwt_token>" \
  -d '{"book_id": "<uuid_livre>", "comment": "Lecture cours IA"}'

# Retourner
curl -X POST http://localhost:8008/api/emprunts/retourner/ \
  -H "Content-Type: application/json" \
  -b "access_token=<jwt_token>" \
  -d '{"loan_id": "<uuid_emprunt>"}'
```

### Service Recommandation — `http://localhost:8004`

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Santé du service |
| `GET` | `/recommendations/{user_id}` | Recommandations personnalisées |
| `POST` | `/train` | Ré-entraîner le modèle |
| `GET` | `/metrics` | Métriques du modèle actuel |
| `GET` | `/popular` | Livres populaires (fallback) |

```bash
# Recommandations pour un utilisateur
curl http://localhost:8004/recommendations/<user_id>

# Ré-entraîner le modèle
curl -X POST http://localhost:8004/train
```

---

## Pipeline DVC — Versioning données & modèle

### Prérequis locaux

```bash
pip install dvc dvc-gdrive pandas scikit-learn joblib
```

### Initialisation (une seule fois)

```bash
# Initialiser DVC dans le dépôt
dvc init

# Configurer le remote Google Drive
dvc remote add -d gdrive_remote gdrive://<folder_id>
dvc remote modify gdrive_remote gdrive_acknowledge_abuse true

git add .dvc/config
git commit -m "config: initialiser DVC avec remote Google Drive"
```

### Export des données d'emprunts

```bash
# Exporter l'historique depuis PostgreSQL
python scripts/export_loans.py

# Versionner avec DVC
dvc add data/loans.csv
git add data/loans.csv.dvc .gitignore
git commit -m "data: exporter historique emprunts v1"
dvc push
```

### Pipeline DVC

Le pipeline est défini dans `dvc.yaml` avec 3 étapes :

```
data/loans.csv → [preprocess] → data/loans_clean.csv
                                      ↓
                               [train] → model/model.pkl
                                              ↓
                                       [evaluate] → metrics/metrics.json
```

```bash
# Reproduire le pipeline complet
dvc repro

# Afficher les métriques
dvc metrics show

# Comparer deux versions du modèle
git checkout v1.0
dvc checkout
dvc metrics show

git checkout v2.0
dvc checkout
dvc metrics show

dvc metrics diff v1.0 v2.0
```

**Rôle de `dvc.lock`** : fichier généré automatiquement par `dvc repro`, il enregistre les hashes MD5 de chaque dépendance et sortie. Il garantit la reproductibilité exacte du pipeline — si les données ou le code n'ont pas changé, `dvc repro` ne ré-exécute pas les étapes concernées.

### Charger la bonne version du modèle

```bash
# Revenir à une version spécifique du modèle
git checkout v1.0
dvc pull model/model.pkl

# Le service recommandation monte le modèle en volume Docker
# il charge automatiquement la version présente dans model/model.pkl
docker compose restart recommandation
```

---

## Versioning Git

### Workflow de branches

```
main                ← production stable
├── develop         ← intégration
│   ├── feature/livres-service
│   ├── feature/utilisateurs-service
│   ├── feature/emprunts-service
│   ├── feature/recommandation-service
│   └── feature/frontend
└── hotfix/*        ← corrections urgentes
```

### Tags de version

```bash
# Lister les versions
git tag -l

# Créer un tag de version
git tag -a v1.0.0 -m "Version initiale — tous les services opérationnels"
git push origin v1.0.0
```

---

## Variables d'environnement

Fichier racine `.env` :

```dotenv
# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres123

# JWT (partagé entre tous les services)
JWT_SECRET_KEY=a-string-secret-at-least-256-bits-long
JWT_ALGORITHM=HS256
JWT_COOKIE_NAME=access_token

# URLs inter-services
SERVICE_LIVRES_URL=http://book-api:8001
SERVICE_UTILISATEURS_URL=http://utilisateurs:8002
SERVICE_EMPRUNTS_URL=http://loans-api:8000
```

---

## Structure du projet

```
bibliotheque-dit/
├── docker-compose.yml          # Orchestration (profils dev/prod)
├── .env                        # Variables d'environnement
├── README.md
│
├── services/
│   ├── livres/                 # Litestar + Piccolo ORM
│   │   ├── Dockerfile
│   │   ├── entrypoint.sh
│   │   ├── seed.py             # 50 livres, 5 catégories
│   │   ├── features/books/     # Controller, schemas, service, tables
│   │   └── core/               # Settings, DB, storage (MinIO)
│   │
│   ├── utilisateurs/           # Django REST Framework + JWT
│   │   ├── Dockerfile
│   │   ├── entrypoint.sh
│   │   └── users/              # Models, views, serializers, URLs
│   │
│   ├── recommandation/         # FastAPI + Scikit-learn (SVD)
│   │   ├── Dockerfile
│   │   ├── app/main.py         # Endpoints: /recommendations, /train
│   │   ├── model/              # model.pkl (volume Docker)
│   │   └── data/               # loans.csv (données d'entraînement)
│   │
│   └── frontend/               # TanStack Start (React) + Bun
│       ├── Dockerfile
│       └── src/features/library/
│
├── emprunts/                   # Django + architecture hexagonale
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── src/loans/
│       ├── app/                # Handlers, domain
│       └── adapters/           # HTTP views, DB, services
│
├── scripts/
│   └── export_loans.py         # Export CSV pour DVC
│
└── dvc/                        # Pipeline DVC
    ├── dvc.yaml                # Définition du pipeline
    ├── dvc.lock                # Hashes de reproductibilité
    ├── preprocess.py
    ├── train.py
    ├── evaluate.py
    └── params.yaml             # Hyperparamètres du modèle
```

---

## Tests des endpoints

### Script de test rapide

```bash
# Health checks
curl http://localhost:8003/health
curl http://localhost:8004/health

# Catalogue livres
curl "http://localhost:8003/api/livres?page_size=5" | python3 -m json.tool

# Recherche
curl "http://localhost:8003/api/livres/search?q=machine+learning"

# Connexion et récupération du token
TOKEN=$(curl -s -X POST http://localhost:8002/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"mamadou.diallo@dit.sn","password":"dit2024!"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access'])")

echo "Token: $TOKEN"

# Recommandations
USER_ID=$(curl -s -X POST http://localhost:8002/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"mamadou.diallo@dit.sn","password":"dit2024!"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

curl "http://localhost:8004/recommendations/$USER_ID"
```

---

## Métriques du modèle ML

Après `dvc repro`, les métriques sont disponibles dans `metrics/metrics.json` :

```json
{
  "rmse": 0.85,
  "mae": 0.67,
  "coverage": 0.73,
  "n_users": 42,
  "n_books": 50
}
```

Comparer deux versions :

```bash
dvc metrics diff HEAD~1 HEAD
```

---

## Technologie

| Service | Framework | ORM | Port |
|---|---|---|---|
| Livres | Litestar 2.x | Piccolo ORM | 8003 |
| Utilisateurs | Django REST Framework | Django ORM | 8002 |
| Emprunts | Django REST Framework | Django ORM | 8008 |
| Recommandation | FastAPI | — | 8004 |
| Frontend | TanStack Start (React) | — | 3000 |
| Base de données | PostgreSQL 16 | — | — |
| Stockage fichiers | MinIO | — | 9090/9091 |
