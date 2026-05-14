from datetime import date
from typing import Optional, Protocol

from src.loans.app.domain.book import Book


class BookServiceInterface(Protocol):
    def get_book_by_id(self, book_id: str) -> Optional[Book]:
        raise NotImplementedError

    def new_loan(self, book_id: str, reader_id: str, term: date) -> None:
        raise NotImplementedError

    def loan_returned(self, book_id: str, reader_id: str) -> None:
        raise NotImplementedError
