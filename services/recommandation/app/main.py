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
import asyncio
import io
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Dict, List, Optional

import httpx
import pandas as pd
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import (
    ALPHA,
    ARTIFACTS_PATH,
    BOOKS_PATH,
    DATA_PATH,
    MIN_USER_RATINGS,
    N_RECOMMENDATIONS,
    REF_WEIGHT,
    SERVICE_EMPRUNTS_URL,
    SERVICE_LIVRES_URL,
)
from .model import RecommendationModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# État global du modèle
model_state = {
    "model": None,
    "ratings": None,
    "entrainement_en_cours": False,
}
livres_cache: Dict[str, dict] = {}


def _resolve_artifacts_path() -> str:
    candidates = [ARTIFACTS_PATH]
    if "artifacts" in ARTIFACTS_PATH:
        candidates.append(ARTIFACTS_PATH.replace("artifacts", "artefacts"))
    for path in candidates:
        if Path(path).exists():
            return path
    return ARTIFACTS_PATH


# ------------------------------------------------------------------ #
# Startup : charger le modèle au démarrage
# ------------------------------------------------------------------ #
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Charge le modèle au démarrage si disponible."""
    try:
        artifacts_path = _resolve_artifacts_path()
        model_state["model"] = RecommendationModel.charger(artifacts_path)
        logger.info("Modèle chargé au démarrage.")
        if model_state["model"].ratings is None:
            ratings = _charger_ratings_locales()
            model_state["model"].ratings = ratings
            model_state["ratings"] = ratings
        else:
            model_state["ratings"] = model_state["model"].ratings
    except FileNotFoundError:
        logger.warning(f"Pas de modèle pré-entraîné à {ARTIFACTS_PATH}. Entraînez-le via POST /train.")
    except Exception as exc:
        model_state["model"] = None
        model_state["ratings"] = None
        logger.warning(
            f"Impossible de charger le modèle ({exc}). "
            "Lancez POST /train pour régénérer des artefacts compatibles."
        )
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
    livre_id: Optional[int] = None
    score: float
    titre: Optional[str] = None
    auteur: Optional[str] = None
    isbn: Optional[str] = None
    disponible: Optional[bool] = None
    categorie: Optional[str] = None


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
async def _fetch_livre_by_isbn(client: httpx.AsyncClient, isbn: str) -> Optional[dict]:
    key = RecommendationModel.normalize_isbn(isbn)
    if not key:
        return None
    if key in livres_cache:
        return livres_cache[key]

    try:
        resp = await client.get(
            f"{SERVICE_LIVRES_URL}/api/livres/search/",
            params={"q": isbn},
        )
        if resp.status_code != 200:
            return None
        data = resp.json() or {}
        results = data.get("results") if isinstance(data, dict) else data
        if not results:
            return None
        match = None
        for livre in results:
            if RecommendationModel.normalize_isbn(livre.get("isbn")) == key:
                match = livre
                break
        match = match or results[0]
        livres_cache[key] = match
        return match
    except Exception:
        return None


async def enrichir_avec_details_livres(
    recommandations: List[dict]
) -> List[RecommandationItem]:
    """Appelle le Service Livres pour enrichir les recommandations."""
    resultat: List[RecommandationItem] = []
    async with httpx.AsyncClient(timeout=5.0) as client:
        tasks = []
        for reco in recommandations:
            isbn = reco.get("isbn") or reco.get("isbn_norm")
            tasks.append(_fetch_livre_by_isbn(client, isbn or ""))
        details_list = await asyncio.gather(*tasks, return_exceptions=True)

    for reco, details in zip(recommandations, details_list):
        isbn = reco.get("isbn") or reco.get("isbn_norm")
        item = RecommandationItem(
            livre_id=None,
            score=float(reco.get("score", 0.0)),
            titre=reco.get("title"),
            auteur=reco.get("author"),
            isbn=isbn,
            categorie=reco.get("categorie"),
        )
        if isinstance(details, dict):
            item.livre_id = details.get("id")
            item.titre = details.get("titre") or item.titre
            item.auteur = details.get("auteur") or item.auteur
            item.isbn = details.get("isbn") or item.isbn
            item.disponible = details.get("disponible")
        resultat.append(item)
    return resultat


def _charger_ratings_locales() -> Optional[pd.DataFrame]:
    if not Path(DATA_PATH).exists():
        return None
    try:
        df = pd.read_csv(DATA_PATH)
        return RecommendationModel.preparer_emprunts(df)
    except Exception as exc:
        logger.warning(f"Impossible de charger les ratings locaux: {exc}")
        return None


def _charger_livres_locaux() -> Optional[pd.DataFrame]:
    if not Path(BOOKS_PATH).exists():
        return None
    try:
        return pd.read_json(BOOKS_PATH)
    except Exception as exc:
        logger.warning(f"Impossible de charger books.json: {exc}")
        return None


async def _charger_livres_service() -> Optional[pd.DataFrame]:
    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            page = 1
            rows = []
            while True:
                resp = await client.get(
                    f"{SERVICE_LIVRES_URL}/api/livres/",
                    params={"page": page},
                )
                resp.raise_for_status()
                data = resp.json()
                if isinstance(data, dict) and "results" in data:
                    rows.extend(data.get("results") or [])
                    if not data.get("next"):
                        break
                    page += 1
                elif isinstance(data, list):
                    rows.extend(data)
                    break
                else:
                    break
            return pd.DataFrame(rows)
        except Exception as exc:
            logger.warning(f"Livres service indisponible: {exc}")
            return None


async def _charger_emprunts_service() -> Optional[pd.DataFrame]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(f"{SERVICE_EMPRUNTS_URL}/api/emprunts/export_csv/")
            resp.raise_for_status()
            df = pd.read_csv(io.StringIO(resp.text))
            logger.info(f"Données téléchargées : {len(df)} emprunts")
            return df
        except Exception as exc:
            logger.warning(f"Emprunts service indisponible: {exc}")
            return None


async def telecharger_donnees_emprunts() -> pd.DataFrame:
    """Télécharge l'historique des emprunts depuis le Service Emprunts."""
    df = await _charger_emprunts_service()
    if df is not None:
        return df
    if Path(DATA_PATH).exists():
        logger.info(f"Fallback : lecture depuis {DATA_PATH}")
        return pd.read_csv(DATA_PATH)
    raise HTTPException(status_code=503, detail="Impossible de récupérer les données d'emprunts.")


def entrainer_en_arriere_plan():
    """Tâche d'entraînement asynchrone."""
    import asyncio
    asyncio.run(_entrainer())


async def _entrainer():
    model_state["entrainement_en_cours"] = True
    try:
        emprunts_df = await telecharger_donnees_emprunts()
        livres_df = await _charger_livres_service()
        if livres_df is None:
            livres_df = _charger_livres_locaux()

        if emprunts_df is None or emprunts_df.empty or len(emprunts_df) < 5:
            logger.warning("Pas assez de données pour entraîner le modèle.")
            return
        if livres_df is None or livres_df.empty:
            logger.warning("Pas de données livres disponibles pour l'entraînement.")
            return

        model = RecommendationModel()
        livre_id_to_isbn = None
        if "id" in livres_df.columns and "isbn" in livres_df.columns:
            livre_id_to_isbn = livres_df.set_index("id")["isbn"].to_dict()

        metrics = model.entrainer(
            emprunts_df,
            livres_df,
            livre_id_to_isbn=livre_id_to_isbn,
            alpha=ALPHA,
            min_user_ratings=MIN_USER_RATINGS,
        )
        model.sauvegarder(ARTIFACTS_PATH)

        # Sauvegarder aussi les données localement
        Path(DATA_PATH).parent.mkdir(parents=True, exist_ok=True)
        emprunts_df.to_csv(DATA_PATH, index=False)

        model_state["model"] = model
        model_state["ratings"] = model.ratings
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
async def get_recommendations(
    user_id: int,
    n: int = N_RECOMMENDATIONS,
    ref_isbn: Optional[str] = None,
):
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
        recos_brutes = model.recommander(
            utilisateur_id=user_id,
            n=n,
            ratings=model_state.get("ratings"),
            ref_isbn=ref_isbn,
            ref_weight=REF_WEIGHT,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Enrichir avec les détails des livres
    recos_enrichies = await enrichir_avec_details_livres(recos_brutes)

    connu = user_id in model.artifacts.get("user_index", {})
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

    model: RecommendationModel = model_state["model"]
    popularity = model.artifacts.get("popularity")
    if popularity is None or popularity.empty:
        raise HTTPException(status_code=503, detail="Pas de données de popularité.")

    top = popularity.sort_values("score", ascending=False).head(n)
    livres = []
    async with httpx.AsyncClient(timeout=5.0) as client:
        for isbn_norm, row in top.iterrows():
            details = await _fetch_livre_by_isbn(client, isbn_norm)
            livres.append({
                "livre_id": details.get("id") if isinstance(details, dict) else None,
                "isbn": isbn_norm,
                "emprunts": int(row.get("count", 0)),
            })

    return {"top_livres": livres}
