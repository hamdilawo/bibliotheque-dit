"""
Fixtures partagées pour tous les tests du service Livres.
"""
import pytest_asyncio
from litestar.testing import AsyncTestClient
from app import app


@pytest_asyncio.fixture(scope="function")
async def client():
    """Client de test Litestar."""
    async with AsyncTestClient(app=app) as c:
        yield c


# ─── Données de test réutilisables ───────────────────────────
CATEGORIE_VALIDE = {
    "nom": "Test Informatique",
    "description": "Catégorie de test"
}

LIVRE_VALIDE = {
    "titre": "Clean Code",
    "auteur": "Robert C. Martin",
    "isbn": "9780132350884",
    "editeur": "Prentice Hall",
    "annee_publication": 2008,
    "langue": "en",
    "quantite_totale": 3,
    "quantite_disponible": 3,
}

LIVRE_VALIDE_2 = {
    "titre": "The Pragmatic Programmer",
    "auteur": "David Thomas",
    "isbn": "9780135957059",
    "editeur": "Addison-Wesley",
    "annee_publication": 2019,
    "langue": "en",
    "quantite_totale": 2,
    "quantite_disponible": 2,
}