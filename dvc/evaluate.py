"""
Pipeline DVC — Étape 3 : Évaluation du modèle
==============================================
Entrée  : data/loans_clean.csv + model/model.pkl
Sortie  : metrics.json

Métriques calculées :
  - RMSE  (Root Mean Square Error)
  - MAE   (Mean Absolute Error)
  - Précision@K
  - Rappel@K
  - Couverture du catalogue
  - Variance expliquée SVD

Exécution : python evaluate.py
"""
import pandas as pd
import numpy as np
import joblib
import json
import logging
from pathlib import Path
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO, format='%(asctime)s — %(levelname)s — %(message)s')
logger = logging.getLogger(__name__)

DATA_PATH    = Path('data/loans_clean.csv')
MODEL_PATH   = Path('model/model.pkl')
METRICS_PATH = Path('metrics.json')
K            = 5   # Top-K pour Précision@K et Rappel@K


def charger_modele_et_data():
    logger.info("Chargement du modèle et des données...")
    model = joblib.load(MODEL_PATH)
    df    = pd.read_csv(DATA_PATH)
    return model, df


def calculer_rmse_mae(df: pd.DataFrame, model: dict) -> tuple:
    """
    Calcule RMSE et MAE en mode leave-one-out :
    Pour chaque utilisateur connu, on masque un emprunt et on prédit son score.
    """
    logger.info("Calcul RMSE / MAE...")

    user_ids   = model['user_ids']
    livre_ids  = model['livre_ids']
    matrice    = model['matrice']
    user_factors = model['user_factors']

    errors = []

    for idx, uid in enumerate(user_ids):
        # Interactions réelles de cet utilisateur
        row = matrice[idx]
        interactions = [(livre_ids[i], row[i]) for i in range(len(livre_ids)) if row[i] > 0]

        if len(interactions) < 2:
            continue   # Pas assez de données pour leave-one-out

        # Prédire les scores via similarité cosinus
        vecteur = user_factors[idx]
        similarites = user_factors @ vecteur
        similarites[idx] = 0
        top_users = np.argsort(similarites)[::-1][:10]

        scores_pred = np.zeros(len(livre_ids))
        for u in top_users:
            scores_pred += similarites[u] * matrice[u]

        # Normaliser les prédictions dans [0, 2] comme les scores réels
        if scores_pred.max() > 0:
            scores_pred = scores_pred / scores_pred.max() * 2

        # Comparer prédictions vs réalité
        for livre_id, score_reel in interactions:
            if livre_id in livre_ids:
                i = livre_ids.index(livre_id)
                score_predit = float(scores_pred[i])
                errors.append((score_reel - score_predit) ** 2)

    if not errors:
        return 0.0, 0.0

    rmse = float(np.sqrt(np.mean(errors)))
    mae  = float(np.mean(np.abs(np.array(
        [np.sqrt(e) for e in errors]
    ))))

    logger.info(f"  RMSE : {rmse:.4f}")
    logger.info(f"  MAE  : {mae:.4f}")
    return round(rmse, 4), round(mae, 4)


def calculer_precision_rappel_at_k(model: dict, k: int = K) -> tuple:
    """
    Précision@K et Rappel@K via validation croisée :
    On masque 20% des interactions et on vérifie si elles apparaissent dans les top-K.
    """
    logger.info(f"Calcul Précision@{k} et Rappel@{k}...")

    user_ids     = model['user_ids']
    livre_ids    = model['livre_ids']
    matrice      = model['matrice']
    user_factors = model['user_factors']

    precisions = []
    rappels    = []

    for idx, uid in enumerate(user_ids):
        row = matrice[idx]
        positifs = [i for i in range(len(livre_ids)) if row[i] > 0]

        if len(positifs) < 2:
            continue

        # Masquer 20% des interactions (test set)
        n_test  = max(1, int(len(positifs) * 0.2))
        test_set = set(np.random.choice(positifs, size=n_test, replace=False))

        # Prédire sans les interactions masquées
        matrice_train = matrice.copy()
        for i in test_set:
            matrice_train[idx][i] = 0

        vecteur     = user_factors[idx]
        similarites = user_factors @ vecteur
        similarites[idx] = 0
        top_users   = np.argsort(similarites)[::-1][:10]

        scores = np.zeros(len(livre_ids))
        for u in top_users:
            scores += similarites[u] * matrice_train[u]

        # Exclure déjà vus (train)
        for i in range(len(livre_ids)):
            if matrice_train[idx][i] > 0:
                scores[i] = 0

        top_k = set(np.argsort(scores)[::-1][:k])

        hits      = len(top_k & test_set)
        precision = hits / k
        rappel    = hits / len(test_set) if test_set else 0

        precisions.append(precision)
        rappels.append(rappel)

    p_at_k = round(float(np.mean(precisions)), 4) if precisions else 0.0
    r_at_k = round(float(np.mean(rappels)), 4) if rappels else 0.0

    logger.info(f"  Précision@{k} : {p_at_k:.4f}")
    logger.info(f"  Rappel@{k}    : {r_at_k:.4f}")
    return p_at_k, r_at_k


def main():
    logger.info("=== Évaluation DVC — Début ===")

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Modèle introuvable : {MODEL_PATH}. Lancez train.py d'abord.")
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Données introuvables : {DATA_PATH}. Lancez preprocess.py d'abord.")

    model, df = charger_modele_et_data()

    # Charger les infos d'entraînement
    training_info = model.get('training_info', {})

    # Calculer les métriques
    np.random.seed(42)
    rmse, mae                 = calculer_rmse_mae(df, model)
    precision_at_k, rappel_at_k = calculer_precision_rappel_at_k(model, k=K)

    # Assembler metrics.json
    metrics = {
        # Métriques de prédiction
        'rmse': rmse,
        'mae': mae,
        f'precision_at_{K}': precision_at_k,
        f'rappel_at_{K}': rappel_at_k,

        # Métriques du modèle
        'variance_expliquee_svd': training_info.get('variance_expliquee', 0),
        'couverture_catalogue':   training_info.get('couverture', 0),

        # Métriques des données
        'n_utilisateurs': training_info.get('n_utilisateurs', 0),
        'n_livres':       training_info.get('n_livres', 0),
        'n_emprunts':     training_info.get('n_emprunts', len(df)),

        # Hyperparamètres utilisés
        'hyperparams': model.get('params', {}),
    }

    # Sauvegarder metrics.json (format attendu par DVC)
    with open(METRICS_PATH, 'w') as f:
        json.dump(metrics, f, indent=2)

    logger.info(f"\nMétriques sauvegardées dans {METRICS_PATH}")
    logger.info("=" * 40)
    logger.info(f"  RMSE              : {rmse}")
    logger.info(f"  MAE               : {mae}")
    logger.info(f"  Précision@{K}      : {precision_at_k}")
    logger.info(f"  Rappel@{K}         : {rappel_at_k}")
    logger.info(f"  Variance SVD      : {training_info.get('variance_expliquee', 0):.2%}")
    logger.info(f"  Couverture        : {training_info.get('couverture', 0):.2%}")
    logger.info("=" * 40)
    logger.info("=== Évaluation DVC — Terminé ===")


if __name__ == '__main__':
    main()
