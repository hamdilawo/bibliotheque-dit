from dataclasses import dataclass
from src.loans.app.ports.loan_repository import LoanRepository


@dataclass
class RateBookCommand:
    loan_id: str
    user_id: str
    rating: int  # 1 à 5


class RateBook:
    def __init__(self, loan_repository: LoanRepository):
        self.loan_repository = loan_repository

    def execute(self, command: RateBookCommand) -> None:
        # 1. Récupérer l'emprunt
        loan = self.loan_repository.find_by_id(command.loan_id)
        if not loan:
            raise ValueError("Emprunt introuvable.")

        # 2. Vérifier que le livre a bien été emprunté par cet utilisateur
        if loan.borrower_id != command.user_id:
            raise PermissionError(
                "Vous ne pouvez pas noter un livre que vous n'avez pas emprunté.")

        # 3. Vérifier que le livre a été retourné
        if not loan.is_returned:
            raise ValueError(
                "Vous ne pouvez noter un livre qu'après l'avoir retourné.")

        # 4. Vérifier que la note est valide
        if not (1 <= command.rating <= 5):
            raise ValueError("La note doit être entre 1 et 5.")

        # 5. Enregistrer la note
        self.loan_repository.rate(command.loan_id, command.rating)