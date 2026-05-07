from dataclasses import dataclass
from src.loans.app.ports.loan_repository import LoanRepository


@dataclass
class RateBookCommand:
    loan_id: str
    user_id: str
    rating: int


class RateBook:
    def __init__(self, loan_repository: LoanRepository):
        self.loan_repository = loan_repository

    def execute(self, command: RateBookCommand) -> None:
        loan = self.loan_repository.find_by_id(command.loan_id)
        if not loan:
            raise ValueError("Emprunt introuvable.")
        if loan.borrower_id != command.user_id:
            raise PermissionError("Vous ne pouvez pas noter un livre que vous n avez pas emprunte.")
        if not loan.is_returned:
            raise ValueError("Vous ne pouvez noter un livre qu apres l avoir retourne.")
        if not (1 <= command.rating <= 5):
            raise ValueError("La note doit etre entre 1 et 5.")
        if not self.loan_repository.has_ever_borrowed_book(command.user_id, loan.book_id):
            raise PermissionError("Vous ne pouvez pas noter un livre que vous n avez jamais emprunte.")
        if self.loan_repository.has_already_rated(command.loan_id):
            raise ValueError("Vous avez deja note cet emprunt.")
        self.loan_repository.rate(command.loan_id, command.rating)
