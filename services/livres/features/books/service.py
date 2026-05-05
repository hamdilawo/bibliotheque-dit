"""
Service Livres — logique métier.
Sépare la logique des endpoints (controller) de l'accès aux données.
"""
from typing import Optional

from features.books.tables import Livre, Categorie
from features.books.schemas import LivreIn, LivrePatchIn, LivreListOut, LivreDetailOut, PaginatedOut
from core.exceptions import (
    LivreNotFoundException, ISBNAlreadyExistsException,
    StockInsuffisantException, StockDepaseeException,
)


# ─── Catégories ──────────────────────────────────────────────

async def lister_categories() -> list[dict]:
    categories = await Categorie.select().order_by(Categorie.nom)
    result = []
    for cat in categories:
        nb = await Livre.count().where(
            Livre.categorie == cat["id"], Livre.actif == True
        )
        result.append({**cat, "nombre_livres": nb})
    return result


async def creer_categorie(nom: str, description: str) -> dict:
    cat = await Categorie.insert(
        Categorie(nom=nom, description=description)
    ).returning(*Categorie.all_columns())
    return cat[0]


async def get_categorie(categorie_id: int) -> dict:
    cat = await Categorie.select().where(Categorie.id == categorie_id).first()
    if not cat:
        raise LivreNotFoundException(categorie_id)
    nb = await Livre.count().where(
        Livre.categorie == categorie_id, Livre.actif == True
    )
    return {**cat, "nombre_livres": nb}


# ─── Livres ───────────────────────────────────────────────────

async def lister_livres(page: int = 1, page_size: int = 20, sort: str = "titre") -> PaginatedOut:
    offset = (page - 1) * page_size
    total = await Livre.count().where(Livre.actif == True)

    sort_col = getattr(Livre, sort, Livre.titre)
    livres = await (
        Livre
        .select(*Livre.all_columns(), Livre.categorie._.nom.as_alias("categorie_nom"))
        .where(Livre.actif == True)
        .order_by(sort_col)
        .limit(page_size)
        .offset(offset)
    )

    return PaginatedOut(
        count=total,
        page=page,
        page_size=page_size,
        results=[_to_list_out(l) for l in livres]
    )


async def creer_livre(data: LivreIn) -> dict:
    existing = await Livre.select().where(Livre.isbn == data.isbn).first()
    if existing:
        raise ISBNAlreadyExistsException(data.isbn)

    livre = await Livre.insert(
        Livre(**data.model_dump())
    ).returning(*Livre.all_columns())
    result = livre[0]
    # ✅ Ajouter disponible (propriété calculée, pas dans le dict Piccolo)
    result["disponible"] = result["quantite_disponible"] > 0
    return result


async def get_livre(livre_id: int) -> dict:
    livre = await (
        Livre
        .select(*Livre.all_columns(), Livre.categorie._.nom.as_alias("categorie_nom"))
        .where(Livre.id == livre_id, Livre.actif == True)
        .first()
    )
    if not livre:
        raise LivreNotFoundException(livre_id)
    # ✅ Ajouter disponible (propriété calculée, pas dans le dict Piccolo)
    livre["disponible"] = livre["quantite_disponible"] > 0
    return livre


async def modifier_livre(livre_id: int, data: LivreIn) -> dict:
    livre = await Livre.objects().where(Livre.id == livre_id, Livre.actif == True).first()
    if not livre:
        raise LivreNotFoundException(livre_id)

    for key, value in data.model_dump().items():
        setattr(livre, key, value)
    await livre.save()
    return await get_livre(livre_id)


async def modifier_partiellement(livre_id: int, data: LivrePatchIn) -> dict:
    livre = await Livre.objects().where(Livre.id == livre_id, Livre.actif == True).first()
    if not livre:
        raise LivreNotFoundException(livre_id)

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(livre, key, value)
    await livre.save()
    return await get_livre(livre_id)


async def supprimer_livre(livre_id: int) -> None:
    """Soft delete — désactive le livre sans le supprimer."""
    livre = await Livre.objects().where(Livre.id == livre_id, Livre.actif == True).first()
    if not livre:
        raise LivreNotFoundException(livre_id)
    livre.actif = False
    await livre.save()


async def rechercher_livres(
    q: Optional[str] = None,
    categorie: Optional[int] = None,
    langue: Optional[str] = None,
    disponible: Optional[bool] = None,
    annee_min: Optional[int] = None,
    annee_max: Optional[int] = None,
    page: int = 1,
    page_size: int = 20,
) -> PaginatedOut:
    # ✅ Construire les filtres dans une liste réutilisable
    filters = [Livre.actif == True]

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
    if disponible is True:
        filters.append(Livre.quantite_disponible > 0)
    elif disponible is False:
        filters.append(Livre.quantite_disponible == 0)
    if annee_min:
        filters.append(Livre.annee_publication >= annee_min)
    if annee_max:
        filters.append(Livre.annee_publication <= annee_max)

    # ✅ Utiliser les mêmes filtres pour count ET select
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
        results=[_to_list_out(l) for l in livres]
    )


async def livres_disponibles(page: int = 1, page_size: int = 20) -> PaginatedOut:
    total = await Livre.count().where(Livre.actif == True, Livre.quantite_disponible > 0)
    offset = (page - 1) * page_size
    livres = await (
        Livre
        .select(*Livre.all_columns(), Livre.categorie._.nom.as_alias("categorie_nom"))
        .where(Livre.actif == True, Livre.quantite_disponible > 0)
        .order_by(Livre.titre)
        .limit(page_size)
        .offset(offset)
    )
    return PaginatedOut(
        count=total,
        page=page,
        page_size=page_size,
        results=[_to_list_out(l) for l in livres]
    )


async def maj_disponibilite(livre_id: int, action: str, quantite: int) -> dict:
    """Appelé par le service Emprunts pour réserver ou retourner."""
    livre = await Livre.objects().where(Livre.id == livre_id, Livre.actif == True).first()
    if not livre:
        raise LivreNotFoundException(livre_id)

    if action == "reserver":
        if livre.quantite_disponible < quantite:
            raise StockInsuffisantException(livre.quantite_disponible, quantite)
        livre.quantite_disponible -= quantite
        message = f"Réservation de {quantite} exemplaire(s) effectuée."
    else:
        if livre.quantite_disponible + quantite > livre.quantite_totale:
            raise StockDepaseeException(livre.quantite_totale)
        livre.quantite_disponible += quantite
        message = f"Retour de {quantite} exemplaire(s) enregistré."

    await livre.save()
    return {
        "message": message,
        "quantite_disponible": livre.quantite_disponible,
        "quantite_totale": livre.quantite_totale,
        "disponible": livre.quantite_disponible > 0,
    }


# ─── Helpers ─────────────────────────────────────────────────
def _to_list_out(data: dict) -> LivreListOut:
    return LivreListOut(
        id=data["id"],
        titre=data["titre"],
        auteur=data["auteur"],
        isbn=data["isbn"],
        langue=data["langue"],
        categorie_nom=data.get("categorie_nom"),
        quantite_disponible=data["quantite_disponible"],
        quantite_totale=data["quantite_totale"],
        disponible=data["quantite_disponible"] > 0,
        couverture_url=data.get("couverture_url", ""),
    )