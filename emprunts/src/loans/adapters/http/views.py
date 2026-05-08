
from src.loans.app.handlers.notify_users_on_loan_overdue import NotifyUsersOnLoanOverdue
from src.loans.app.handlers.notify_users_before_loan_due import NotifyUsers3DaysBeforeLoanDue
from src.loans.adapters.services.brevo_email_service import BrevoEmailService
from src.loans.app.handlers.return_loan import ReturnLoan
from src.loans.adapters.database.repositories.loan_repository import LoanRepositoryImpl
from src.loans.app.handlers.borrow_a_book import BorrowABook, BorrowCommand
from src.loans.adapters.database.models.emprunt import Emprunt
from rest_framework import serializers, viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter
import csv
import io
from src.loans.adapters.services.book import FakeBookService
from .serializers import (
    BorrowABookResponseSerializer,
    CreerEmpruntSerializer, RetourEmpruntSerializer,
    ReturnLoanResponseSerializer
)
from ...client import LivresClient, UtilisateursClient, ServiceException


class EmpruntViewSet(viewsets.ViewSet):
    """
    Gestion complète des emprunts.
    """
    # filter_backends = [filters.OrderingFilter]
    # ordering_fields = ['date_emprunt', 'date_retour_prevue', 'statut']
    # ordering = ['-date_emprunt']
    # http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        return Emprunt.objects.all()

    def get_serializer_class(self):
        if self.action == "emprunter":
            return CreerEmpruntSerializer()
        if self.action in ['retourner']:
            return RetourEmpruntSerializer

    # ------------------------------------------------------------------ #
    # Endpoint 1 — Emprunter un livre
    # ------------------------------------------------------------------ #
    @extend_schema(request=CreerEmpruntSerializer, summary="Emprunter un livre",
                   description="Crée un nouvel emprunt pour l'utilisateur authentifié. Vérifie la disponibilité du livre et envoie une confirmation par email.")
    @action(detail=False, methods=['post'])
    def emprunter(self, request):

        try:
            serializer = CreerEmpruntSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

        except serializers.ValidationError as e:
            return Response({'error': 'Données invalides. Veuillez vérifier les champs.', "error_details": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {'error': 'Données invalides. Veuillez vérifier les champs.',
                    "error_details": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        command = BorrowCommand(
            book_id=data.get("book_id", ""),
            user=request.authenticated_user,
            term=data.get("term", None),
            comment=data.get("comment", None)
        )

        loan_repository = LoanRepositoryImpl()
        # book_repository = BookRepositoryImpl(
        #     "http://service-livres:8000")  # URL du service Livres

        book_service = FakeBookService()
        brevo_email_service = BrevoEmailService()

        borrow_a_book = BorrowABook(
            email_service=brevo_email_service,
            loan_repository=loan_repository, book_service=book_service)

        try:
            loan = borrow_a_book.execute(command)
        except ServiceException as e:
            return Response({'error': str(e)}, status=e.status_code or 400)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        response = BorrowABookResponseSerializer(loan).data
        return Response({'message': 'Emprunt créé avec succès.', "data": response}, status=status.HTTP_201_CREATED)

    @extend_schema(request=RetourEmpruntSerializer, summary="Retourner un livre",
                   description="Enregistre le retour d'un emprunt. Calcule les éventuels jours de retard et la pénalité associée, puis notifie l'utilisateur par email.")
    @action(detail=False, methods=['post'])
    def retourner(self, request):

        loan_repo = LoanRepositoryImpl()
        brevo_email_service = BrevoEmailService()

        try:
            serializer = RetourEmpruntSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return Response({'error': 'Données invalides. Veuillez vérifier les champs.', "error_details": e.detail}, status=status.HTTP_400_BAD_REQUEST)

        return_loan = ReturnLoan(
            email_service=brevo_email_service,
            loan_repository=loan_repo, book_service=FakeBookService())

        try:
            loan_returned = return_loan.execute(
                loan_id=serializer.data["loan_id"])
        except ServiceException as e:
            return Response({'error': str(e)}, status=e.status_code or 400)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        response_data = ReturnLoanResponseSerializer(loan_returned).data

        if loan_returned.jours_retard > 0:
            message = f'Retour avec {loan_returned.jours_retard} jour(s) de retard. Pénalité : {loan_returned.penalite} FCFA.'
        else:
            message = 'Retour effectué à temps. Merci !'

        return Response({"message": message, "data": response_data, })

    @extend_schema(summary="Notifier avant échéance (J-3)",
                   description="Déclenche l'envoi d'emails de rappel aux utilisateurs dont la date de retour prévue est dans 3 jours. Destiné à être appelé par un scheduler (cron).")
    @action(detail=False, methods=['post'], url_path="notify-users-before-3-days-before-loan-due",)
    def notify_users_before_3_days_before_loan_due(self, request):

        loan_repo = LoanRepositoryImpl()
        brevo_email_service = BrevoEmailService()

        try:
            notify = NotifyUsers3DaysBeforeLoanDue(
                loan_repository=loan_repo, email_service=brevo_email_service)
            notify.execute()
            return Response({"message": "Success", })
        except:
            return Response({"message": "Error"}, status=500)

    @extend_schema(summary="Notifier les emprunts en retard",
                   description="Déclenche l'envoi d'emails de relance aux utilisateurs ayant dépassé leur date de retour prévue. Destiné à être appelé par un scheduler (cron).")
    @action(detail=False, methods=['post'], url_path='notify-users-on-loan-overdue', )
    def notify_users_on_loan_overdue(self, request):

        loan_repo = LoanRepositoryImpl()
        brevo_email_service = BrevoEmailService()

        try:
            notify = NotifyUsersOnLoanOverdue(
                loan_repository=loan_repo, email_service=brevo_email_service)
            notify.execute()
            return Response({"message": "Success", })
        except:
            return Response({"message": "Error"}, status=500)
