"""
Pipeline DVC — Étape 1 : Prétraitement des données
====================================================
Entrée  : data/loans.csv       (historique brut des emprunts)
Sortie  : data/loans_clean.csv (données nettoyées et enrichies)

Exécution : python preprocess.py
"""
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s — %(levelname)s — %(message)s')
logger = logging.getLogger(__name__)

INPUT_PATH  = Path('data/loans.csv')
OUTPUT_PATH = Path('data/loans_clean.csv')
STATS_PATH  = Path('data/preprocess_stats.json')


def charger_donnees(path: Path) -> pd.DataFrame:
    logger.info(f"Chargement de {path} ...")
    df = pd.read_csv(path)
    logger.info(f"  {len(df)} lignes chargées, colonnes : {list(df.columns)}")
    return df


def nettoyer(df: pd.DataFrame) -> pd.DataFrame:
    stats = {'initial': len(df)}

    # 1. Supprimer les doublons
    avant = len(df)
    df = df.drop_duplicates()
    stats['doublons_supprimes'] = avant - len(df)
    logger.info(f"  Doublons supprimés : {stats['doublons_supprimes']}")

    # 2. Supprimer les lignes avec utilisateur_id ou livre_id manquants
    avant = len(df)
    df = df.dropna(subset=['utilisateur_id', 'livre_id'])
    stats['lignes_ids_manquants'] = avant - len(df)
    logger.info(f"  Lignes IDs manquants : {stats['lignes_ids_manquants']}")

    # 3. Convertir les types
    df['utilisateur_id'] = df['utilisateur_id'].astype(int)
    df['livre_id']       = df['livre_id'].astype(int)
    df['jours_retard']   = df['jours_retard'].fillna(0).astype(int)

    # 4. Parser les dates
    df['date_emprunt'] = pd.to_datetime(df['date_emprunt'], errors='coerce')
    df = df.dropna(subset=['date_emprunt'])

    # 5. Garder uniquement les emprunts retournés (statut RETOURNE)
    avant = len(df)
    df = df[df['statut'] == 'RETOURNE'].copy()
    stats['non_retournes_exclus'] = avant - len(df)
    logger.info(f"  Emprunts non retournés exclus : {stats['non_retournes_exclus']}")

    # 6. Construire un score implicite d'interaction
    #    score = 1 (emprunt normal) + bonus si rendu à temps
    df['score'] = 1.0
    df.loc[df['jours_retard'] == 0, 'score'] = 1.5   # rendu à temps → score plus élevé
    df.loc[df['jours_retard'] > 7,  'score'] = 0.8   # fort retard → signal faible

    # 7. Ajouter des features temporelles
    df['mois_emprunt']   = df['date_emprunt'].dt.month
    df['annee_emprunt']  = df['date_emprunt'].dt.year
    df['jour_semaine']   = df['date_emprunt'].dt.dayofweek

    # 8. Filtre qualité : garder utilisateurs avec au moins 1 emprunt
    #    et livres avec au moins 1 emprunt
    users_valides = df['utilisateur_id'].value_counts()
    livres_valides = df['livre_id'].value_counts()
    df = df[
        df['utilisateur_id'].isin(users_valides[users_valides >= 1].index) &
        df['livre_id'].isin(livres_valides[livres_valides >= 1].index)
    ]

    stats['final'] = len(df)
    stats['n_utilisateurs'] = df['utilisateur_id'].nunique()
    stats['n_livres']       = df['livre_id'].nunique()
    stats['taux_retention'] = round(stats['final'] / stats['initial'] * 100, 2)

    logger.info(f"  Données finales : {stats['final']} lignes")
    logger.info(f"  Utilisateurs uniques : {stats['n_utilisateurs']}")
    logger.info(f"  Livres uniques       : {stats['n_livres']}")
    logger.info(f"  Taux de rétention    : {stats['taux_retention']}%")

    return df, stats


def main():
    logger.info("=== Prétraitement DVC — Début ===")

    if not INPUT_PATH.exists():
        # Générer des données de démonstration si le CSV n'existe pas encore
        logger.warning(f"{INPUT_PATH} introuvable → génération de données de démonstration...")
        generer_donnees_demo()

    df = charger_donnees(INPUT_PATH)
    df_clean, stats = nettoyer(df)

    # Sauvegarder
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(OUTPUT_PATH, index=False)
    logger.info(f"Données nettoyées sauvegardées : {OUTPUT_PATH}")

    # Sauvegarder les stats de prétraitement
    with open(STATS_PATH, 'w') as f:
        json.dump(stats, f, indent=2)
    logger.info(f"Stats sauvegardées : {STATS_PATH}")

    logger.info("=== Prétraitement DVC — Terminé ===")


def generer_donnees_demo():
    """Génère un CSV de démonstration pour les tests du pipeline."""
    import random
    from datetime import date, timedelta

    random.seed(42)
    today = date.today()
    rows = []

    for i in range(1, 201):
        utilisateur_id = random.randint(1, 20)
        livre_id       = random.randint(1, 30)
        jours_passes   = random.randint(15, 365)
        date_emprunt   = today - timedelta(days=jours_passes)
        retard         = random.choice([0, 0, 0, 0, random.randint(1, 20)])
        rows.append({
            'id': i,
            'utilisateur_id': utilisateur_id,
            'livre_id': livre_id,
            'date_emprunt': date_emprunt.strftime('%Y-%m-%d'),
            'date_retour_effective': (date_emprunt + timedelta(days=14 + retard)).strftime('%Y-%m-%d'),
            'statut': 'RETOURNE',
            'jours_retard': retard,
        })

    INPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(INPUT_PATH, index=False)
    logger.info(f"Données de démonstration générées : {len(rows)} emprunts → {INPUT_PATH}")


if __name__ == '__main__':
    main()
