"""
Schemas Pydantic — validation des données entrantes et sortantes.
"""
from datetime import datetime, date
from enum import Enum
from typing import Optional
from pydantic import BaseModel, field_validator, model_validator


class LangueEnum(str, Enum):
    fr = "fr"
    en = "en"
    ar = "ar"
    es = "es"


# ─── Catégorie ───────────────────────────────────────────────
class CategorieOut(BaseModel):
    id: int
    nom: str
    description: str
    nombre_livres: int = 0


class CategorieIn(BaseModel):
    nom: str
    description: str = ""


# ─── Livre — réponse liste (allégée) ─────────────────────────
class LivreListOut(BaseModel):
    id: int
    titre: str
    auteur: str
    isbn: str
    langue: str
    categorie_nom: Optional[str] = None
    quantite_disponible: int
    quantite_totale: int
    disponible: bool
    couverture_url: str = ""


# ─── Livre — réponse détail (complète) ───────────────────────
class LivreDetailOut(BaseModel):
    id: int
    titre: str
    auteur: str
    isbn: str
    editeur: str = ""
    annee_publication: Optional[int] = None
    langue: str
    description: str = ""
    nombre_pages: Optional[int] = None
    categorie: Optional[int] = None
    categorie_nom: Optional[str] = None
    quantite_totale: int
    quantite_disponible: int
    disponible: bool
    couverture_url: str = ""
    actif: bool
    date_ajout: datetime
    date_modification: datetime


# ─── Livre — création ────────────────────────────────────────
class LivreIn(BaseModel):
    titre: str
    auteur: str
    isbn: str
    editeur: str = ""
    annee_publication: Optional[int] = None
    langue: LangueEnum = LangueEnum.fr
    description: str = ""
    nombre_pages: Optional[int] = None
    categorie: Optional[int] = None
    quantite_totale: int = 1
    quantite_disponible: Optional[int] = None
    couverture_url: str = ""

    @field_validator("isbn")
    @classmethod
    def valider_isbn(cls, value: str) -> str:
        """Validation ISBN-13 avec clé de contrôle (algorithme officiel)."""
        value = value.replace("-", "").replace(" ", "")
        if not value.isdigit():
            raise ValueError("L'ISBN ne doit contenir que des chiffres.")
        if len(value) != 13:
            raise ValueError("L'ISBN doit contenir exactement 13 chiffres.")
        total = sum(int(value[i]) * (1 if i % 2 == 0 else 3) for i in range(12))
        cle = (10 - (total % 10)) % 10
        if cle != int(value[12]):
            raise ValueError("ISBN-13 invalide : clé de contrôle incorrecte.")
        return value

    @field_validator("annee_publication")
    @classmethod
    def valider_annee(cls, value: Optional[int]) -> Optional[int]:
        if value is not None:
            annee_courante = date.today().year
            if value < 1000:
                raise ValueError("L'année doit être supérieure à 1000.")
            if value > annee_courante:
                raise ValueError(f"L'année ne peut pas dépasser {annee_courante}.")
        return value

    @model_validator(mode="after")
    def valider_stock(self) -> "LivreIn":
        if self.quantite_disponible is None:
            self.quantite_disponible = self.quantite_totale
        if self.quantite_disponible > self.quantite_totale:
            raise ValueError("La quantité disponible ne peut pas dépasser le total.")
        return self


# ─── Livre — modification partielle PATCH ────────────────────
class LivrePatchIn(BaseModel):
    """ISBN et année non modifiables après création."""
    titre: Optional[str] = None
    auteur: Optional[str] = None
    editeur: Optional[str] = None
    description: Optional[str] = None
    nombre_pages: Optional[int] = None
    langue: Optional[LangueEnum] = None
    quantite_totale: Optional[int] = None
    couverture_url: Optional[str] = None
    actif: Optional[bool] = None
    categorie: Optional[int] = None


# ─── Disponibilité inter-services ────────────────────────────
class DisponibiliteIn(BaseModel):
    action: str  # "reserver" ou "retourner"
    quantite: int = 1

    @field_validator("action")
    @classmethod
    def valider_action(cls, v: str) -> str:
        if v not in ("reserver", "retourner"):
            raise ValueError("L'action doit être 'reserver' ou 'retourner'.")
        return v

    @field_validator("quantite")
    @classmethod
    def valider_quantite(cls, v: int) -> int:
        if v < 1:
            raise ValueError("La quantité doit être au moins 1.")
        return v


# ─── Réponses génériques ─────────────────────────────────────
class DisponibiliteOut(BaseModel):
    message: str
    quantite_disponible: int
    quantite_totale: int
    disponible: bool


class HealthOut(BaseModel):
    status: str
    service: str
    db: str
    version: str


class PaginatedOut(BaseModel):
    count: int
    page: int
    page_size: int
    results: list[LivreListOut]