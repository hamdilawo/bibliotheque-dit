"""
Service de Recommandation — FastAPI
Port : 8004

Endpoints :
  GET  /health                         → santé du service
  GET  /recommendations/{user_id}      → recommandations personnalisées
  POST /train                          → ré-entraînement du modèle
  GET  /metrics                        → métriques du modèle actuel
  GET  /popular                        → livres populaires (fallback)
"""
import logging
import httpx
import pandas as pd
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from .config import (
    MODEL_PATH, DATA_PATH,
    SERVICE_LIVRES_URL, SERVICE_EMPRUNTS_URL,
    N_RECOMMENDATIONS,
)
from .model import RecommendationModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# État global du modèle
model_state = {"model": None, "entrainement_en_cours": False}


# ------------------------------------------------------------------ #
# Startup : charger le modèle au démarrage
# ------------------------------------------------------------------ #
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Charge le modèle au démarrage si disponible."""
    try:
        model_state["model"] = RecommendationModel.charger(MODEL_PATH)
        logger.info("Modèle chargé au démarrage.")
    except FileNotFoundError:
        logger.warning(f"Pas de modèle pré-entraîné à {MODEL_PATH}. Entraînez-le via POST /train.")
    yield
    logger.info("Arrêt du service recommandation.")


app = FastAPI(
    title="Service Recommandation — Bibliothèque DIT",
    description="API de recommandation de livres basée sur l'historique des emprunts (SVD).",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------ #
# Schémas Pydantic
# ------------------------------------------------------------------ #
class RecommandationItem(BaseModel):
    livre_id: int
    score: float
    titre: Optional[str] = None
    auteur: Optional[str] = None
    isbn: Optional[str] = None
    disponible: Optional[bool] = None


class RecommandationsResponse(BaseModel):
    utilisateur_id: int
    recommandations: List[RecommandationItem]
    modele_entraine: bool
    message: str


class TrainResponse(BaseModel):
    success: bool
    message: str
    metrics: dict


# ------------------------------------------------------------------ #
# Helpers
# ------------------------------------------------------------------ #
async def enrichir_avec_details_livres(
    recommandations: List[dict]
) -> List[RecommandationItem]:
    """Appelle le Service Livres pour enrichir les recommandations."""
    resultat = []
    async with httpx.AsyncClient(timeout=5.0) as client:
        for reco in recommandations:
            item = RecommandationItem(
                livre_id=reco['livre_id'],
                score=reco['score']
            )
            try:
                resp = await client.get(
                    f"{SERVICE_LIVRES_URL}/api/livres/{reco['livre_id']}/"
                )
                if resp.status_code == 200:
                    data = resp.json()
                    item.titre = data.get('titre')
                    item.auteur = data.get('auteur')
                    item.isbn = data.get('isbn')
                    item.disponible = data.get('disponible')
            except Exception:
                pass  # On retourne quand même la reco sans détails
            resultat.append(item)
    return resultat


async def telecharger_donnees_emprunts() -> pd.DataFrame:
    """Télécharge l'historique des emprunts depuis le Service Emprunts."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(f"{SERVICE_EMPRUNTS_URL}/api/emprunts/export_csv/")
            resp.raise_for_status()
            import io
            df = pd.read_csv(io.StringIO(resp.text))
            logger.info(f"Données téléchargées : {len(df)} emprunts")
            return df
        except Exception as e:
            # Fallback : lire depuis le fichier local (DVC)
            if Path(DATA_PATH).exists():
                logger.info(f"Fallback : lecture depuis {DATA_PATH}")
                return pd.read_csv(DATA_PATH)
            raise HTTPException(
                status_code=503,
                detail=f"Impossible de récupérer les données : {e}"
            )


def entrainer_en_arriere_plan():
    """Tâche d'entraînement asynchrone."""
    import asyncio
    asyncio.run(_entrainer())


async def _entrainer():
    model_state["entrainement_en_cours"] = True
    try:
        df = await telecharger_donnees_emprunts()
        if df.empty or len(df) < 5:
            logger.warning("Pas assez de données pour entraîner le modèle.")
            return

        model = RecommendationModel()
        metrics = model.entrainer(df)
        model.sauvegarder(MODEL_PATH)

        # Sauvegarder aussi les données localement pour DVC
        Path(DATA_PATH).parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(DATA_PATH, index=False)

        model_state["model"] = model
        logger.info(f"Entraînement terminé. Métriques : {metrics}")
    except Exception as e:
        logger.error(f"Erreur entraînement : {e}")
    finally:
        model_state["entrainement_en_cours"] = False


# ------------------------------------------------------------------ #
# Endpoints
# ------------------------------------------------------------------ #
@app.get("/health")
async def health():
    """Endpoint de santé."""
    return {
        "status": "ok",
        "modele_charge": model_state["model"] is not None,
        "entrainement_en_cours": model_state["entrainement_en_cours"],
    }


@app.get(
    "/recommendations/{user_id}",
    response_model=RecommandationsResponse,
    summary="Recommandations personnalisées",
)
async def get_recommendations(user_id: int, n: int = N_RECOMMENDATIONS):
    """
    Retourne les N meilleures recommandations de livres pour un utilisateur.

    - **user_id** : ID de l'utilisateur
    - **n** : nombre de recommandations (défaut : 5)
    """
    if model_state["model"] is None:
        raise HTTPException(
            status_code=503,
            detail="Modèle non disponible. Lancez POST /train d'abord."
        )

    model: RecommendationModel = model_state["model"]

    try:
        recos_brutes = model.recommander(utilisateur_id=user_id, n=n)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Enrichir avec les détails des livres
    recos_enrichies = await enrichir_avec_details_livres(recos_brutes)

    connu = user_id in model.user_ids
    return RecommandationsResponse(
        utilisateur_id=user_id,
        recommandations=recos_enrichies,
        modele_entraine=True,
        message=(
            f"{len(recos_enrichies)} recommandations personnalisées."
            if connu
            else f"{len(recos_enrichies)} recommandations (utilisateur nouveau → popularité)."
        )
    )


@app.post("/train", response_model=TrainResponse, summary="Ré-entraîner le modèle")
async def train_model(background_tasks: BackgroundTasks):
    """
    Lance le ré-entraînement du modèle en arrière-plan.
    Télécharge les dernières données depuis le Service Emprunts.
    """
    if model_state["entrainement_en_cours"]:
        return TrainResponse(
            success=False,
            message="Un entraînement est déjà en cours.",
            metrics={}
        )

    background_tasks.add_task(entrainer_en_arriere_plan)

    return TrainResponse(
        success=True,
        message="Entraînement lancé en arrière-plan. Consultez GET /metrics pour le suivi.",
        metrics={}
    )


@app.get("/metrics", summary="Métriques du modèle")
async def get_metrics():
    """Retourne les métriques du modèle actuellement chargé."""
    if model_state["model"] is None:
        raise HTTPException(status_code=503, detail="Aucun modèle chargé.")
    return {
        "modele_charge": True,
        "entrainement_en_cours": model_state["entrainement_en_cours"],
        **model_state["model"].metrics,
    }


@app.get("/popular", summary="Livres les plus empruntés")
async def get_popular(n: int = 10):
    """Retourne les livres les plus empruntés (sans personnalisation)."""
    if model_state["model"] is None:
        raise HTTPException(status_code=503, detail="Aucun modèle chargé.")

    import numpy as np
    model: RecommendationModel = model_state["model"]
    popularite = model.matrice.sum(axis=0)
    top_indices = np.argsort(popularite)[::-1][:n]

    livres = [
        {"livre_id": int(model.livre_ids[i]), "emprunts": int(popularite[i])}
        for i in top_indices
    ]
    return {"top_livres": livres}
