

from dataclasses import dataclass


@dataclass(frozen=True)
class Book:
    id: str
    title: str
    author: str
    isbn: str
    numbers_of_copies: int = 1
    cover: str = ""

    def __post_init__(self):
        if not self.id:
            raise ValueError("Book ID cannot be empty")
        if not self.title:
            raise ValueError("Book title cannot be empty")
        if not self.author:
            raise ValueError("Book author cannot be empty")
        if not self.isbn:
            raise ValueError("Book ISBN cannot be empty")

    def __str__(self):
        return f"{self.title} by {self.author}"
