"""
Modèles Piccolo ORM — tables de la base de données.
Piccolo est async natif et s'intègre parfaitement avec Litestar.
"""
from piccolo.columns import (
    Varchar, Text, Integer, Boolean, Timestamp,
    ForeignKey, Serial
)
from piccolo.table import Table
from core.database import DB


class Categorie(Table, db=DB):
    """Table des catégories de livres."""
    id = Serial(primary_key=True)
    nom = Varchar(length=100, unique=True, null=False)
    description = Text(default="")

    class Meta:
        tablename = "categories"


class Livre(Table, db=DB):
    """Table principale des livres."""
    id = Serial(primary_key=True)
    titre = Varchar(length=255, null=False)
    auteur = Varchar(length=255, null=False)

    # ISBN-13 — validé au niveau du schema Pydantic
    isbn = Varchar(length=13, unique=True, null=False)

    editeur = Varchar(length=255, default="")
    annee_publication = Integer(null=True)
    langue = Varchar(length=2, default="fr")
    description = Text(default="")
    nombre_pages = Integer(null=True)

    # Clé étrangère vers Categorie
    categorie = ForeignKey(references=Categorie, null=True)

    quantite_totale = Integer(default=1)
    quantite_disponible = Integer(default=1)

    date_ajout = Timestamp()
    date_modification = Timestamp()

    couverture_url = Varchar(length=500, default="")
    actif = Boolean(default=True)

    class Meta:
        tablename = "livres"

    # ─── Propriétés métier ────────────────────────────────────
    @property
    def disponible(self) -> bool:
        return self.quantite_disponible > 0

    def reserver(self, quantite: int = 1) -> None:
        """Décrémente le stock lors d'un emprunt."""
        if quantite < 1:
            raise ValueError("La quantité doit être au moins 1.")
        if self.quantite_disponible < quantite:
            raise ValueError(
                f"Seulement {self.quantite_disponible} exemplaire(s) "
                f"disponible(s), {quantite} demandé(s)."
            )
        self.quantite_disponible -= quantite

    def retourner(self, quantite: int = 1) -> None:
        """Incrémente le stock lors d'un retour."""
        if quantite < 1:
            raise ValueError("La quantité doit être au moins 1.")
        if self.quantite_disponible + quantite > self.quantite_totale:
            raise ValueError(
                f"Impossible : dépasse le stock total ({self.quantite_totale})."
            )
        self.quantite_disponible += quantite