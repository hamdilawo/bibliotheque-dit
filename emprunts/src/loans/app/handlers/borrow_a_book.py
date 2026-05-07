

from dataclasses import dataclass
from datetime import date
from typing import Optional

from src.loans.app.domain.email import Email
from src.loans.app.domain.loan import Loan
from src.loans.app.domain.reader import Reader
from src.loans.app.domain.user import User
from src.loans.app.ports.book_service_interface import BookServiceInterface
from src.loans.app.ports.loan_repository import LoanRepository


@dataclass(frozen=True)
class BorrowCommand:
    book_id: str
    user: User
    nb_copies: int = 1
    term: Optional[date] = None
    notes: str | None = None


class BorrowABook():
    def __init__(self, loan_repository: LoanRepository, book_service: BookServiceInterface):
        self.loan_repository = loan_repository
        self.book_service = book_service

    def execute(self, command: BorrowCommand) -> Loan:

        already_borrowed = self.loan_repository.already_borrowed_by_reader_and_not_returned(
            book_id=command.book_id, reader_id=command.user.id)

        if already_borrowed:
            raise Exception(
                "You have already borrowed this book and not returned it yet")

        book = self.book_service.get_book_by_id(
            command.book_id)  # Verifier l exsista,ce du livre

        if not book:
            raise ValueError("Book not found")

        count_loans = self.loan_repository.count_active_loans_by_book_id(
            book_id=command.book_id)

        if count_loans >= book.numbers_of_copies:
            raise Exception("No more copies available for this book")

        reader = Reader(id=command.user.id, name=command.user.name,
                        email=Email(command.user.email))

        loan = Loan.new(book=book, reader=reader)

        self.loan_repository.save(loan)

        try:
            self.book_service.new_loan(
                book_id=command.book_id, reader_id=command.user.id, term=loan.term)
        except Exception as e:
            # TODO: faire un rollback de l'emprunt dans la base de données
            # Ou Enregistrer une tâche de compensation à exécuter plus tard pour corriger l'état du système
            raise Exception(
                f'Loan enregistré mais erreur service livres: {e}')

        return loan
