"""
Évaluation du modèle SVD : calcul RMSE et MAE.

Entrée  : model/model.pkl + data/loans_clean.csv
Sortie  : metrics/metrics.json

Usage:
    python scripts/evaluate.py
"""
import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.model_selection import train_test_split

PARAMS = yaml.safe_load(Path("params.yaml").read_text())
TEST_SIZE = PARAMS["data"]["test_size"]


def predict_score(user_id, isbn, artifacts) -> float | None:
    user_index = artifacts["user_index"]
    item_index = artifacts["item_index"]
    user_factors = artifacts["user_factors"]
    item_factors = artifacts["item_factors"]

    if user_id not in user_index or isbn not in item_index:
        return None

    u = user_index[user_id]
    i = item_index[isbn]
    return float(np.dot(user_factors[u], item_factors[i]))


def evaluate(model_path: str, data_path: str, output_path: str) -> dict:
    with open(model_path, "rb") as f:
        artifacts = pickle.load(f)

    df = pd.read_csv(data_path)

    # Split train/test
    _, test_df = train_test_split(
        df, test_size=TEST_SIZE,
        random_state=PARAMS["svd"]["random_state"]
    )

    predictions, actuals = [], []
    for _, row in test_df.iterrows():
        pred = predict_score(row["user_id"], row["isbn_norm"], artifacts)
        if pred is not None:
            predictions.append(pred)
            actuals.append(float(row["note"]))

    if not predictions:
        print("Aucune prédiction possible sur le test set (utilisateurs/livres inconnus).")
        metrics = {"rmse": None, "mae": None, "n_predictions": 0}
    else:
        predictions = np.array(predictions)
        actuals = np.array(actuals)
        rmse = float(np.sqrt(np.mean((predictions - actuals) ** 2)))
        mae = float(np.mean(np.abs(predictions - actuals)))
        metrics = {
            "rmse": round(rmse, 4),
            "mae": round(mae, 4),
            "n_predictions": len(predictions),
            "n_users": len(artifacts["user_index"]),
            "n_books": len(artifacts["item_index"]),
        }
        print(f"RMSE : {rmse:.4f}")
        print(f"MAE  : {mae:.4f}")
        print(f"Prédictions : {len(predictions)}")

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"Métriques sauvegardées : {output_path}")
    return metrics


if __name__ == "__main__":
    model_path = sys.argv[1] if len(sys.argv) > 1 else "model/model.pkl"
    data_path = sys.argv[2] if len(sys.argv) > 2 else "data/loans_clean.csv"
    output_path = sys.argv[3] if len(sys.argv) > 3 else "metrics/metrics.json"
    evaluate(model_path, data_path, output_path)
