from loans.models import Emprunt
from loans.app.domain.loan import Loan, LoanStatus
from loans.app.ports.loan_repository import LoanRepository

#  TODO: A fixer


class LoanRepositoryImpl(LoanRepository):
    def __init__(self):
        pass

    def save(self, loan: Loan) -> None:
        # Convertir le domaine Loan en modèle Django et sauvegarder

        emprunt = Emprunt(
            id=loan.id,
            livre_id=loan.book.id,
            utilisateur_id=loan.borrower_id,
            date_retour_prevue=loan.term,
            statut=loan.status.value  # TODO: To fix: Le mapper avec celui du model
        )
        emprunt.save()

    def find_by_id(self, loan_id: str) -> Loan:
        # TODO: check si la methode .get() renvoie None si item non trouvé ou si elle lève une exception
        emprunt = Emprunt.objects.get(id=loan_id)
        loan = Loan(
            id=emprunt.id,
            borrower_id=emprunt.utilisateur_id,
            book=None,
            reader=None,
            term=emprunt.date_retour_prevue,
            status=LoanStatus(emprunt.statut)
        )
        return loan

    def count_active_loans_by_book_id(self, book_id: str) -> int:
        return Emprunt.objects.filter(livre_id=book_id, statut='EN_COURS').count()

    def already_borrowed_by_reader_and_not_returned(self, book_id: str, reader_id: str) -> bool:
        return Emprunt.objects.filter(livre_id=book_id, utilisateur_id=reader_id, statut='EN_COURS').exists()

    def find_active_loans_by_reader_id(self, reader_id: str) -> list[Loan]:
        # Oulbnie pour le moment
        raise NotImplementedError("Method not implemented yet")

    def find_active_loans_by_book_id(self, book_id: str) -> list[Loan]:
        # Oulbnie pour le moment
        raise NotImplementedError("Method not implemented yet")

    def find_all_active_loans(self) -> list[Loan]:
        # Oulbnie pour le moment
        raise NotImplementedError("Method not implemented yet")
