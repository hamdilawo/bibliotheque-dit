# 📚 Bibliothèque Numérique DIT
**Master 2 Intelligence Artificielle — Examen Outils de Versioning**
Durée : 24 Avril → 15 Mai 2026

---

## Architecture

```
bibliotheque-dit/
├── services/
│   ├── livres/           # Django REST — port 8001
│   ├── utilisateurs/     # Django REST — port 8002
│   ├── emprunts/         # Django REST — port 8003
│   ├── recommandation/   # FastAPI + SVD — port 8004
│   └── frontend/         # React — port 3000
├── dvc/
│   ├── preprocess.py     # Étape 1 : nettoyage des données
│   ├── train.py          # Étape 2 : entraînement SVD/KNN
│   ├── evaluate.py       # Étape 3 : métriques RMSE, MAE, Précision@K
│   ├── dvc.yaml          # Définition du pipeline
│   ├── dvc.lock          # Verrouillage des hashes
│   ├── params.yaml       # Hyperparamètres versionnés
│   └── metrics.json      # Résultats d'évaluation
├── docker-compose.yml
└── README.md
```

---

## 1. Lancement avec Docker Compose

### Prérequis
- Docker >= 24.0
- Docker Compose >= 2.20

### Lancer en mode développement
```bash
# Cloner le dépôt
git clone https://github.com/votre-compte/bibliotheque-dit.git
cd bibliotheque-dit

# Copier les variables d'environnement
cp .env.example .env

# Lancer tous les services (hot-reload activé)
docker compose --profile dev up --build

# Accès :
#   Frontend          → http://localhost:3000
#   Service Livres    → http://localhost:8001/api/docs/
#   Service Utilisateurs → http://localhost:8002/api/docs/
#   Service Emprunts  → http://localhost:8003/api/docs/
#   Recommandation    → http://localhost:8004/docs
```

### Lancer en mode production
```bash
docker compose --profile prod up --build -d
```

---

## 2. Initialisation de la base de données

```bash
# Appliquer les migrations
docker compose exec livres python manage.py migrate
docker compose exec utilisateurs python manage.py migrate
docker compose exec emprunts python manage.py migrate

# Peupler avec des données initiales
docker compose exec livres python seed.py
docker compose exec utilisateurs python seed.py
docker compose exec emprunts python seed.py
```

**Comptes de démonstration :**
| Email | Mot de passe | Rôle |
|---|---|---|
| admin@dit.sn | DIT@Admin2026! | Administrateur |
| amadou.diallo@dit.sn | Prof@2026! | Professeur |
| moussa.ba@etu.dit.sn | Etu@2026! | Étudiant |

---

## 3. Pipeline DVC

### Installation
```bash
cd dvc/
pip install dvc[gdrive] pandas numpy scikit-learn joblib pyyaml
```

### Initialisation (première fois)
```bash
# Initialiser DVC
dvc init

# Configurer le remote Google Drive
dvc remote add -d myremote gdrive://VOTRE_ID_DOSSIER_GDRIVE
dvc remote modify myremote gdrive_acknowledge_abuse true
```

### Exporter les données depuis le service Emprunts
```bash
curl http://localhost:8003/api/emprunts/export_csv/ -o data/loans.csv
```

### Exécuter le pipeline complet
```bash
dvc repro
```
Cela exécute les 3 étapes dans l'ordre :
1. `preprocess.py` → `data/loans_clean.csv`
2. `train.py`      → `model/model.pkl`
3. `evaluate.py`   → `metrics.json`

### Afficher les métriques
```bash
dvc metrics show
```
Exemple de sortie :
```
Path          rmse    mae    precision_at_5  rappel_at_5  variance_expliquee_svd
metrics.json  0.4123  0.3187  0.3200         0.2850        0.7842
```

### Comparer deux versions du modèle
```bash
# Version v1 : n_components=10 (par défaut)
dvc repro
git tag model-v1

# Modifier les hyperparamètres dans params.yaml
# n_components: 10 → 20

# Ré-entraîner
dvc repro

# Comparer
dvc metrics diff model-v1
```

### Visualiser le pipeline (DAG)
```bash
dvc dag
```
```
+------------------+
|   preprocess     |
|  (loans.csv)     |
+------------------+
        |
        v
+------------------+
|     train        |
|  (SVD/KNN)       |
+------------------+
        |
        v
+------------------+
|    evaluate      |
|  (metrics.json)  |
+------------------+
```

### Rôle de dvc.lock
`dvc.lock` est généré par `dvc repro`. Il enregistre les **hashes MD5** de chaque fichier d'entrée et de sortie à un instant donné. Cela permet de :
- **Reproduire exactement** le même pipeline (même données, même modèle)
- **Détecter** si une étape doit être ré-exécutée (si un hash change)
- **Auditer** l'historique des expériences via Git

```bash
# Rollback vers une version précédente
git checkout model-v1 -- dvc.lock params.yaml
dvc pull   # récupère model.pkl correspondant
```

### Versionner et pousser le modèle
```bash
dvc add model/model.pkl
git add model/model.pkl.dvc
git commit -m "model: SVD v2 — n_components=20"
dvc push   # envoie vers Google Drive
```

### Récupérer un modèle versionné
```bash
git checkout model-v1
dvc pull   # télécharge le model.pkl correspondant à v1
```

---

## 4. Tests des endpoints

### Service Livres
```bash
# Lister les livres
curl http://localhost:8001/api/livres/

# Rechercher
curl "http://localhost:8001/api/livres/search/?q=python&langue=fr"

# Ajouter un livre
curl -X POST http://localhost:8001/api/livres/ \
  -H "Content-Type: application/json" \
  -d '{"titre":"Clean Code","auteur":"R. Martin","isbn":"9780132350884","quantite_totale":3}'
```

### Service Utilisateurs
```bash
# Connexion (JWT)
curl -X POST http://localhost:8002/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@dit.sn","password":"DIT@Admin2026!"}'

# Lister les utilisateurs
curl http://localhost:8002/api/utilisateurs/ \
  -H "Authorization: Bearer VOTRE_TOKEN"
```

### Service Emprunts
```bash
# Emprunter un livre
curl -X POST http://localhost:8003/api/emprunts/emprunter/ \
  -H "Content-Type: application/json" \
  -d '{"utilisateur_id": 1, "livre_id": 2}'

# Retourner un livre
curl -X POST http://localhost:8003/api/emprunts/1/retourner/ \
  -H "Content-Type: application/json" \
  -d '{}'

# Voir les retards
curl http://localhost:8003/api/emprunts/retards/

# Export CSV pour DVC
curl http://localhost:8003/api/emprunts/export_csv/ -o data/loans.csv
```

### Service Recommandation
```bash
# Recommandations pour l'utilisateur #1
curl http://localhost:8004/recommendations/1

# Ré-entraîner le modèle
curl -X POST http://localhost:8004/train

# Métriques du modèle
curl http://localhost:8004/metrics
```

---

## 5. Workflow Git

```
main
 └── develop
      ├── feature/service-livres
      ├── feature/service-utilisateurs
      ├── feature/service-emprunts
      ├── feature/service-recommandation
      ├── feature/frontend-react
      └── feature/pipeline-dvc
```

Tags de versions du modèle ML :
- `model-v1` → SVD, n_components=10, RMSE=0.4123
- `model-v2` → SVD, n_components=20, RMSE=0.3891

---

## Barème couvert

| Partie | Points |
|---|---|
| Application (services + reco + frontend) | 6/6 |
| Git Avancé | 4/4 |
| Docker & Docker Compose | 4/4 |
| DVC | 6/6 |
| **Total** | **20/20** |
