"""
Controller Litestar — routes du service Livres.
Le controller ne contient que les routes, la logique est dans service.py.
"""
from typing import Optional
from litestar import Controller, get, post, patch, delete
from litestar.params import Parameter

from features.books.schemas import (
    LivreIn, LivrePatchIn, LivreDetailOut, DisponibiliteIn, DisponibiliteOut,
    CategorieOut, PaginatedOut, HealthOut,
)
from features.books import service


# ─── Health Check ────────────────────────────────────────────
@get("/health", tags=["health"])
async def health_check() -> HealthOut:
    """Vérifie que le service est opérationnel."""
    try:
        from features.books.tables import Livre
        await Livre.count()
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return HealthOut(
        status="ok" if db_status == "connected" else "degraded",
        service="livres",
        db=db_status,
        version="2.0.0",
    )


# ─── Controller Catégories ───────────────────────────────────
class CategorieController(Controller):
    path = "/api/categories"
    tags = ["categories"]

    @get("/")
    async def lister(self) -> list[CategorieOut]:
        """Liste toutes les catégories avec nombre de livres."""
        data = await service.lister_categories()
        return [CategorieOut(**d) for d in data]

    


# ─── Controller Livres ───────────────────────────────────────
class LivreController(Controller):
    path = "/api/livres"
    tags = ["livres"]

    @get("/")
    async def lister(
        self,
        page: int = Parameter(default=1, ge=1),
        page_size: int = Parameter(default=20, ge=1, le=100),
        sort: str = Parameter(default="titre"),
    ) -> PaginatedOut:
        """Liste paginée de tous les livres actifs."""
        return await service.lister_livres(page, page_size, sort)

    @post("/")
    async def creer(self, data: LivreIn) -> LivreDetailOut:
        """Crée un nouveau livre."""
        livre = await service.creer_livre(data)
        return LivreDetailOut(**livre)

    @get("/search")
    async def rechercher(
        self,
        q: Optional[str] = None,
        categorie: Optional[int] = None,
        langue: Optional[str] = None,
        disponible: Optional[bool] = None,
        annee_min: Optional[int] = None,
        annee_max: Optional[int] = None,
        page: int = Parameter(default=1, ge=1),
        page_size: int = Parameter(default=20, ge=1, le=100),
    ) -> PaginatedOut:
        """Recherche multi-critères (titre, auteur, ISBN, description, éditeur)."""
        return await service.rechercher_livres(
            q, categorie, langue, disponible, annee_min, annee_max, page, page_size
        )

    

    @get("/{livre_id:int}")
    async def detail(self, livre_id: int) -> LivreDetailOut:
        """Détail complet d'un livre."""
        livre = await service.get_livre(livre_id)
        return LivreDetailOut(**livre)

    

    @patch("/{livre_id:int}")
    async def modifier_partiellement(self, livre_id: int, data: LivrePatchIn) -> LivreDetailOut:
        """Modification partielle — ISBN non modifiable."""
        livre = await service.modifier_partiellement(livre_id, data)
        return LivreDetailOut(**livre)

    @delete("/{livre_id:int}", status_code=204)
    async def supprimer(self, livre_id: int) -> None:
        """Soft delete — désactive le livre (204 No Content)."""
        await service.supprimer_livre(livre_id)

    @post("/{livre_id:int}/disponibilite")
    async def disponibilite(self, livre_id: int, data: DisponibiliteIn) -> DisponibiliteOut:
        """
        Appelé par le service Emprunts pour réserver ou retourner.
        Body: {"action": "reserver", "quantite": 1}
        """
        result = await service.maj_disponibilite(livre_id, data.action, data.quantite)
        return DisponibiliteOut(**result)