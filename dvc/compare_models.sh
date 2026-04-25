#!/bin/bash
# =============================================================
# compare_models.sh — Comparer deux versions du modèle ML
# =============================================================
# Usage : bash compare_models.sh
#
# Workflow :
#   1. Version v1 : n_components=10 (déjà entraîné)
#   2. On modifie params.yaml → n_components=20
#   3. dvc repro → ré-entraînement automatique
#   4. dvc metrics diff → comparaison des métriques
# =============================================================

set -e

echo ""
echo "╔══════════════════════════════════════════════════╗"
echo "║   Comparaison de modèles — DVC Experiments       ║"
echo "╚══════════════════════════════════════════════════╝"

# ── Version v1 : déjà entraîné avec n_components=10 ─────────
echo ""
echo "[V1] Métriques actuelles (n_components=10) :"
dvc metrics show
git tag -f model-v1
echo "  ✓ Tag git 'model-v1' créé"

# ── Version v2 : n_components=20 ────────────────────────────
echo ""
echo "[V2] Modification des hyperparamètres : n_components=10 → 20"

# Modifier params.yaml
python3 - << 'PYEOF'
import yaml
with open('params.yaml', 'r') as f:
    params = yaml.safe_load(f)
params['train']['n_components'] = 20
with open('params.yaml', 'w') as f:
    yaml.dump(params, f, default_flow_style=False)
print("  params.yaml mis à jour : n_components=20")
PYEOF

echo ""
echo "[V2] Ré-entraînement avec dvc repro..."
dvc repro

echo ""
echo "[V2] Métriques après modification :"
dvc metrics show

git add params.yaml dvc.lock metrics.json
git commit -m "experiment: SVD n_components=20 — test amélioration"
git tag -f model-v2
echo "  ✓ Tag git 'model-v2' créé"

# ── Comparaison ──────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════"
echo "  COMPARAISON  model-v1  vs  model-v2"
echo "════════════════════════════════════════════"
dvc metrics diff model-v1 model-v2
echo ""

# ── Sélectionner le meilleur modèle ──────────────────────────
echo "Sélection automatique du meilleur modèle (RMSE le plus bas)..."
python3 - << 'PYEOF'
import json, subprocess

def get_metrics(tag):
    result = subprocess.run(
        ['git', 'show', f'{tag}:metrics.json'],
        capture_output=True, text=True
    )
    return json.loads(result.stdout) if result.returncode == 0 else {}

v1 = get_metrics('model-v1')
v2 = get_metrics('model-v2')

rmse_v1 = v1.get('rmse', 9999)
rmse_v2 = v2.get('rmse', 9999)

print(f"\n  model-v1 → RMSE={rmse_v1}, Précision@5={v1.get('precision_at_5', 0)}")
print(f"  model-v2 → RMSE={rmse_v2}, Précision@5={v2.get('precision_at_5', 0)}")

if rmse_v1 <= rmse_v2:
    print(f"\n  ✓ Meilleur modèle : model-v1 (RMSE plus bas)")
    print("    → Rollback : git checkout model-v1 -- model/model.pkl")
else:
    print(f"\n  ✓ Meilleur modèle : model-v2 (RMSE plus bas)")
    print("    → Ce modèle est déjà actif.")
PYEOF

echo ""
echo "Pour revenir à une version précédente :"
echo "  git checkout model-v1 -- model/model.pkl dvc.lock params.yaml"
echo "  dvc pull"
echo ""
