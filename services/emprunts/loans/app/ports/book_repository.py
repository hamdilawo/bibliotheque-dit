from typing import Optional, Protocol

from services.emprunts.loans.app.domain.book import Book


class BookRepository(Protocol):
    def get_book_by_id(self, book_id: str) -> Optional[Book]:
        raise NotImplementedError
