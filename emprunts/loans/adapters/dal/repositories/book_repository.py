import requests
# httpx
from typing import Optional

from loans.app.domain.book import Book
from loans.app.ports.book_repository import BookRepository
from loans.client import ServiceException


class BookRepositoryImpl(BookRepository):
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


class FakeBookRepositoryImpl(BookRepository):
    def __init__(self,):
        ...

    def get_book_by_id(self, book_id: str) -> Optional[Book]:
        """Récupère les infos d'un livre."""

        book = Book(
            id="book_id",
            title="Untitled Book",
            author="Unknown Author",
            numbers_of_copies=1,
            isbn="978-0-123456"
        )

        return book
