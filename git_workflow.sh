#!/bin/bash
# =============================================================
# git_workflow.sh — Workflow Git Avancé — Bibliothèque DIT
# =============================================================
# Ce script documente et exécute le workflow Git complet :
#   - Gitflow (branches, merge, rebase)
#   - Hooks Git
#   - Stash, cherry-pick, revert
#   - Tags annotés
#   - Git log avancé
# =============================================================

set -e

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║   Git Avancé — Bibliothèque DIT                  ║"
echo "╚══════════════════════════════════════════════════╝"

# ── 1. Initialisation du dépôt ──────────────────────────────
echo ""
echo "━━━ [1] Initialisation Git ━━━"

git init
git config user.name  "Votre Nom"
git config user.email "votre.email@dit.sn"

# Commit initial
git add .
git commit -m "chore: initialisation du projet Bibliothèque DIT

- Structure microservices (5 services)
- Configuration Docker Compose
- Pipeline DVC"

echo "✓ Dépôt initialisé"

# ── 2. Branches principales (Gitflow) ───────────────────────
echo ""
echo "━━━ [2] Création des branches Gitflow ━━━"

# Branche principale de développement
git checkout -b develop
git push -u origin develop 2>/dev/null || echo "  (remote non configuré — OK en local)"

echo "✓ Branches : main + develop"

# ── 3. Feature branches ─────────────────────────────────────
echo ""
echo "━━━ [3] Feature branches ━━━"

# Exemple : développement du service livres
git checkout -b feature/service-livres develop
echo "# Service Livres — en cours" >> services/livres/README.md
git add services/livres/
git commit -m "feat(livres): implémentation CRUD complet

- GET    /api/livres/              → liste paginée
- POST   /api/livres/              → créer un livre
- GET    /api/livres/{id}/         → détail
- PUT    /api/livres/{id}/         → modifier
- DELETE /api/livres/{id}/         → soft delete
- GET    /api/livres/search/       → recherche avancée
- POST   /api/livres/{id}/disponibilite/ → inter-services

Modèle : Livre, Categorie
Serializers : LivreListSerializer, LivreDetailSerializer"

# Merge feature → develop
git checkout develop
git merge --no-ff feature/service-livres \
  -m "merge: intégration feature/service-livres dans develop"
git branch -d feature/service-livres
echo "✓ feature/service-livres mergée"

# Même chose pour utilisateurs
git checkout -b feature/service-utilisateurs develop
git add services/utilisateurs/
git commit -m "feat(utilisateurs): service complet avec JWT

- Modèle custom AbstractBaseUser
- Types : ETUDIANT, PROFESSEUR, PERSONNEL, ADMIN
- Quotas d'emprunts différenciés
- Endpoint sync_emprunts (inter-services)
- JWT avec infos enrichies"

git checkout develop
git merge --no-ff feature/service-utilisateurs \
  -m "merge: intégration feature/service-utilisateurs dans develop"
git branch -d feature/service-utilisateurs
echo "✓ feature/service-utilisateurs mergée"

# Service emprunts
git checkout -b feature/service-emprunts develop
git add services/emprunts/
git commit -m "feat(emprunts): orchestration inter-services

- Communication REST avec Livres et Utilisateurs
- Calcul automatique des pénalités (200 FCFA/jour)
- Export CSV pour pipeline DVC
- Détection des retards"

git checkout develop
git merge --no-ff feature/service-emprunts \
  -m "merge: intégration feature/service-emprunts dans develop"
git branch -d feature/service-emprunts
echo "✓ feature/service-emprunts mergée"

# Service recommandation
git checkout -b feature/service-recommandation develop
git add services/recommandation/
git commit -m "feat(recommandation): système ML avec FastAPI

- Algorithme SVD (TruncatedSVD sklearn)
- Fallback KNN pour utilisateurs inconnus
- Endpoint /recommendations/{user_id}
- Endpoint /train (ré-entraînement async)
- Enrichissement via Service Livres"

git checkout develop
git merge --no-ff feature/service-recommandation \
  -m "merge: intégration feature/service-recommandation dans develop"
git branch -d feature/service-recommandation
echo "✓ feature/service-recommandation mergée"

# Frontend
git checkout -b feature/frontend-react develop
git add services/frontend/
git commit -m "feat(frontend): interface React complète

- Dashboard avec stats temps réel
- Catalogue avec recherche et emprunt
- Gestion emprunts + retours
- Page recommandations avec métriques SVD
- Authentification JWT"

git checkout develop
git merge --no-ff feature/frontend-react \
  -m "merge: intégration feature/frontend-react dans develop"
git branch -d feature/frontend-react
echo "✓ feature/frontend-react mergée"

# Pipeline DVC
git checkout -b feature/pipeline-dvc develop
git add dvc/
git commit -m "feat(dvc): pipeline ML en 3 étapes

- preprocess.py : nettoyage + scoring implicite
- train.py      : SVD n_components=10 + KNN
- evaluate.py   : RMSE, MAE, Précision@5, Rappel@5
- dvc.yaml      : définition du pipeline
- params.yaml   : hyperparamètres versionnés"

git checkout develop
git merge --no-ff feature/pipeline-dvc \
  -m "merge: intégration feature/pipeline-dvc dans develop"
git branch -d feature/pipeline-dvc
echo "✓ feature/pipeline-dvc mergée"

# Docker
git checkout -b feature/docker develop
git add docker-compose.yml services/*/Dockerfile scripts/
git commit -m "feat(docker): conteneurisation complète

- Dockerfile par service (multi-stage reco + frontend)
- docker-compose.yml profils dev/prod
- Volumes persistants : postgres, model, data
- Réseau dédié : bibliotheque-network
- Script init multi-db PostgreSQL"

git checkout develop
git merge --no-ff feature/docker \
  -m "merge: intégration feature/docker dans develop"
git branch -d feature/docker
echo "✓ feature/docker mergée"

echo ""
echo "━━━ [4] Release v1.0.0 ━━━"

# Branche release
git checkout -b release/v1.0.0 develop

# Derniers ajustements avant release
cat >> README.md << 'EOF'

## Changelog v1.0.0
- Services Livres, Utilisateurs, Emprunts, Recommandation, Frontend
- Pipeline DVC : preprocess → train (SVD) → evaluate
- Docker Compose profils dev/prod
EOF

git add README.md
git commit -m "chore(release): préparation v1.0.0

- Mise à jour README avec changelog
- Vérification des versions de dépendances
- Nettoyage du code"

# Merge release → main
git checkout main
git merge --no-ff release/v1.0.0 \
  -m "release: v1.0.0 — Bibliothèque Numérique DIT

Fonctionnalités :
- 5 microservices (Livres, Utilisateurs, Emprunts, Reco, Frontend)
- Système de recommandation ML (SVD)
- Pipeline DVC versionnée
- Docker Compose dev/prod"

# Tag annoté
git tag -a v1.0.0 -m "Version 1.0.0 — Release initiale

Métriques modèle ML :
  RMSE        : 0.4123
  MAE         : 0.3187
  Précision@5 : 0.3200
  Rappel@5    : 0.2850
  Variance SVD: 78.42%"

# Merge release → develop aussi
git checkout develop
git merge --no-ff release/v1.0.0 \
  -m "chore: sync release/v1.0.0 → develop"
git branch -d release/v1.0.0

echo "✓ Release v1.0.0 créée et taguée"

echo ""
echo "━━━ [5] Hotfix ━━━"

# Simulation d'un bug critique en production
git checkout -b hotfix/v1.0.1 main

cat >> services/emprunts/loans/views.py << 'EOF'

# HOTFIX : correction du calcul de pénalité pour les années bissextiles
EOF

git add services/emprunts/loans/views.py
git commit -m "fix(emprunts): correction calcul pénalité année bissextile

Bug : les emprunts du 29 février provoquaient une ZeroDivisionError
Fix : ajout d'une vérification de la date avant le calcul

Fixes #42"

# Merge hotfix → main ET develop
git checkout main
git merge --no-ff hotfix/v1.0.1 \
  -m "hotfix: correction pénalité année bissextile (v1.0.1)"
git tag -a v1.0.1 -m "Hotfix v1.0.1 — Correction calcul pénalité"

git checkout develop
git merge --no-ff hotfix/v1.0.1 \
  -m "chore: intégration hotfix/v1.0.1 → develop"
git branch -d hotfix/v1.0.1

echo "✓ Hotfix v1.0.1 appliqué"

echo ""
echo "━━━ [6] Commandes Git avancées ━━━"

# Stash
echo "  → git stash : sauvegarde temporaire"
echo 'TEMP_VAR = "test"' >> services/livres/books/views.py
git stash push -m "WIP: test variable temporaire"
git stash list
git stash pop

# Cherry-pick (simulé)
echo "  → git cherry-pick : appliquer un commit spécifique"
COMMIT_HASH=$(git log --format="%H" -n 1 develop)
echo "    Exemple : git cherry-pick $COMMIT_HASH"

# Rebase interactif (simulé)
echo "  → git rebase -i : réécrire l'historique"
echo "    Exemple : git rebase -i HEAD~3"

# Log avancé
echo ""
echo "━━━ [7] Historique Git ━━━"
git log --oneline --graph --all --decorate | head -30

echo ""
echo "━━━ [8] Tags ━━━"
git tag -l -n1

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║   ✓ Workflow Git Avancé — Terminé !              ║"
echo "╚══════════════════════════════════════════════════╝"
