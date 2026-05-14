

from datetime import date
from typing import List, Optional, Protocol

from src.loans.app.domain.email import Email
from src.loans.app.domain.loan import Loan


class LoanRepository(Protocol):
    def save(self, loan: Loan) -> None:
        raise NotImplementedError

    def find_by_id(self, loan_id: str) -> Optional[Loan]:
        raise NotImplementedError

    def count_active_loans_by_book_id(self, book_id: str) -> int:
        raise NotImplementedError

    def already_borrowed_by_reader_and_not_returned(self, book_id: str, reader_id: str) -> bool:
        raise NotImplementedError

    def rate(self, loan_id: str, rating: int) -> None:
        raise NotImplementedError

    def has_ever_borrowed_book(self, user_id: str, book_id: str) -> bool:
        raise NotImplementedError

    def has_already_rated(self, loan_id: str) -> bool:
        raise NotImplementedError

    def get_borrower_emails_with_loan_due_in_3_days(self, reference_date: date) -> List[Email]:
        raise NotImplementedError

    def get_borrower_emails_with_overdue_loans(self, reference_date: date) -> List[Email]:
        raise NotImplementedError
