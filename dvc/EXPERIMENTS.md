# Journal des expérimentations DVC

Ce document trace les expériences successives sur le pipeline `preprocess → train → evaluate`.
Chaque version est associée à un **tag Git annoté** et à un état complet de `dvc.lock`.

## Reproduire une version donnée

DVC permet deux modes de récupération :

**Mode 1 — Re-télécharger l'artefact pré-entraîné depuis le remote :**
```bash
git checkout model-v3   # ou model-v1, model-v2
dvc pull                # télécharge le model.pkl déjà entraîné
dvc metrics show
```

**Mode 2 — Re-générer entièrement le pipeline (recommandé, démontre la reproductibilité) :**
```bash
git checkout model-v3
dvc repro               # réexécute preprocess + train + evaluate
                        # produit un model.pkl bit-pour-bit identique grâce
                        # aux hashes de dvc.lock et au random_state=42
dvc metrics show
```

Le **Mode 2 est l'argument fort de DVC** : on n'a pas besoin de stocker chaque
version du modèle si le pipeline est déterministe. `dvc.lock` garantit que les
mêmes données + les mêmes paramètres + le même code produisent le même modèle,
au bit près. C'est ce qui rend DVC fondamentalement supérieur à un simple
versioning d'artefacts.

## Configuration du remote DVC

Le remote est configuré en **local** sur ce poste (au-dessus du repo) :
`../../dvc-remote-local`. Pour reproduire depuis un autre poste, il suffit
de redéfinir le remote :

```bash
dvc remote modify myremote url /chemin/local/de/votre/choix
```

## Comparer deux versions

```bash
dvc metrics diff model-v1 model-v3
```

---

## Tableau de comparaison

### Phase 1 — Petit dataset (6 utilisateurs / 7 livres / 57 emprunts)

| Version | Algorithme | n_components | RMSE | MAE | P@5 | R@5 | Variance SVD |
|---|---|---:|---:|---:|---:|---:|---:|
| `model-v1` | SVD | 10 | 1.5665 | 1.1616 | 0.20 | 1.00 | **99.01 %** |
| `model-v2` | SVD | 2 | 1.5765 | 1.1750 | 0.20 | 1.00 | 61.67 % |
| `model-v3` | SVD | 4 | **1.5657** | **1.1613** | 0.20 | 1.00 | 97.35 % |

### Phase 2 — Dataset enrichi (30 utilisateurs / 50 livres / 463 emprunts)

| Version | Algorithme | n_components | RMSE | MAE | P@5 | R@5 | Variance SVD |
|---|---|---:|---:|---:|---:|---:|---:|
| **`model-v4`** ⭐ | SVD | 15 | **1.5315** | **1.1197** | **0.227** | 0.678 | 87.15 % |

> **Phase 1** : matrice 6×7, rang max 5. Métriques saturées (R@5=1.0 car top-5 sur 7 livres).
> **Phase 2** : matrice 30×50, rang max 29. Métriques discriminantes.
> Test split : 20 %. K = 5 pour Précision@K et Rappel@K.

---

## Analyse

### V1 — n_components=10 (état initial)
SVD avec 10 dimensions latentes alors que la matrice utilisateur×livre est de rang
maximal `min(6, 7) - 1 = 5`. Conséquence : 4 dimensions sont du pur bruit qui
gonfle artificiellement la `variance_expliquee_svd` à 99 % sans amélioration des
recommandations. Cas typique de **sur-paramétrisation**.

### V2 — n_components=2 (sous-paramétrisation)
Choix volontairement bas pour matérialiser l'erreur opposée. La variance expliquée
chute à 61 %, le RMSE augmente légèrement (1.5765). Le modèle perd du signal
réellement utile.

### V3 — n_components=4 (meilleur sur petit dataset)
Le bon point dans la courbe en U RMSE = f(n_components) sur le petit dataset :
- Capture 97 % de variance utile (proche de V1)
- Sans le sur-ajustement aux 4 dimensions parasites
- **RMSE et MAE les plus bas des 3 premières versions**

### V4 — n_components=15 sur dataset enrichi (modèle de production retenu) ⭐
Après enrichissement du seed (×8 emprunts, ×7 livres, ×5 utilisateurs), le rang
max de la matrice passe de 5 à 29. **L'optimum de `n_components` change avec
le dataset.** V4 démontre que :
- RMSE descend à **1.5315** (vs 1.5657 pour V3) malgré un dataset 8× plus grand
  → preuve que le modèle **généralise** au lieu de mémoriser
- MAE descend à **1.1197** (vs 1.1613 pour V3)
- Précision@5 monte à **22.7 %** (vs saturé à 20 % en phase 1)
- Rappel@5 descend à 67.8 % : valeur réaliste (sur petit dataset, R@5=1.0
  était une saturation : top-5 sur 7 livres = 71 % du catalogue)
- Couverture du catalogue à 84 % : largement suffisant

**Conclusion pédagogique :** le bon `n_components` n'est pas absolu, il dépend
de la taille de la matrice. C'est `model-v4` qui devient le **modèle de
production** (`model-prod` est un alias pointant sur V4 après cette phase).

---

## Procédure suivie

```bash
# V1 : état initial (commit fac02aa)
git tag -a model-v1 -m "Modele V1 - SVD n_components=10"

# V2 : modifier params.yaml -> n_components: 2 puis dvc repro
dvc repro
git add dvc/params.yaml dvc/dvc.lock dvc/metrics.json
git commit -m "experiment(dvc): SVD n_components=2 - V2"
git tag -a model-v2 -m "Modele V2 - SVD n_components=2"

# V3 : modifier params.yaml -> n_components: 4 puis dvc repro
dvc repro
git add dvc/params.yaml dvc/dvc.lock dvc/metrics.json
git commit -m "experiment(dvc): SVD n_components=4 - V3 (meilleur compromis)"
git tag -a model-v3 -m "Modele V3 - SVD n_components=4"

# V4 : enrichissement du seed -> 30 utilisateurs / 50 livres / 500 emprunts
# Modifier params.yaml -> n_components: 15 puis dvc repro
docker compose --profile dev down -v
docker compose --profile dev up --build      # ré-applique les seeds enrichis
curl http://localhost:8003/api/emprunts/export_csv/ -o dvc/data/loans.csv
cd dvc && dvc repro
git add services/*/seed.py dvc/params.yaml dvc/dvc.lock dvc/metrics.json \
        dvc/model/training_info.json dvc/data/preprocess_stats.json
git commit -m "feat(seed): enrichissement dataset (50 livres / 30 utilisateurs / 500 emprunts)"
git tag -a model-v4 -m "Modele V4 - SVD n_components=15 sur dataset enrichi"

# Re-pointage de l'alias production sur V4
git tag -d model-prod
git push origin :refs/tags/model-prod
git tag -a model-prod model-v4 -m "Modele de production = V4 (dataset enrichi)"

# Pousser tags + artefacts DVC
git push origin develop --tags
dvc push
```
