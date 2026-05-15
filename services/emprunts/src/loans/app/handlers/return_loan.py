from concurrent.futures import Future, ThreadPoolExecutor
import logging
from typing import Callable

from loans.app.domain.loan import Loan
from loans.app.ports.book_service_interface import BookServiceInterface
from loans.app.ports.loan_repository import LoanRepository
from loans.app.ports.email_service import EmailServiceInterface

logger = logging.getLogger(__name__)

LOAN_RETURNED_EMAIL_TEMPLATE_ID = "LOAN_RETURNED_EMAIL_TEMPLATE_ID_0001"


class LoanNotFoundException(Exception):
    ...


class ReturnLoan:
    def __init__(
        self,
        loan_repository: LoanRepository,
        book_service: BookServiceInterface,
        email_service: EmailServiceInterface,
        executor: ThreadPoolExecutor | None = None,
    ) -> None:
        self.loan_repository = loan_repository
        self.book_service = book_service
        self.email_service = email_service
        self._executor = executor or ThreadPoolExecutor(max_workers=4)

    def execute(self, loan_id: str) -> Loan:
        loan = self.loan_repository.find_by_id(loan_id)
        if not loan:
            raise LoanNotFoundException(f"Emprunt #{loan_id} introuvable.")

        if loan.is_returned:
            return loan

        loan.complete()
        self.loan_repository.save(loan)

        self._submit(
            self.book_service.loan_returned,
            book_id=loan.book_id,
            reader_id=loan.reader.id,
        )
        self._submit(
            self.email_service.send_email_with_template,
            template_id=LOAN_RETURNED_EMAIL_TEMPLATE_ID,
            email=str(loan.reader.email),
            params={
                "user_fullname": loan.reader.name,
                "user_email": loan.reader.email,
                "book_title": loan.book.title,
            },
        )

        return loan

    def _submit(self, fn: Callable, **kwargs) -> None:
        future = self._executor.submit(fn, **kwargs)
        future.add_done_callback(self._on_task_done)

    @staticmethod
    def _on_task_done(future: Future) -> None:
        exc = future.exception()
        if exc:
            logger.exception("Background task failed", exc_info=exc)
