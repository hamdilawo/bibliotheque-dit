from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Set

from loans.app.domain.book import Book
from loans.app.domain.email import Email
from loans.app.domain.reader import Reader
from loans.adapters.database.models.emprunt import Emprunt
from loans.app.domain.loan import Loan, LoanStatus
from loans.app.ports.loan_repository import LoanRepository


class LoanRepositoryImpl(LoanRepository):
    def __init__(self):
        pass

    def save(self, loan: Loan) -> None:

        # excluded_fields: Set[str] = {"id", "date_emprunt"}

        defaults: Dict[str, Any] = {
            "livre_id": loan.book_id,
            "utilisateur_id": loan.borrower_id,
            "utilisateur_nom": loan.reader.name if loan.reader else '',
            "utilisateur_carte": '',
            "livre_titre": loan.book.title if loan.book else '',
            "livre_isbn": loan.book.isbn if loan.book else '',
            "livre_auteur": loan.book.author if loan.book else '',
            "date_retour_prevue": loan.term,
            "statut": loan.status.value,
            "date_retour_effective": loan.completed_at,
            "penalite_fcfa": Decimal(str(loan.penalty)),
            "jours_retard": loan.jours_retard,
            "comment": loan.comment,
            "utilisateur_email": loan.reader.email,
        }

        _, _ = Emprunt.objects.update_or_create(
            id=loan.id,
            defaults=defaults,
        )

    def find_by_id(self, loan_id: str) -> Optional[Loan]:
        try:
            emprunt = Emprunt.objects.get(id=loan_id)
        except Emprunt.DoesNotExist:
            return None
        return Loan(
            id=emprunt.id,
            borrower_id=emprunt.utilisateur_id,
            book=Book(
                id=emprunt.livre_id,
                title=emprunt.livre_titre,
                isbn=emprunt.livre_isbn,
                author=emprunt.livre_auteur,
            ),
            reader=Reader(
                id=emprunt.utilisateur_id,
                name=emprunt.utilisateur_nom,
                email=Email(emprunt.utilisateur_email) if emprunt.utilisateur_email else None,
            ),
            term=emprunt.date_retour_prevue,
            status=LoanStatus(emprunt.statut),
            penalty=int(emprunt.penalite_fcfa),
            jours_retard=emprunt.jours_retard,
            comment=emprunt.comment,
        )

    def count_active_loans_by_book_id(self, book_id: str) -> int:
        return Emprunt.objects.filter(livre_id=book_id).exclude(statut=LoanStatus.COMPLETED).count()

    def already_borrowed_by_reader_and_not_returned(self, book_id: str, reader_id: str) -> bool:
        borrowed = Emprunt.objects.filter(livre_id=book_id, utilisateur_id=reader_id, ).exclude(
            statut=LoanStatus.COMPLETED).exists()
        return borrowed

    def get_borrower_emails_with_loan_due_in_3_days(self, reference_date: date) -> List[Email]:
        # return [Email(e) for e in ["test1@gmail.com", "test2@gmail.com"]]
        target_date = reference_date + timedelta(days=3)
        emprunts = Emprunt.objects.filter(
            date_retour_prevue=target_date,
            statut=LoanStatus.APPROVED,
            before_notification_is_sent=False,
            utilisateur_email__isnull=False,
        ).exclude(utilisateur_email='')
        return [Email(e.utilisateur_email) for e in emprunts if e.utilisateur_email]

    def get_borrower_emails_with_overdue_loans(self, reference_date: date) -> List[Email]:
        # return [Email(e) for e in ["test1@gmail.com", "test2@gmail.com"]]
        target_date = reference_date + timedelta(days=0)

        emprunts = Emprunt.objects.filter(
            date_retour_prevue__lt=target_date,
            statut__in=[LoanStatus.APPROVED],
            retard_notification_is_sent=False,
            utilisateur_email__isnull=False,
        ).exclude(utilisateur_email='')

        return [Email(e.utilisateur_email) for e in emprunts if e.utilisateur_email]

    def find_active_loans_by_reader_id(self, reader_id: str) -> list[Loan]:
        # Oulbnie pour le moment
        raise NotImplementedError("Method not implemented yet")

    def find_active_loans_by_book_id(self, book_id: str) -> list[Loan]:
        # Oulbnie pour le moment
        raise NotImplementedError("Method not implemented yet")

    def find_all_active_loans(self) -> list[Loan]:
        # Oulbnie pour le moment
        raise NotImplementedError("Method not implemented yet")
    
    def rate(self, loan_id: str, rating: int) -> None:
        Emprunt.objects.filter(id=loan_id).update(rating=rating)

    def has_ever_borrowed_book(self, user_id: str, book_id: str) -> bool:
        return Emprunt.objects.filter(
            utilisateur_id=user_id,
            livre_id=book_id,
            statut=LoanStatus.COMPLETED
        ).exists()

    def has_already_rated(self, loan_id: str) -> bool:
        return Emprunt.objects.filter(id=loan_id, rating__isnull=False).exists()

    def has_ever_borrowed_book(self, user_id: str, book_id: str) -> bool:
        return Emprunt.objects.filter(utilisateur_id=user_id, livre_id=book_id, statut=LoanStatus.COMPLETED).exists()

    def has_already_rated(self, loan_id: str) -> bool:
        return Emprunt.objects.filter(id=loan_id, rating__isnull=False).exists()
