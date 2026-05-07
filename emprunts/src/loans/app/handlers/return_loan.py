
from loans.app.domain.loan import Loan
from loans.app.ports.book_service_interface import BookServiceInterface
from loans.app.ports.loan_repository import LoanRepository
from loans.client import ServiceException


class ReturnLoan():
    def __init__(self, loan_repository: LoanRepository, book_service: BookServiceInterface) -> None:
        self.loan_repository = loan_repository
        self.book_service = book_service

    def execute(self, loan_id: str) -> Loan:
        """Enregistre le retour d'un emprunt, calcule les pénalités éventuelles,
        et met à jour les deux autres services."""

        loan = self.loan_repository.find_by_id(loan_id)
        if not loan:
            raise ServiceException(f"Emprunt #{loan_id} introuvable.", 404)

        if loan.is_returned:
            return loan

        loan.complete()

        try:
            self.book_service.loan_returned(
                book_id=loan.book_id, reader_id=loan.reader.id)
        except ServiceException as e:
            # TODO: faire un rollback de la transaction
            # Ou Enregistrer une tâche de compensation à exécuter plus tard pour corriger l'état du système
            raise ServiceException(
                f'Retour enregistré mais erreur service livres: {e}')
        self.loan_repository.complete(loan)
        return loan
