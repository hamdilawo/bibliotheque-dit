
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
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
    book: Book
    reader: Reader
    term: date
    borrow_date: date = field(default_factory=date.today)
    status: LoanStatus = field(default=LoanStatus.PENDING)
    comment: Optional[str] = None
    penalty: int = 0
    completed_at: Optional[date] = None
    jours_retard: int = 0

    @property
    def book_id(self) -> str:
        return self.book.id if self.book else ''

    @property
    def is_returned(self) -> bool:
        return self.status == LoanStatus.COMPLETED

    @classmethod
    def new(cls, book: Book, reader: Reader, term: Optional[date] = None, comment: Optional[str] = None) -> Self:

        if term and term < date.today():
            raise ValueError("Term date cannot be in the past")

        loan = cls(
            id=uuid7(),
            borrower_id=reader.id,
            book=book,
            borrow_date=date.today(),
            comment=comment,
            reader=reader,
            term=term or timedelta(
                days=DEFAULT_BOOK_LOAN_DURATION_DAYS) + date.today(),
            status=LoanStatus.PENDING
        )
        return loan

    def approve(self) -> None:
        self.status = LoanStatus.APPROVED

    def complete(self):

        if self.status != LoanStatus.APPROVED:
            raise Exception("Ce emprunt n'a pas été approuvé.")
        today = datetime.now(timezone.utc).date()
        jours_retard = 0
        penalty = 0

        if today > self.term:
            jours_retard = (today - self.term).days
            penalty = jours_retard * 200  # TODO: Mettre dans une CONST

        self.status = LoanStatus.COMPLETED
        self.borrow_date = date.today()
        self.completed_at = date.today()
        self.penalty = penalty
        self.jours_retard = jours_retard
