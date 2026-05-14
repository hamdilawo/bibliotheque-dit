"""
Service métier — Service Livres.
Toute la logique base de données et MinIO passe par ici.
"""
import logging
from typing import Optional
from uuid import UUID

logger = logging.getLogger(__name__)

from piccolo.columns.combination import Or, Where

from features.books.tables import Livre, Categorie
from features.books.schemas import LivreIn, LivrePatchIn, LivreListOut, PaginatedOut
from core.exceptions import LivreNotFoundException, ISBNAlreadyExistsException
from core.storage import upload_couverture, delete_couverture, get_couverture_url


# ─── Catégories ──────────────────────────────────────────────

async def lister_categories() -> list[dict]:
    categories = await Categorie.select().order_by(Categorie.nom)
    result = []
    for cat in categories:
        nb = await Livre.count().where(
            (Livre.categorie == cat["id"]) & Livre.actif.eq(True)
        )
        result.append({**cat, "nombre_livres": nb})
    return result


# ─── Livres ──────────────────────────────────────────────────

async def lister_livres(
    page: int = 1,
    page_size: int = 20,
    sort: str = "titre",
) -> PaginatedOut:
    offset = (page - 1) * page_size
    total = await Livre.count().where(Livre.actif.eq(True))
    sort_col = getattr(Livre, sort, Livre.titre)

    livres = await (
        Livre
        .select(*Livre.all_columns(), Livre.categorie._.nom.as_alias("categorie_nom"))
        .order_by(sort_col)
        .limit(page_size)
        .offset(offset)
    )

    return PaginatedOut(
        count=total,
        page=page,
        page_size=page_size,
        results=[_to_list_out(livre) for livre in livres],
    )


async def creer_livre(data: LivreIn) -> dict:
    existing = await Livre.select().where(Livre.isbn == data.isbn).first()
    if existing:
        raise ISBNAlreadyExistsException(data.isbn)

    donnees = data.model_dump()
    donnees.pop("couverture", None)

    if data.couverture is not None:
        content_type = data.couverture.content_type or "image/jpeg"
        file_bytes = await data.couverture.read()
        object_name = upload_couverture(file_bytes, content_type)
        donnees["couverture_url"] = object_name

    if donnees.get("categorie") is not None:
        donnees["categorie"] = UUID(str(donnees["categorie"]))

    livre = await Livre.insert(Livre(**donnees)).returning(*Livre.all_columns())
    row = livre[0]
    row["couverture_url_publique"] = get_couverture_url(row.get("couverture_url", ""))
    return row


async def get_livre(livre_id: UUID) -> dict:
    livre = await (
        Livre
        .select(*Livre.all_columns(), Livre.categorie._.nom.as_alias("categorie_nom"))
        .where((Livre.id == livre_id) & Livre.actif.eq(True))
        .first()
    )
    if not livre:
        raise LivreNotFoundException(livre_id)
    livre["couverture_url_publique"] = get_couverture_url(livre.get("couverture_url", ""))
    return livre


async def modifier_partiellement(livre_id: UUID, data: LivrePatchIn) -> dict:
    livre = await Livre.objects().where(
        (Livre.id == livre_id) & Livre.actif.eq(True)
    ).first()
    if not livre:
        raise LivreNotFoundException(livre_id)

    donnees = data.model_dump(exclude_none=True)
    if donnees.get("categorie") is not None:
        donnees["categorie"] = UUID(str(donnees["categorie"]))

    for key, value in donnees.items():
        setattr(livre, key, value)
    await livre.save()
    return await get_livre(livre_id)


async def supprimer_livre(livre_id: UUID) -> None:
    livre = await Livre.objects().where(
        (Livre.id == livre_id) & Livre.actif.eq(True)
    ).first()
    if not livre:
        raise LivreNotFoundException(livre_id)

    if livre.couverture_url:
        try:
            delete_couverture(livre.couverture_url)
        except Exception as e:
            logger.warning(f"Erreur suppression couverture ignorée : {e}")

    await Livre.update({Livre.actif: False}).where(Livre.id == livre_id)


async def rechercher_livres(
    q: Optional[str] = None,
    categorie: Optional[UUID] = None,
    langue: Optional[str] = None,
    annee_min: Optional[int] = None,
    annee_max: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedOut:
    filters: list[Where | Or] = [Livre.actif.eq(True)]

    if q:
        filters.append(
            Livre.titre.ilike(f"%{q}%")
            | Livre.auteur.ilike(f"%{q}%")
            | Livre.isbn.ilike(f"%{q}%")
            | Livre.description.ilike(f"%{q}%")
            | Livre.editeur.ilike(f"%{q}%")
        )
    if categorie:
        filters.append(Livre.categorie == categorie)
    if langue:
        filters.append(Livre.langue == langue)
    if annee_min:
        filters.append(Livre.annee_publication >= annee_min)
    if annee_max:
        filters.append(Livre.annee_publication <= annee_max)

    total = await Livre.count().where(*filters)
    offset = (page - 1) * page_size
    livres = await (
        Livre
        .select(*Livre.all_columns(), Livre.categorie._.nom.as_alias("categorie_nom"))
        .where(*filters)
        .order_by(Livre.titre)
        .limit(page_size)
        .offset(offset)
    )

    return PaginatedOut(
        count=total,
        page=page,
        page_size=page_size,
        results=[_to_list_out(livre) for livre in livres],
    )


async def get_quantite_totale(livre_id: UUID) -> dict:
    livre = await Livre.select(
        Livre.id, Livre.quantite_totale, Livre.actif
    ).where(Livre.id == livre_id).first()
    if not livre:
        raise LivreNotFoundException(livre_id)
    return livre


async def maj_disponibilite(livre_id: UUID) -> dict:
    livre = await Livre.objects().where(
        (Livre.id == livre_id) & Livre.actif.eq(True)
    ).first()
    if not livre:
        raise LivreNotFoundException(livre_id)
    return {
        "message": "Disponibilité récupérée avec succès.",
        "titre": livre.titre,
        "isbn": livre.isbn,
        "quantite_totale": livre.quantite_totale,
        "actif": livre.actif,
        "couverture_url": livre.couverture_url,
    }


# ─── Helpers ─────────────────────────────────────────────────
def _to_list_out(data: dict) -> LivreListOut:
    token = data.get("couverture_url", "")
    return LivreListOut(
        id=data["id"],
        titre=data["titre"],
        auteur=data["auteur"],
        isbn=data["isbn"],
        langue=data["langue"],
        categorie_nom=data.get("categorie_nom"),
        quantite_totale=data["quantite_totale"],
        couverture_url=token,
        couverture_url_publique=get_couverture_url(token),
    )