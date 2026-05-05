

from dataclasses import dataclass
from datetime import date
from typing import Optional

from loans.app.domain.email import Email
from loans.app.domain.loan import Loan
from loans.app.domain.reader import Reader
from loans.app.ports.book_repository import BookRepository
from loans.app.ports.loan_repository import LoanRepository


@dataclass(frozen=True)
class BorrowCommand:
    book_id: str
    nb_copies: int
    reader_id: str
    reader_email: str
    reader_name: str

    term: Optional[date] = None


class BorrowABook():
    def __init__(self, loan_repository: LoanRepository, book_repository: BookRepository):
        self.loan_repository = loan_repository
        self.book_repository = book_repository

    def execute(self, command: BorrowCommand) -> Loan:

        already_borrowed = self.loan_repository.already_borrowed_by_reader_and_not_returned(
            book_id=command.book_id, reader_id=command.reader_id)

        if already_borrowed:
            raise Exception(
                "You have already borrowed this book and not returned it yet")

        book = self.book_repository.get_book_by_id(
            command.book_id)  # Verifier l exsista,ce du livre

        if not book:
            raise ValueError("Book not found")

        count_loans = self.loan_repository.count_active_loans_by_book_id(
            book.id)

        if count_loans >= book.numbers_of_copies:
            raise Exception("No more copies available for this book")

        reader = Reader(id=command.reader_id, name=command.reader_name,
                        email=Email(command.reader_email))

        loan = Loan.new(book=book, reader=reader, term=command.term)

        self.loan_repository.save(loan)

        return loan
