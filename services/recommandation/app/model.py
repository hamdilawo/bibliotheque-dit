"""
Modèle de recommandation basé sur le filtrage collaboratif.
Utilise une matrice utilisateur-livre avec SVD (TruncatedSVD de sklearn).
"""
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)


class RecommendationModel:
    """
    Modèle de recommandation par filtrage collaboratif (SVD).

    Pipeline :
    1. Construction d'une matrice utilisateur × livre
    2. Décomposition SVD pour capturer les patterns latents
    3. Calcul de similarité cosinus entre utilisateurs
    4. Recommandation des livres populaires chez les utilisateurs similaires
    """

    def __init__(self):
        self.svd = None
        self.user_factors = None         # Représentation des utilisateurs dans l'espace latent
        self.livre_ids: List[int] = []   # Index → livre_id
        self.user_ids: List[int] = []    # Index → utilisateur_id
        self.matrice = None              # Matrice brute utilisateur × livre
        self.is_trained = False
        self.metrics = {}

    def entrainer(self, df: pd.DataFrame, n_components: int = 10) -> dict:
        """
        Entraîne le modèle sur l'historique des emprunts.

        Args:
            df: DataFrame avec colonnes [utilisateur_id, livre_id, ...]
            n_components: nombre de dimensions latentes SVD

        Returns:
            Dictionnaire de métriques
        """
        logger.info(f"Entraînement sur {len(df)} emprunts...")

        # 1. Construire la matrice utilisateur × livre
        df_pivot = df.groupby(['utilisateur_id', 'livre_id']).size().reset_index(name='count')
        matrice_df = df_pivot.pivot(index='utilisateur_id', columns='livre_id', values='count').fillna(0)

        self.user_ids = list(matrice_df.index)
        self.livre_ids = list(matrice_df.columns)
        self.matrice = matrice_df.values.astype(float)

        # 2. SVD
        n_comp = min(n_components, min(self.matrice.shape) - 1)
        self.svd = TruncatedSVD(n_components=n_comp, random_state=42)
        self.user_factors = self.svd.fit_transform(self.matrice)
        self.user_factors = normalize(self.user_factors)

        self.is_trained = True

        # 3. Métriques simples
        variance_expliquee = float(self.svd.explained_variance_ratio_.sum())
        self.metrics = {
            'n_utilisateurs': len(self.user_ids),
            'n_livres': len(self.livre_ids),
            'n_emprunts': len(df),
            'n_components': n_comp,
            'variance_expliquee': round(variance_expliquee, 4),
            'densite_matrice': round(
                float(np.count_nonzero(self.matrice)) / self.matrice.size, 4
            ),
        }

        logger.info(f"Modèle entraîné. Variance expliquée : {variance_expliquee:.2%}")
        return self.metrics

    def recommander(self, utilisateur_id: int, n: int = 5) -> List[dict]:
        """
        Génère des recommandations pour un utilisateur.

        Args:
            utilisateur_id: ID de l'utilisateur
            n: nombre de recommandations

        Returns:
            Liste de {livre_id, score}
        """
        if not self.is_trained:
            raise RuntimeError("Le modèle n'est pas encore entraîné.")

        # Livres déjà empruntés par cet utilisateur
        deja_empruntes = set()
        if utilisateur_id in self.user_ids:
            idx_user = self.user_ids.index(utilisateur_id)
            deja_empruntes = {
                self.livre_ids[i]
                for i, val in enumerate(self.matrice[idx_user])
                if val > 0
            }
            # Vecteur de l'utilisateur dans l'espace latent
            vecteur_user = self.user_factors[idx_user]

            # Similarité cosinus avec tous les autres utilisateurs
            similarites = self.user_factors @ vecteur_user
            similarites[idx_user] = 0  # Exclure lui-même

            # Top utilisateurs similaires
            top_similaires = np.argsort(similarites)[::-1][:10]

            # Agréger les scores des livres chez les utilisateurs similaires
            scores = np.zeros(len(self.livre_ids))
            for sim_idx in top_similaires:
                poids = similarites[sim_idx]
                scores += poids * self.matrice[sim_idx]

        else:
            # Utilisateur inconnu → recommandations basées sur la popularité
            scores = self.matrice.sum(axis=0)

        # Exclure les livres déjà empruntés
        for i, livre_id in enumerate(self.livre_ids):
            if livre_id in deja_empruntes:
                scores[i] = 0

        # Top-N
        top_indices = np.argsort(scores)[::-1][:n]
        recommandations = [
            {
                'livre_id': int(self.livre_ids[i]),
                'score': round(float(scores[i]), 4),
            }
            for i in top_indices
            if scores[i] > 0
        ]

        # Fallback popularité si pas assez de résultats
        if len(recommandations) < n:
            popularite = self.matrice.sum(axis=0)
            for i in np.argsort(popularite)[::-1]:
                livre_id = int(self.livre_ids[i])
                if livre_id not in deja_empruntes and not any(
                    r['livre_id'] == livre_id for r in recommandations
                ):
                    recommandations.append({
                        'livre_id': livre_id,
                        'score': round(float(popularite[i]) / popularite.max(), 4),
                    })
                if len(recommandations) >= n:
                    break

        return recommandations

    def sauvegarder(self, path: str):
        """Sauvegarde le modèle avec joblib."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, path)
        logger.info(f"Modèle sauvegardé : {path}")

    @classmethod
    def charger(cls, path: str) -> 'RecommendationModel':
        """Charge le modèle depuis le disque."""
        if not Path(path).exists():
            raise FileNotFoundError(f"Aucun modèle trouvé à : {path}")
        model = joblib.load(path)
        logger.info(f"Modèle chargé depuis : {path}")
        return model
