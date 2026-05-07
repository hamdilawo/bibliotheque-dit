from decimal import Decimal
from typing import Optional

from loans.app.domain.book import Book
from loans.app.domain.email import Email
from loans.app.domain.reader import Reader
from src.loans.adapters.database.models.emprunt import Emprunt
from src.loans.app.domain.loan import Loan, LoanStatus
from src.loans.app.ports.loan_repository import LoanRepository


class LoanRepositoryImpl(LoanRepository):
    def __init__(self):
        pass

    def save(self, loan: Loan) -> None:
        # Convertir le domaine Loan en modèle Django et sauvegarder

        emprunt = Emprunt(
            id=loan.id,
            livre_id=loan.book_id,
            utilisateur_id=loan.borrower_id,
            utilisateur_nom=loan.reader.name if loan.reader else '',
            utilisateur_carte='',  # TODO: ajouter la carte de l'utilisateur si nécessaire
            livre_titre=loan.book.title if loan.book else '',
            livre_isbn=loan.book.isbn if loan.book else '',
            livre_auteur=loan.book.author if loan.book else '',
            date_retour_prevue=loan.term,
            statut=loan.status.value,
            date_retour_effective=loan.completed_at,
            penalite_fcfa=Decimal(str(loan.penalty)),
            jours_retard=loan.jours_retard,
            date_emprunt=loan.borrow_date
        )
        emprunt.save()

    def complete(self, loan: Loan) -> None:
        # Convertir le domaine Loan en modèle Django et sauvegarder

        emprunt = Emprunt(
            id=loan.id,
            livre_id=loan.book_id,
            utilisateur_id=loan.borrower_id,
            utilisateur_nom=loan.reader.name if loan.reader else '',
            utilisateur_carte='',  # TODO: ajouter la carte de l'utilisateur si nécessaire
            livre_titre=loan.book.title if loan.book else '',
            livre_isbn=loan.book.isbn if loan.book else '',
            livre_auteur=loan.book.author if loan.book else '',
            date_retour_prevue=loan.term,
            statut=loan.status.value,
            date_retour_effective=loan.completed_at,
            penalite_fcfa=Decimal(str(loan.penalty)),
            jours_retard=loan.jours_retard,
        )

        emprunt.save(update_fields=['livre_id', 'utilisateur_id', 'utilisateur_nom', 'utilisateur_carte', 'livre_titre',
                     'livre_isbn', 'livre_auteur', 'date_retour_prevue', 'statut', 'date_retour_effective', 'penalite_fcfa', 'jours_retard'])

    def find_by_id(self, loan_id: str) -> Optional[Loan]:
        try:

            emprunt = Emprunt.objects.get(id=loan_id)
            loan = Loan(
                id=emprunt.id,
                borrower_id=emprunt.utilisateur_id,
                book=Book(
                    id=emprunt.livre_id,
                    title=emprunt.livre_titre,
                    isbn=emprunt.livre_isbn,
                    author=emprunt.livre_auteur
                ),
                reader=Reader(
                    id=emprunt.utilisateur_id,
                    name=emprunt.utilisateur_nom,
                    email=Email(emprunt.utilisateur_nom + "@example.com")
                ),
                term=emprunt.date_retour_prevue,
                status=LoanStatus(emprunt.statut),
                penalty=int(emprunt.penalite_fcfa),
                jours_retard=emprunt.jours_retard
            )
            return loan
        except:
            return None

    def count_active_loans_by_book_id(self, book_id: str) -> int:
        return Emprunt.objects.filter(livre_id=book_id).exclude(statut=LoanStatus.COMPLETED).count()

    def already_borrowed_by_reader_and_not_returned(self, book_id: str, reader_id: str) -> bool:
        borrowed = Emprunt.objects.filter(livre_id=book_id, utilisateur_id=reader_id, ).exclude(
            statut=LoanStatus.COMPLETED).exists()
        return borrowed

    def find_active_loans_by_reader_id(self, reader_id: str) -> list[Loan]:
        # Oulbnie pour le moment
        raise NotImplementedError("Method not implemented yet")

    def find_active_loans_by_book_id(self, book_id: str) -> list[Loan]:
        # Oulbnie pour le moment
        raise NotImplementedError("Method not implemented yet")

    def find_all_active_loans(self) -> list[Loan]:
        # Oulbnie pour le moment
        raise NotImplementedError("Method not implemented yet")
