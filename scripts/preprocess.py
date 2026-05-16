"""
Prétraitement des données d'emprunts pour le pipeline ML.

Entrée  : data/loans.csv
Sortie  : data/loans_clean.csv

Usage:
    python scripts/preprocess.py
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

PARAMS = yaml.safe_load(Path("params.yaml").read_text())
MIN_RATING = PARAMS["data"]["min_rating"]
MAX_RATING = PARAMS["data"]["max_rating"]


def normalize_isbn(isbn) -> str:
    if not isbn or str(isbn) in ("nan", "None", ""):
        return ""
    return re.sub(r"[^0-9X]", "", str(isbn).upper())


def implicit_score(row) -> float:
    """Note implicite si l'utilisateur n'a pas noté."""
    retard = float(row.get("jours_retard", 0) or 0)
    if retard <= 0:
        return 1.5
    elif retard <= 7:
        return 1.0
    else:
        return 0.8


def preprocess(input_path: str, output_path: str) -> None:
    df = pd.read_csv(input_path)
    print(f"Chargé : {len(df)} lignes")

    # Renommer les colonnes pour cohérence
    df = df.rename(columns={
        "user_id": "user_id",
        "book_id": "livre_id",
        "rating": "note",
    })

    # Garder uniquement les emprunts terminés ou approuvés
    df = df[df["statut"].isin(["completed", "approved"])].copy()
    print(f"Après filtre statut : {len(df)} lignes")

    # Convertir les notes numériques
    df["note"] = pd.to_numeric(df["note"], errors="coerce")

    # Imputer les notes manquantes via score implicite
    mask_no_rating = df["note"].isna()
    df.loc[mask_no_rating, "note"] = df[mask_no_rating].apply(implicit_score, axis=1)

    # Normaliser les ISBNs
    df["isbn_norm"] = df["isbn"].apply(normalize_isbn)

    # Supprimer les lignes sans user_id ou isbn
    df = df.dropna(subset=["user_id"])
    df = df[df["isbn_norm"] != ""]
    print(f"Après nettoyage : {len(df)} lignes")

    # Clamp des notes
    df["note"] = df["note"].clip(MIN_RATING, MAX_RATING)

    # Colonnes finales
    cols = ["user_id", "livre_id", "isbn_norm", "book_title", "book_author",
            "note", "jours_retard", "statut"]
    cols = [c for c in cols if c in df.columns]
    df = df[cols]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Sauvegardé : {output_path} ({len(df)} lignes propres)")


if __name__ == "__main__":
    input_path = sys.argv[1] if len(sys.argv) > 1 else "data/loans.csv"
    output_path = sys.argv[2] if len(sys.argv) > 2 else "data/loans_clean.csv"
    preprocess(input_path, output_path)
