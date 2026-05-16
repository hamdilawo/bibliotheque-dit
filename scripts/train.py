"""
Entraînement du modèle SVD (filtrage collaboratif).

Entrée  : data/loans_clean.csv
Sortie  : model/model.pkl

Usage:
    python scripts/train.py
"""
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.decomposition import TruncatedSVD

PARAMS = yaml.safe_load(Path("params.yaml").read_text())
SVD_PARAMS = PARAMS["svd"]


def train(input_path: str, output_path: str) -> dict:
    df = pd.read_csv(input_path)
    print(f"Données chargées : {len(df)} lignes")

    # Filtrer les utilisateurs avec suffisamment d'emprunts
    min_ratings = SVD_PARAMS["min_user_ratings"]
    user_counts = df.groupby("user_id")["note"].count()
    active_users = user_counts[user_counts >= min_ratings].index
    df = df[df["user_id"].isin(active_users)]
    print(f"Utilisateurs actifs (>= {min_ratings} emprunts) : {len(active_users)}")

    # Construire la matrice user-item (pivotée sur isbn_norm)
    matrix = df.pivot_table(
        index="user_id",
        columns="isbn_norm",
        values="note",
        aggfunc="mean",
    ).fillna(0)

    user_index = {uid: i for i, uid in enumerate(matrix.index)}
    item_index = {isbn: i for i, isbn in enumerate(matrix.columns)}

    print(f"Matrice : {matrix.shape[0]} utilisateurs × {matrix.shape[1]} livres")

    # SVD
    n_components = min(SVD_PARAMS["n_components"], min(matrix.shape) - 1)
    svd = TruncatedSVD(
        n_components=n_components,
        n_iter=SVD_PARAMS["n_iter"],
        random_state=SVD_PARAMS["random_state"],
    )
    user_factors = svd.fit_transform(matrix.values)
    item_factors = svd.components_.T

    # Popularité (nb d'emprunts par isbn)
    popularity = (
        df.groupby("isbn_norm")
        .agg(count=("note", "count"), score=("note", "mean"))
        .reset_index()
        .set_index("isbn_norm")
    )

    # Mapping isbn → titre/auteur
    isbn_to_meta = (
        df.groupby("isbn_norm")
        .first()[["book_title", "book_author"]]
        .to_dict("index")
    )

    artifacts = {
        "user_factors": user_factors,
        "item_factors": item_factors,
        "user_index": user_index,
        "item_index": item_index,
        "popularity": popularity,
        "isbn_to_meta": isbn_to_meta,
        "ratings": df,
        "params": SVD_PARAMS,
    }

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        pickle.dump(artifacts, f)

    print(f"Modèle sauvegardé : {output_path}")
    return artifacts


if __name__ == "__main__":
    input_path = sys.argv[1] if len(sys.argv) > 1 else "data/loans_clean.csv"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "model/model.pkl"
    train(input_path, output_path)
