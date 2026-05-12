"""
Exceptions métier du service Livres.
Toutes héritent des exceptions Litestar pour générer automatiquement
les bons codes HTTP sans handler supplémentaire.
"""
from uuid import UUID
from litestar.exceptions import NotFoundException, HTTPException


class LivreNotFoundException(NotFoundException):
    def __init__(self, livre_id: UUID | int | str):
        super().__init__(detail=f"Livre '{livre_id}' introuvable.")


class ISBNAlreadyExistsException(HTTPException):
    status_code = 409

    def __init__(self, isbn: str):
        super().__init__(detail=f"Un livre avec l'ISBN {isbn} existe déjà.")


class StockInsuffisantException(HTTPException):
    status_code = 400

    def __init__(self, disponible: int, demande: int):
        super().__init__(
            detail=f"Stock insuffisant : {disponible} exemplaire(s) disponible(s), "
                   f"{demande} demandé(s)."
        )


class StockDepasseException(HTTPException):
    status_code = 400

    def __init__(self, total: int):
        super().__init__(
            detail=f"Impossible : dépasse le stock total ({total} exemplaires)."
        )
