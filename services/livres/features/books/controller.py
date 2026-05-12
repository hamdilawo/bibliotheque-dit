"""
Controller Litestar — routes du service Livres.
"""
from typing import Annotated, Optional
from uuid import UUID

from litestar import Controller, get, post, patch, delete
from litestar.datastructures import UploadFile
from litestar.enums import RequestEncodingType
from litestar.params import Body, Parameter
from litestar.exceptions import HTTPException

from features.books.schemas import (
    LivreIn, LivrePatchIn, LivreDetailOut, DisponibiliteIn, DisponibiliteOut,
    CategorieOut, PaginatedOut, HealthOut,
)
from features.books import service


# ─── Health Check ────────────────────────────────────────────
@get("/health", tags=["health"])
async def health_check() -> HealthOut:
    db_status = "connected"
    minio_status = "connected"

    try:
        from features.books.tables import Livre
        await Livre.count()
    except Exception:
        db_status = "disconnected"

    try:
        from core.storage import get_minio_client, get_settings
        from core.settings import get_settings
        settings = get_settings()
        client = get_minio_client()
        client.bucket_exists(settings.minio_bucket_couvertures)
    except Exception:
        minio_status = "disconnected"

    overall = "ok" if db_status == "connected" and minio_status == "connected" else "degraded"
    return HealthOut(
        status=overall,
        service="livres",
        db=db_status,
        minio=minio_status,
        version="2.0.0",
    )


# ─── Controller Catégories ───────────────────────────────────
class CategorieController(Controller):
    path = "/api/categories"
    tags = ["categories"]

    @get("")
    async def lister(self) -> list[CategorieOut]:
        """Liste toutes les catégories avec nombre de livres."""
        data = await service.lister_categories()
        return [CategorieOut(**d) for d in data]


# ─── Controller Livres ───────────────────────────────────────
class LivreController(Controller):
    path = "/api/livres"
    tags = ["livres"]

    @get("")
    async def lister(
        self,
        page: int = Parameter(default=1, ge=1),
        page_size: int = Parameter(default=20, ge=1, le=100),
        sort: str = Parameter(default="titre"),
    ) -> PaginatedOut:
        """Liste paginée de tous les livres actifs."""
        return await service.lister_livres(page, page_size, sort)

    @post("")
    async def creer(
        self,
        titre: Annotated[str, Body(media_type=RequestEncodingType.MULTI_PART)],
        auteur: Annotated[str, Body(media_type=RequestEncodingType.MULTI_PART)],
        isbn: Annotated[str, Body(media_type=RequestEncodingType.MULTI_PART)],
        couverture: Annotated[UploadFile, Body(media_type=RequestEncodingType.MULTI_PART)],
        editeur: Annotated[str, Body(media_type=RequestEncodingType.MULTI_PART)] = "",
        annee_publication: Annotated[Optional[int], Body(media_type=RequestEncodingType.MULTI_PART)] = None,
        langue: Annotated[str, Body(media_type=RequestEncodingType.MULTI_PART)] = "fr",
        description: Annotated[str, Body(media_type=RequestEncodingType.MULTI_PART)] = "",
        nombre_pages: Annotated[Optional[int], Body(media_type=RequestEncodingType.MULTI_PART)] = None,
        categorie: Annotated[Optional[UUID], Body(media_type=RequestEncodingType.MULTI_PART)] = None,
        quantite_totale: Annotated[int, Body(media_type=RequestEncodingType.MULTI_PART)] = 1,
    ) -> LivreDetailOut:
        """Crée un nouveau livre avec sa couverture (multipart/form-data). L'image est obligatoire."""
        content_type = couverture.content_type or "application/octet-stream"
        file_bytes = await couverture.read()

        try:
            data = LivreIn(
                titre=titre,
                auteur=auteur,
                isbn=isbn,
                editeur=editeur,
                annee_publication=annee_publication,
                langue=langue,
                description=description,
                nombre_pages=nombre_pages,
                categorie=categorie,
                quantite_totale=quantite_totale,
            )
        except Exception as e:
            raise HTTPException(status_code=422, detail=str(e))

        try:
            livre = await service.creer_livre(data, file_bytes, content_type)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))

        return LivreDetailOut(**livre)

    @get("/search")
    async def rechercher(
        self,
        q: Optional[str] = None,
        categorie: Optional[UUID] = None,
        langue: Optional[str] = None,
        annee_min: Optional[int] = None,
        annee_max: Optional[int] = None,
        page: int = Parameter(default=1, ge=1),
        page_size: int = Parameter(default=20, ge=1, le=100),
    ) -> PaginatedOut:
        """Recherche multi-critères (titre, auteur, ISBN, description, éditeur)."""
        return await service.rechercher_livres(
            q, categorie, langue, annee_min, annee_max, page, page_size
        )

    @get("/{livre_id:uuid}")
    async def detail(self, livre_id: UUID) -> LivreDetailOut:
        """Détail complet d'un livre."""
        livre = await service.get_livre(livre_id)
        return LivreDetailOut(**livre)

    @patch("/{livre_id:uuid}")
    async def modifier_partiellement(self, livre_id: UUID, data: LivrePatchIn) -> LivreDetailOut:
        """Modification partielle — ISBN non modifiable."""
        livre = await service.modifier_partiellement(livre_id, data)
        return LivreDetailOut(**livre)

    @delete("/{livre_id:uuid}", status_code=204)
    async def supprimer(self, livre_id: UUID) -> None:
        """Soft delete + suppression couverture MinIO."""
        await service.supprimer_livre(livre_id)

    @post("/{livre_id:uuid}/disponibilite") 
    async def disponibilite(self, livre_id: UUID, data: DisponibiliteIn) -> DisponibiliteOut:
        """
        Appelé par le service Emprunts pour réserver ou retourner.
        Body: {"action": "reserver", "quantite": 1}
        """
        result = await service.maj_disponibilite(livre_id, data.action, data.quantite)
        return DisponibiliteOut(**result)

    # ─── Endpoints couverture MinIO ──────────────────────────

    @delete("/{livre_id:uuid}/couverture", status_code=200, tags=["livres"])
    async def supprimer_couverture(self, livre_id: UUID) -> dict:
        """
        Supprime la couverture d'un livre depuis MinIO et efface le token en base.
        """
        return await service.supprimer_couverture(livre_id)
