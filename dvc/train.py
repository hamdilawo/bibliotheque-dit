"""
Pipeline DVC — Étape 2 : Entraînement du modèle
================================================
Entrée  : data/loans_clean.csv
Sortie  : model/model.pkl

Algorithme : SVD (TruncatedSVD) + fallback KNN (NearestNeighbors)
Exécution  : python train.py
"""
import pandas as pd
import numpy as np
import joblib
import json
import logging
from pathlib import Path
from sklearn.decomposition import TruncatedSVD
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import normalize
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO, format='%(asctime)s — %(levelname)s — %(message)s')
logger = logging.getLogger(__name__)

INPUT_PATH  = Path('data/loans_clean.csv')
MODEL_PATH  = Path('model/model.pkl')
PARAMS_PATH = Path('params.yaml')


def charger_params() -> dict:
    """Charge les hyperparamètres depuis params.yaml."""
    try:
        import yaml
        with open(PARAMS_PATH) as f:
            return yaml.safe_load(f).get('train', {})
    except Exception:
        logger.warning("params.yaml introuvable, utilisation des valeurs par défaut.")
        return {}


def construire_matrice(df: pd.DataFrame):
    """Construit la matrice utilisateur × livre avec scores implicites."""
    logger.info("Construction de la matrice utilisateur × livre...")

    # Agréger les scores par paire (utilisateur, livre)
    df_agg = df.groupby(['utilisateur_id', 'livre_id'])['score'].sum().reset_index()

    # Pivot en matrice dense
    matrice_df = df_agg.pivot(
        index='utilisateur_id',
        columns='livre_id',
        values='score'
    ).fillna(0)

    user_ids  = list(matrice_df.index)
    livre_ids = list(matrice_df.columns)
    matrice   = matrice_df.values.astype(float)

    logger.info(f"  Matrice : {len(user_ids)} utilisateurs × {len(livre_ids)} livres")
    logger.info(f"  Densité : {np.count_nonzero(matrice) / matrice.size:.2%}")

    return matrice, user_ids, livre_ids


def entrainer_svd(matrice: np.ndarray, n_components: int):
    """Entraîne le modèle SVD."""
    logger.info(f"Entraînement SVD (n_components={n_components})...")
    n_comp = min(n_components, min(matrice.shape) - 1)
    svd = TruncatedSVD(n_components=n_comp, n_iter=10, random_state=42)
    user_factors = svd.fit_transform(matrice)
    user_factors = normalize(user_factors)

    variance = float(svd.explained_variance_ratio_.sum())
    logger.info(f"  Variance expliquée : {variance:.2%}")
    return svd, user_factors, variance


def entrainer_knn(matrice: np.ndarray, n_neighbors: int):
    """Entraîne un modèle KNN pour la similarité entre utilisateurs."""
    logger.info(f"Entraînement KNN (n_neighbors={n_neighbors})...")
    knn = NearestNeighbors(
        n_neighbors=min(n_neighbors, matrice.shape[0]),
        metric='cosine',
        algorithm='brute',
    )
    knn.fit(matrice)
    logger.info("  KNN entraîné.")
    return knn


def evaluer_couverture(matrice: np.ndarray, user_factors: np.ndarray,
                        user_ids: list, livre_ids: list, n: int = 5) -> float:
    """
    Calcule la couverture du catalogue :
    proportion de livres recommandés au moins une fois sur l'ensemble des utilisateurs.
    """
    livres_recommandes = set()
    for idx in range(len(user_ids)):
        vecteur = user_factors[idx]
        similarites = user_factors @ vecteur
        similarites[idx] = 0
        top_users = np.argsort(similarites)[::-1][:5]
        scores = np.zeros(len(livre_ids))
        for u in top_users:
            scores += similarites[u] * matrice[u]
        # Exclure déjà lus
        for i, v in enumerate(matrice[idx]):
            if v > 0:
                scores[i] = 0
        top_n = np.argsort(scores)[::-1][:n]
        livres_recommandes.update(top_n)

    couverture = len(livres_recommandes) / len(livre_ids)
    logger.info(f"  Couverture catalogue : {couverture:.2%}")
    return round(couverture, 4)


def main():
    logger.info("=== Entraînement DVC — Début ===")

    # Charger les paramètres
    params = charger_params()
    n_components = params.get('n_components', 10)
    n_neighbors  = params.get('n_neighbors', 5)
    algorithme   = params.get('algorithme', 'svd')

    # Charger les données
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Fichier introuvable : {INPUT_PATH}. Lancez preprocess.py d'abord.")

    df = pd.read_csv(INPUT_PATH)
    logger.info(f"Données chargées : {len(df)} lignes")

    # Construire la matrice
    matrice, user_ids, livre_ids = construire_matrice(df)

    # Entraîner SVD
    svd, user_factors, variance_expliquee = entrainer_svd(matrice, n_components)

    # Entraîner KNN (en supplément)
    knn = entrainer_knn(matrice, n_neighbors)

    # Couverture
    couverture = evaluer_couverture(matrice, user_factors, user_ids, livre_ids)

    # Assembler l'objet modèle
    model = {
        'svd': svd,
        'knn': knn,
        'user_factors': user_factors,
        'matrice': matrice,
        'user_ids': user_ids,
        'livre_ids': livre_ids,
        'algorithme': algorithme,
        'params': {
            'n_components': n_components,
            'n_neighbors': n_neighbors,
        },
        'training_info': {
            'n_utilisateurs': len(user_ids),
            'n_livres': len(livre_ids),
            'n_emprunts': len(df),
            'variance_expliquee': round(variance_expliquee, 4),
            'couverture': couverture,
        },
    }

    # Sauvegarder
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    logger.info(f"Modèle sauvegardé : {MODEL_PATH}")

    # Sauvegarder les infos d'entraînement pour evaluate.py
    with open('model/training_info.json', 'w') as f:
        json.dump(model['training_info'], f, indent=2)

    logger.info("=== Entraînement DVC — Terminé ===")
    logger.info(f"  Utilisateurs : {len(user_ids)}")
    logger.info(f"  Livres       : {len(livre_ids)}")
    logger.info(f"  Variance SVD : {variance_expliquee:.2%}")
    logger.info(f"  Couverture   : {couverture:.2%}")


if __name__ == '__main__':
    main()
