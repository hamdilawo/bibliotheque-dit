from enum import Enum

from piccolo.columns import (
    Varchar, Text, Integer, SmallInt, Boolean,
    Timestamptz, ForeignKey, Serial
)
from piccolo.table import Table
from core.database import DB


# ✅ Enum propre pour Piccolo
class LangueEnum(str, Enum):
    FR = "fr"
    EN = "en"
    AR = "ar"
    ES = "es"


class Categorie(Table, db=DB):
    id = Serial(primary_key=True)
    nom = Varchar(length=100, unique=True, null=False)
    description = Text(default="")

    class Meta:
        tablename = "categories"


class Livre(Table, db=DB):
    id = Serial(primary_key=True)
    titre = Varchar(length=255, null=False)
    auteur = Varchar(length=255, null=False)
    isbn = Varchar(length=13, unique=True, null=False)
    editeur = Varchar(length=255, default="")
    annee_publication = Integer(null=True)

    # ✅ FIX ICI
    langue = Varchar(
        length=2,
        default=LangueEnum.FR,
        choices=LangueEnum
    )

    description = Text(default="")
    nombre_pages = SmallInt(null=True)
    categorie = ForeignKey(references=Categorie, null=True)
    quantite_totale = SmallInt(default=1)
    quantite_disponible = SmallInt(default=1)
    date_ajout = Timestamptz(auto_now_add=True)
    date_modification = Timestamptz(auto_now=True)
    couverture_url = Varchar(length=500, default="")
    actif = Boolean(default=True)

    class Meta:
        tablename = "livres"

    @property
    def disponible(self) -> bool:
        return self.quantite_disponible > 0

    def reserver(self, quantite: int = 1) -> None:
        if quantite < 1:
            raise ValueError("La quantité doit être au moins 1.")
        if self.quantite_disponible < quantite:
            raise ValueError(
                f"Seulement {self.quantite_disponible} exemplaire(s) "
                f"disponible(s), {quantite} demandé(s)."
            )
        self.quantite_disponible -= quantite

    def retourner(self, quantite: int = 1) -> None:
        if quantite < 1:
            raise ValueError("La quantité doit être au moins 1.")
        if self.quantite_disponible + quantite > self.quantite_totale:
            raise ValueError(
                f"Impossible : dépasse le stock total ({self.quantite_totale})."
            )
        self.quantite_disponible += quantite