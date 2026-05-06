from datetime import date

import requests
# httpx
from typing import Optional

from src.loans.app.domain.book import Book
from src.loans.app.ports.book_service_interface import BookServiceInterface
from src.loans.client import ServiceException


class BookService(BookServiceInterface):
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_book_by_id(self, book_id: str) -> Optional[Book]:
        """Récupère les infos d'un livre."""

        try:
            url = f"{self.base_url}/api/livres/{book_id}/"
            response = requests.get(url, timeout=5)
            if response.status_code == 404:
                return None
            response.raise_for_status()
            book = Book(
                id=response.json()['id'],
                title=response.json()['title'],
                author=response.json()['author'],
                numbers_of_copies=response.json()['numbers_of_copies'],
                isbn=response.json()['isbn']
            )
            return book
        except requests.ConnectionError:
            raise ServiceException("Service Livres indisponible.", 503)
        except requests.Timeout:
            raise ServiceException("Service Livres trop lent.", 504)

    def new_loan(self, book_id: str, reader_id: str, term: date) -> None:
        raise NotImplementedError(
            "book_repo.new_loan() Method not implemented yet")


class FakeBookService(BookServiceInterface):
    def __init__(self,):
        ...

    def get_book_by_id(self, book_id: str) -> Optional[Book]:
        """Récupère les infos d'un livre."""

        book = Book(
            id=book_id,
            title="Untitled Book",
            author="Unknown Author",
            numbers_of_copies=1,
            isbn="978-0-123456"
        )

        return book

    def new_loan(self, book_id: str, reader_id: str, term: date) -> None:
        return
