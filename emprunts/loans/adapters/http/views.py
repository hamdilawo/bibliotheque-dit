
from loans.adapters.dal.repositories.loan_repository import LoanRepositoryImpl
from loans.app.handlers.borrow_a_book import BorrowABook, BorrowCommand
from loans.models import Emprunt
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter
import csv
import io
from loans.adapters.dal.repositories.book_repository import FakeBookRepositoryImpl
from .serializers import (
    EmpruntListSerializer, EmpruntDetailSerializer,
    CreerEmpruntSerializer, RetourEmpruntSerializer
)
from ...client import LivresClient, UtilisateursClient, ServiceException


class EmpruntViewSet(viewsets.ViewSet):
    """
    Gestion complète des emprunts.
    """
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['date_emprunt', 'date_retour_prevue', 'statut']
    ordering = ['-date_emprunt']
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_queryset(self):
        return Emprunt.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return EmpruntListSerializer
        if self.action == "emprunter":
            return CreerEmpruntSerializer()
        if self.action in ['retourner']:
            return RetourEmpruntSerializer
        return EmpruntDetailSerializer

    # ------------------------------------------------------------------ #
    # Endpoint 1 — Emprunter un livre
    # ------------------------------------------------------------------ #
    @extend_schema(request=CreerEmpruntSerializer)
    @action(detail=False, methods=['post'])
    def emprunter(self, request):
        """
        POST /api/emprunts/emprunter/
        Vérifie la disponibilité du livre et le quota de l'utilisateur,
        puis crée l'emprunt en communicant avec les deux autres services.
        """

        try:
            print("request.data", request)
            serializer = CreerEmpruntSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = serializer.validated_data

            utilisateur_id = "hello"
            livre_id: str = data['livre_id']
        except Exception as e:
            return Response(
                {'error': 'Données invalides. Veuillez vérifier les champs.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        command = BorrowCommand(
            book_id=livre_id,
            nb_copies=1,
            reader_id=utilisateur_id,
            reader_email=data.get('reader_email', ''),
            reader_name=data.get('reader_name', '')
        )

        loan_repository = LoanRepositoryImpl()
        # book_repository = BookRepositoryImpl(
        #     "http://service-livres:8000")  # URL du service Livres

        book_repository = FakeBookRepositoryImpl()

        borrow_a_book = BorrowABook(
            loan_repository=loan_repository, book_repository=book_repository)

        try:
            loan = borrow_a_book.execute(command)
        except ServiceException as e:
            return Response({'error': str(e)}, status=e.status_code or 400)

        return Response({'success': 'Emprunt créé avec succès.', 'loan_id': loan.id, 'book_id': loan.book.id}, status=status.HTTP_201_CREATED)

    # ------------------------------------------------------------------ #
    # Endpoint 2 — Retourner un livre
    # ------------------------------------------------------------------ #
    def get_object(self):
        try:
            return Emprunt.objects.get(pk=self.kwargs['pk'])
        except Emprunt.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound(detail="Emprunt introuvable.")

    @extend_schema(request=RetourEmpruntSerializer)
    @action(detail=True, methods=['post'])
    def retourner(self, request, pk=None):
        """
        POST /api/emprunts/{id}/retourner/
        Enregistre le retour, calcule les pénalités éventuelles,
        et met à jour les deux autres services.
        """
        emprunt = self.get_object()

        if emprunt.statut == 'RETOURNE':
            return Response(
                {'error': 'Ce livre a déjà été retourné.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = RetourEmpruntSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Calculer le retard
        today = timezone.now().date()
        jours_retard = 0
        penalite = 0
        if today > emprunt.date_retour_prevue:
            jours_retard = (today - emprunt.date_retour_prevue).days
            penalite = jours_retard * 200  # Mettre dans une CONST

        # Mettre à jour l'emprunt
        emprunt.date_retour_effective = today
        emprunt.statut = 'RETOURNE'
        emprunt.jours_retard = jours_retard
        emprunt.penalite_fcfa = penalite
        if serializer.validated_data.get('notes'):
            emprunt.notes = serializer.validated_data['notes']
        emprunt.save()

        # Libérer le livre (Service Livres)
        try:
            LivresClient.retourner_livre(emprunt.livre_id)
        except ServiceException as e:
            return Response({'warning': f'Retour enregistré mais erreur service livres: {e}'})

        # Décrémenter le compteur (Service Utilisateurs)
        try:
            UtilisateursClient.decrementer_emprunts(emprunt.utilisateur_id)
        except ServiceException:
            pass  # Non bloquant

        response_data = EmpruntDetailSerializer(emprunt).data
        if jours_retard > 0:
            response_data['message'] = f'Retour avec {jours_retard} jour(s) de retard. Pénalité : {penalite} FCFA.'
        else:
            response_data['message'] = 'Retour effectué à temps. Merci !'

        return Response(response_data)

    # ------------------------------------------------------------------ #
    # Endpoint 3 — Historique par utilisateur
    # ------------------------------------------------------------------ #
    @extend_schema(
        parameters=[OpenApiParameter(
            'utilisateur_id', int, description='ID de l\'utilisateur')]
    )
    @action(detail=False, methods=['get'])
    def historique(self, request):
        """
        GET /api/emprunts/historique/?utilisateur_id=3
        Historique complet des emprunts d'un utilisateur.
        """
        utilisateur_id = request.query_params.get('utilisateur_id')
        if not utilisateur_id:
            return Response(
                {'error': 'Paramètre utilisateur_id requis.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        emprunts = self.get_queryset().filter(utilisateur_id=utilisateur_id)
        statut = request.query_params.get('statut')
        if statut:
            emprunts = emprunts.filter(statut=statut.upper())
        emprunts = self.get_queryset().filter(utilisateur_id=utilisateur_id)
        statut = request.query_params.get('statut')
        if statut:
            emprunts = emprunts.filter(statut=statut.upper())

        serializer = EmpruntListSerializer(emprunts, many=True)
        return Response({'count': emprunts.count(), 'results': serializer.data})

    # ------------------------------------------------------------------ #
    # Endpoint 4 — Retards
    # ------------------------------------------------------------------ #
    @action(detail=False, methods=['get'])
    def retards(self, request):
        """
        GET /api/emprunts/retards/
        Liste des emprunts en retard avec mise à jour automatique des pénalités.
        """
        today = timezone.now().date()
        emprunts_retard = self.get_queryset().filter(
            statut__in=['EN_COURS', 'EN_RETARD'],
            date_retour_prevue__lt=today
        )

        # Mettre à jour les pénalités
        for emprunt in emprunts_retard:
            emprunt.calculer_retard()

        serializer = EmpruntListSerializer(emprunts_retard, many=True)
        return Response({
            'total_retards': emprunts_retard.count(),
            'penalites_totales_fcfa': sum(e.penalite_fcfa for e in emprunts_retard),
            'results': serializer.data,
        })

    # ------------------------------------------------------------------ #
    # Endpoint 5 — Export CSV pour le pipeline DVC/ML
    # ------------------------------------------------------------------ #
    @action(detail=False, methods=['get'])
    def export_csv(self, request):
        """
        GET /api/emprunts/export_csv/
        Exporte l'historique des emprunts en CSV pour le pipeline DVC.
        Colonnes : id, utilisateur_id, livre_id, date_emprunt,
                   date_retour_effective, statut, jours_retard
        """
        emprunts = self.get_queryset().filter(statut='RETOURNE')

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            'id', 'utilisateur_id', 'livre_id',
            'date_emprunt', 'date_retour_effective',
            'statut', 'jours_retard',
        ])
        for e in emprunts:
            writer.writerow([
                e.id, e.utilisateur_id, e.livre_id,
                e.date_emprunt.strftime('%Y-%m-%d'),
                e.date_retour_effective or '',
                e.statut, e.jours_retard,
            ])

        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="loans.csv"'
        return response

    # ------------------------------------------------------------------ #
    # Endpoint 6 — Statistiques globales
    # ------------------------------------------------------------------ #
    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """
        GET /api/emprunts/statistiques/
        """
        qs = self.get_queryset()
        today = timezone.now().date()

        return Response({
            'total_emprunts': qs.count(),
            'en_cours': qs.filter(statut='EN_COURS').count(),
            'en_retard': qs.filter(statut='EN_RETARD').count(),
            'retournes': qs.filter(statut='RETOURNE').count(),
            'penalites_totales_fcfa': float(
                sum(e.penalite_fcfa for e in qs.filter(jours_retard__gt=0))
            ),
        })
