
from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum
from typing import Optional, Self
from uuid import UUID, uuid7
from src.loans.app.domain.book import Book
from src.loans.app.domain.reader import Reader


class LoanStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


DEFAULT_BOOK_LOAN_DURATION_DAYS = 14  # Durée par défaut d'un emprunt en jours


@dataclass(kw_only=True)
class Loan:
    id: UUID
    borrower_id: str
    book: Optional[Book]
    reader: Optional[Reader]
    term: date
    borrow_date: date = field(default_factory=date.today)
    status: LoanStatus = field(default=LoanStatus.PENDING)
    notes: str = ""

    @property
    def book_id(self) -> Optional[str]:
        return self.book.id if self.book else ''

    @classmethod
    def new(cls, book: Book, reader: Reader, term: Optional[date] = None) -> Self:

        if term and term < date.today():
            raise ValueError("Term date cannot be in the past")

        loan = cls(
            id=uuid7(),
            borrower_id=reader.id,
            book=book,
            reader=reader,
            term=term or timedelta(
                days=DEFAULT_BOOK_LOAN_DURATION_DAYS) + date.today(),
            status=LoanStatus.PENDING
        )
        return loan
