
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
    @extend_schema(request=CreerEmpruntSerializer, auth=["Token"])
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
            notes=data.get("notes", None)
        )

        loan_repository = LoanRepositoryImpl()
        # book_repository = BookRepositoryImpl(
        #     "http://service-livres:8000")  # URL du service Livres

        book_service = FakeBookService()

        borrow_a_book = BorrowABook(
            loan_repository=loan_repository, book_service=book_service)

        try:
            loan = borrow_a_book.execute(command)
        except ServiceException as e:
            return Response({'error': str(e)}, status=e.status_code or 400)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        response = BorrowABookResponseSerializer(loan).data
        return Response({'message': 'Emprunt créé avec succès.', "data": response}, status=status.HTTP_201_CREATED)

    @extend_schema(request=RetourEmpruntSerializer)
    @action(detail=False, methods=['post'])
    def retourner(self, request):

        loan_repo = LoanRepositoryImpl()

        try:
            serializer = RetourEmpruntSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return Response({'error': 'Données invalides. Veuillez vérifier les champs.', "error_details": e.detail}, status=status.HTTP_400_BAD_REQUEST)

        return_loan = ReturnLoan(
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
            response_data['message'] = f'Retour avec {loan_returned.jours_retard} jour(s) de retard. Pénalité : {loan_returned.penalite} FCFA.'
        else:
            response_data['message'] = 'Retour effectué à temps. Merci !'

        return Response(response_data)

    def rate_book():
        pass
