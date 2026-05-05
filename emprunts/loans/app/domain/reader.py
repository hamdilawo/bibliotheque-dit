from dataclasses import dataclass

from loans.app.domain.email import Email


@dataclass(kw_only=True, frozen=True)
class Reader:
    id: str
    name: str
    email: Email

    def __post_init__(self):
        if not self.name:
            raise ValueError("Reader name cannot be empty")

    def __str__(self):
        return f"{self.name} <{self.email}>"
