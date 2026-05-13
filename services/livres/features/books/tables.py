from enum import Enum
from uuid import uuid4

from piccolo.columns import (
    Varchar, Text, Integer, SmallInt, Boolean,
    Timestamptz, ForeignKey
)
from piccolo.columns.column_types import UUID
from piccolo.table import Table
from core.database import DB


class LangueEnum(str, Enum):
    FR = "fr"
    EN = "en"
    AR = "ar"
    ES = "es"


class Categorie(Table, tablename="categories", db=DB):
    id          = UUID(primary_key=True, default=uuid4)
    nom         = Varchar(length=100, unique=True, null=False)
    description = Text(default="")


class Livre(Table, tablename="livres", db=DB):
    id                = UUID(primary_key=True, default=uuid4)
    titre             = Varchar(length=255, null=False)
    auteur            = Varchar(length=255, null=False)
    isbn              = Varchar(length=13, unique=True, null=False)
    editeur           = Varchar(length=255, default="")
    annee_publication = Integer(null=True)
    langue            = Varchar(length=2, default=LangueEnum.FR.value, choices=LangueEnum)
    description       = Text(default="")
    nombre_pages      = SmallInt(null=True)
    categorie         = ForeignKey(references=Categorie, null=True)
    quantite_totale   = SmallInt(default=1)
    date_ajout        = Timestamptz(auto_now_add=True)
    date_modification = Timestamptz(auto_now=True)
    couverture_url    = Varchar(length=500, default="")
    actif             = Boolean(default=True)
