from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from datetime import date
import logging
from typing import Callable, Optional

from loans.app.domain.email import Email
from loans.app.domain.loan import Loan
from loans.app.domain.reader import Reader
from loans.app.domain.user import User
from loans.app.ports.book_service_interface import BookServiceInterface
from loans.app.ports.loan_repository import LoanRepository
from loans.app.ports.email_service import EmailServiceInterface

logger = logging.getLogger(__name__)

NEW_LOAN_EMAIL_TEMPLATE_ID = "NEW_LOAN_EMAIL_TEMPLATE_ID_0001"


@dataclass(frozen=True)
class BorrowCommand:
    book_id: str
    user: User
    nb_copies: int = 1
    term: Optional[date] = None
    comment: str | None = None


class BookAlreadyBorrowedException(Exception):
    ...


class NoCopiesAvailableException(Exception):
    ...


class BorrowABook:
    def __init__(
        self,
        loan_repository: LoanRepository,
        book_service: BookServiceInterface,
        email_service: EmailServiceInterface,
        executor: ThreadPoolExecutor | None = None,
    ):
        self.loan_repository = loan_repository
        self.book_service = book_service
        self.email_service = email_service
        self._executor = executor or ThreadPoolExecutor(max_workers=4)

    def execute(self, command: BorrowCommand) -> Loan:
        already_borrowed = self.loan_repository.already_borrowed_by_reader_and_not_returned(
            book_id=command.book_id, reader_id=command.user.id
        )
        if already_borrowed:
            raise BookAlreadyBorrowedException(
                "You have already borrowed this book and not returned it yet"
            )

        book = self.book_service.get_book_by_id(command.book_id)
        if not book:
            raise ValueError("Book not found")

        if self.loan_repository.count_active_loans_by_book_id(command.book_id) >= book.numbers_of_copies:
            raise NoCopiesAvailableException(
                "No more copies available for this book")

        reader = Reader(id=command.user.id, name=command.user.name,
                        email=Email(command.user.email))
        loan = Loan.new(book=book, reader=reader,
                        term=command.term, comment=command.comment)

        loan.approve()

        self.loan_repository.save(loan)

        self._submit(
            self.book_service.new_loan,
            book_id=command.book_id,
            reader_id=command.user.id,
            term=loan.term,
        )
        self._submit(
            self.email_service.send_email_with_template,
            template_id=NEW_LOAN_EMAIL_TEMPLATE_ID,
            email=str(loan.reader.email),
            params={"user_fullname": loan.reader.name,
                    "user_email": loan.reader.email},
        )

        return loan

    def _submit(self, fn: Callable, **kwargs) -> None:
        future = self._executor.submit(fn, **kwargs)
        future.add_done_callback(self._on_task_done)

    @staticmethod
    def _on_task_done(future: Future) -> None:
        exc = future.exception()
        if exc:
            logger.exception(
                "Background task failed: %s",
                future,
                exc_info=exc,
            )
