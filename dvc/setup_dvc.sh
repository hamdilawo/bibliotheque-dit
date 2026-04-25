#!/bin/bash
# =============================================================
# setup_dvc.sh — Initialisation complète du pipeline DVC
# Bibliothèque Numérique DIT — Master 2 IA
# =============================================================
# Usage : bash setup_dvc.sh
# =============================================================

set -e  # Arrêter en cas d'erreur

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║   Pipeline DVC — Bibliothèque DIT                ║"
echo "║   Initialisation                                  ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""

# ── 0. Vérifications ────────────────────────────────────────
echo "[0/6] Vérification des prérequis..."
command -v git  >/dev/null || { echo "ERREUR : git non installé"; exit 1; }
command -v dvc  >/dev/null || { echo "ERREUR : dvc non installé. Lancez : pip install dvc[gdrive]"; exit 1; }
command -v python3 >/dev/null || { echo "ERREUR : python3 non installé"; exit 1; }
echo "  ✓ git, dvc, python3 disponibles"

# ── 1. Initialiser Git ──────────────────────────────────────
echo ""
echo "[1/6] Initialisation Git..."
if [ ! -d ".git" ]; then
    git init
    echo "  ✓ Dépôt Git initialisé"
else
    echo "  ~ Dépôt Git déjà initialisé"
fi

# ── 2. Initialiser DVC ──────────────────────────────────────
echo ""
echo "[2/6] Initialisation DVC..."
if [ ! -d ".dvc" ]; then
    dvc init
    git add .dvc .dvcignore
    git commit -m "chore: initialisation DVC"
    echo "  ✓ DVC initialisé et commité"
else
    echo "  ~ DVC déjà initialisé"
fi

# ── 3. Configurer le remote DVC (Google Drive) ──────────────
echo ""
echo "[3/6] Configuration du remote DVC (Google Drive)..."
echo ""
echo "  → Ouvrez Google Drive et créez un dossier 'dvc-bibliotheque-dit'"
echo "  → Copiez l'ID du dossier depuis l'URL :"
echo "    https://drive.google.com/drive/folders/VOTRE_ID_ICI"
echo ""
read -p "  Collez l'ID du dossier Google Drive : " GDRIVE_ID

if [ -n "$GDRIVE_ID" ]; then
    dvc remote add -d myremote "gdrive://${GDRIVE_ID}"
    dvc remote modify myremote gdrive_acknowledge_abuse true
    git add .dvc/config
    git commit -m "chore: configuration remote DVC Google Drive"
    echo "  ✓ Remote Google Drive configuré : gdrive://${GDRIVE_ID}"
else
    echo "  ! ID vide — remote non configuré. Configurez-le manuellement :"
    echo "    dvc remote add -d myremote gdrive://VOTRE_ID"
fi

# ── 4. Installer les dépendances Python ─────────────────────
echo ""
echo "[4/6] Installation des dépendances Python..."
pip install --quiet dvc[gdrive] pandas numpy scikit-learn joblib pyyaml
echo "  ✓ Dépendances installées"

# ── 5. Exporter les données depuis le service Emprunts ───────
echo ""
echo "[5/6] Export des données d'emprunts..."
mkdir -p data model

if [ ! -f "data/loans.csv" ]; then
    echo "  → Tentative de téléchargement depuis le Service Emprunts..."
    curl -s "http://localhost:8003/api/emprunts/export_csv/" -o data/loans.csv 2>/dev/null || {
        echo "  ! Service Emprunts non disponible → génération automatique via preprocess.py"
    }
fi

# ── 6. Lancer le pipeline DVC ────────────────────────────────
echo ""
echo "[6/6] Exécution du pipeline DVC..."
echo ""
echo "  → Étape 1/3 : Prétraitement..."
python3 preprocess.py

echo "  → Étape 2/3 : Entraînement SVD..."
python3 train.py

echo "  → Étape 3/3 : Évaluation..."
python3 evaluate.py

# ── Versionner les fichiers avec DVC ─────────────────────────
echo ""
echo "Versionnement des fichiers avec DVC..."
dvc add data/loans.csv data/loans_clean.csv model/model.pkl

git add data/loans.csv.dvc data/loans_clean.csv.dvc model/model.pkl.dvc .gitignore
git add dvc.yaml dvc.lock params.yaml metrics.json
git commit -m "feat: pipeline DVC v1 — SVD n_components=10"

echo ""
echo "Push vers le remote DVC..."
dvc push

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║   ✓ Pipeline DVC configuré avec succès !         ║"
echo "╚══════════════════════════════════════════════════╝"
echo ""
echo "Commandes utiles :"
echo "  dvc repro              → rejouer le pipeline"
echo "  dvc metrics show       → afficher les métriques"
echo "  dvc metrics diff       → comparer deux versions"
echo "  dvc dag                → visualiser le pipeline"
echo "  dvc push               → pousser vers Google Drive"
echo "  dvc pull               → récupérer depuis Google Drive"
echo ""
