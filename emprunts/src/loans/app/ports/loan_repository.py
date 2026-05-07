

from typing import Optional, Protocol

from src.loans.app.domain.loan import Loan


class LoanRepository(Protocol):
    def save(self, loan: Loan) -> None:
        """Enregistre un emprunt dans la base de données."""
        raise NotImplementedError

    def complete(self, loan: Loan) -> None:
        """Enregistre un emprunt dans la base de données."""
        raise NotImplementedError

    def find_by_id(self, loan_id: str) -> Optional[Loan]:
        """Récupère un prêt par son ID."""
        raise NotImplementedError

    def count_active_loans_by_book_id(self, book_id: str) -> int:
        """Compte le nombre d'emprunts actifs pour un livre donné."""
        raise NotImplementedError

    def already_borrowed_by_reader_and_not_returned(self, book_id: str, reader_id: str) -> bool:
        """Vérifie si le livre a déjà été emprunté par le lecteur et n'a pas encore été retourné."""
        raise NotImplementedError
