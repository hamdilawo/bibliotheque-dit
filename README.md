# Bibliotheque Numerique DIT
**Master 2 Intelligence Artificielle - Examen Outils de Versioning**
Duree : 24 Avril -> 15 Mai 2026

---

## Architecture

```
bibliotheque-dit/
+-- services/
|   +-- livres/           # Django REST - port 8001
|   +-- utilisateurs/     # Django REST - port 8002
|   +-- emprunts/         # Django REST - port 8003
|   +-- recommandation/   # FastAPI + SVD - port 8004
|   +-- frontend/         # React - port 3000
+-- dvc/
|   +-- preprocess.py     # Etape 1 : nettoyage des donnees
|   +-- train.py          # Etape 2 : entrainement SVD/KNN
|   +-- evaluate.py       # Etape 3 : metriques RMSE, MAE, Precision@K
|   +-- dvc.yaml          # Definition du pipeline
|   +-- dvc.lock          # Verrouillage des hashes
|   +-- params.yaml       # Hyperparametres versionnes
|   +-- metrics.json      # Resultats d'evaluation
|   +-- EXPERIMENTS.md    # Journal des experiences V1/V2/V3/V4
+-- docker-compose.yml
+-- Jenkinsfile
+-- README.md
```

---

## 1. Lancement avec Docker Compose

### Prerequis
- Docker >= 24.0
- Docker Compose >= 2.20

### Lancer en mode developpement
```bash
# Cloner le depot
git clone https://github.com/hamdilawo/bibliotheque-dit.git
cd bibliotheque-dit

# Copier les variables d'environnement
cp .env.example .env

# Lancer tous les services (hot-reload active)
docker compose --profile dev up --build

# Acces :
#   Frontend          -> http://localhost:3000
#   Service Livres    -> http://localhost:8001/api/docs/
#   Service Utilisateurs -> http://localhost:8002/api/docs/
#   Service Emprunts  -> http://localhost:8003/api/docs/
#   Recommandation    -> http://localhost:8004/docs
```

### Lancer en mode production
```bash
docker compose --profile prod up --build -d
```

---

## 2. Initialisation de la base de donnees

Les migrations Django et le peuplement initial sont declenches
automatiquement au demarrage de chaque conteneur via le `command` defini
dans `docker-compose.yml`. Aucune commande manuelle n'est necessaire.

Volume de donnees peuple au seed :
- **50 livres** repartis sur 5 categories (IA, Informatique, Mathematiques, Sciences, Litterature)
- **30 utilisateurs** : 1 admin, 5 professeurs, 22 etudiants, 2 personnels
- **500 emprunts** generes avec patterns de comportement (chaque utilisateur a une
  categorie favorite, 70 % de ses emprunts y sont, 30 % disperses ailleurs)
- ~ 463 emprunts retournes / 37 en cours / 114 avec retard

**Comptes de demonstration :**

| Email | Mot de passe | Role |
|---|---|---|
| admin@dit.sn | DIT@Admin2026! | Administrateur |
| amadou.diallo@dit.sn | Prof@2026! | Professeur |
| moussa.ba@etu.dit.sn | Etu@2026! | Etudiant |
| bibliothecaire@dit.sn | Pers@2026! | Personnel |

---

## 3. Pipeline DVC

### Installation
```bash
cd dvc/
pip install dvc pandas numpy scikit-learn joblib pyyaml
```

### Configuration du remote (deja faite - pour info)

Le remote DVC est configure sur **Google Drive** (conforme au sujet) :

```bash
dvc remote add -d myremote gdrive://1X-22WFVUs6DUGHB7v6jtitkx3nvbEfVW
dvc remote modify myremote gdrive_acknowledge_abuse true
```

L'authentification utilise un client OAuth Desktop personnel (cree via
Google Cloud Console). Les credentials sont stockes en local (`config.local`,
non commite). Pour reproduire :

1. Creer un projet sur https://console.cloud.google.com
2. Activer l'API Google Drive
3. Creer des credentials OAuth client ID type "Desktop application"
4. Ajouter les credentials en mode local :
   ```bash
   dvc remote modify --local myremote gdrive_client_id "<client_id>"
   dvc remote modify --local myremote gdrive_client_secret "<client_secret>"
   ```
5. Lancer `dvc pull` ou `dvc push` - le navigateur ouvrira la page d'autorisation

### Exporter les donnees depuis le service Emprunts
```bash
curl http://localhost:8003/api/emprunts/export_csv/ -o data/loans.csv
```

### Executer le pipeline complet
```bash
dvc repro
```
Cela execute les 3 etapes dans l'ordre :
1. `preprocess.py` -> `data/loans_clean.csv`
2. `train.py`      -> `model/model.pkl`
3. `evaluate.py`   -> `metrics.json`

### Metriques du modele de production (`model-prod` = `model-v4`)

```bash
dvc metrics show
```

| Metrique | Valeur |
|---|---:|
| RMSE | 1.5315 |
| MAE | 1.1197 |
| Precision@5 | 22.7 % |
| Rappel@5 | 67.8 % |
| Variance expliquee SVD | 87.15 % |
| Couverture catalogue | 84 % |

Sur un dataset de 30 utilisateurs * 50 livres * 463 emprunts retournes
(`hyperparams.n_components = 15`).

### Comparer les versions du modele
```bash
# Comparer V3 (petit dataset) vs V4 (dataset enrichi)
dvc metrics diff model-v3 model-v4

# Comparer V1 (sur-parametre) vs V3 (compromis)
dvc metrics diff model-v1 model-v3
```

L'historique complet des experiences et les analyses sont consignes dans
[`dvc/EXPERIMENTS.md`](dvc/EXPERIMENTS.md).

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

### Role de dvc.lock
`dvc.lock` est genere par `dvc repro`. Il enregistre les **hashes MD5** de chaque fichier d'entree et de sortie a un instant donne. Cela permet de :
- **Reproduire exactement** le meme pipeline (memes donnees, meme modele)
- **Detecter** si une etape doit etre re-executee (si un hash change)
- **Auditer** l'historique des experiences via Git

```bash
# Rollback vers une version precedente
git checkout model-v1 -- dvc.lock params.yaml
dvc pull   # recupere model.pkl correspondant
```

### Versionner et pousser le modele
Le `model.pkl` est deja declare comme output du stage `train` dans `dvc.yaml`,
donc DVC le tracke automatiquement a chaque `dvc repro` (pas besoin de
`dvc add` manuel). Pour publier sur le remote :

```bash
dvc push   # envoie vers le remote local configure
```

### Recuperer un modele versionne

**Option 1 - Recuperer l'artefact depuis le remote :**
```bash
git checkout model-v3   # ou model-v1, model-v2, model-v4, model-prod
dvc pull
dvc metrics show
```

**Option 2 - Re-generer via le pipeline (plus propre, demontre la reproductibilite) :**
```bash
git checkout model-v3
dvc repro       # regenere un model.pkl bit-pour-bit identique
                # grace aux hashes de dvc.lock + random_state=42
dvc metrics show
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
curl http://localhost:8004/recommandation/1

# Livres similaires a partir d'un ISBN de reference
curl "http://localhost:8004/livre_similaire?ref_isbn=9780134610993&n=5"

# Re-entrainer le modele
curl -X POST http://localhost:8004/train

# Metriques du modele
curl http://localhost:8004/metric
```

---

## 5. Workflow Git

```
main
 \-- develop
      |-- feature/service-livres
      |-- feature/service-utilisateurs
      |-- feature/service-emprunts
      |-- feature/service-recommandation
      |-- feature/frontend-react
      \-- feature/pipeline-dvc
```

Tags de versions du modele ML (par ordre chronologique) :

| Tag | Algorithme | n_components | Dataset | RMSE | Statut |
|---|---|---:|---|---:|---|
| `model-v1` | SVD | 10 | 6x7 / 57 emprunts | 1.5665 | sur-parametre |
| `model-v2` | SVD | 2 | 6x7 / 57 emprunts | 1.5765 | sous-parametre |
| `model-v3` | SVD | 4 | 6x7 / 57 emprunts | 1.5657 | meilleur sur petit dataset |
| `model-v4` | SVD | 15 | 30x50 / 463 emprunts | **1.5315** | **production** |
| `model-prod` | (alias de `model-v4`) | | | | pointeur production |
| `v1.0.0` | (release applicative) | | | | merge dans main |

Voir [`dvc/EXPERIMENTS.md`](dvc/EXPERIMENTS.md) pour l'analyse detaillee
des 4 experiences et la justification du choix de V4.

---

## Changelog v1.0.0
- Services Livres, Utilisateurs, Emprunts, Recommandation, Frontend
- Pipeline DVC : preprocess -> train (SVD) -> evaluate
- Docker Compose profils dev/prod
