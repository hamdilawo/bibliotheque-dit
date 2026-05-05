from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.http import HttpResponse
from drf_spectacular.utils import extend_schema, OpenApiParameter
import csv
import io

from .models import Emprunt
from .serializers import (
    EmpruntListSerializer, EmpruntDetailSerializer,
    CreerEmpruntSerializer, RetourEmpruntSerializer,
    EmpruntExportSerializer, ProlongationSerializer,
)
from .client import LivresClient, UtilisateursClient, ServiceException


class EmpruntViewSet(viewsets.ModelViewSet):
    """
    Gestion complète des emprunts.

    Endpoints :
    - POST   /api/emprunts/emprunter/          → emprunter un livre
    - POST   /api/emprunts/{id}/retourner/     → retourner un livre
    - GET    /api/emprunts/                    → liste de tous les emprunts
    - GET    /api/emprunts/{id}/               → détail d'un emprunt
    - GET    /api/emprunts/historique/         → historique par utilisateur
    - GET    /api/emprunts/retards/            → liste des retards
    - GET    /api/emprunts/export_csv/         → export pour le ML (DVC)
    - GET    /api/emprunts/statistiques/       → stats globales
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
        serializer = CreerEmpruntSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        utilisateur_id = data['utilisateur_id']
        livre_id = data['livre_id']

        # 1. Vérifier l'utilisateur
        try:
            utilisateur = UtilisateursClient.get_utilisateur(utilisateur_id)
        except ServiceException as e:
            return Response({'error': str(e)}, status=e.status_code or 400)

        if not utilisateur.get('peut_emprunter'):
            return Response(
                {'error': 'Utilisateur suspendu ou quota d\'emprunts atteint.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. Vérifier le livre
        try:
            livre = LivresClient.get_livre(livre_id)
        except ServiceException as e:
            return Response({'error': str(e)}, status=e.status_code or 400)

        if not livre.get('disponible'):
            return Response(
                {'error': f'Le livre "{livre["titre"]}" n\'est pas disponible.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 3. Vérifier qu'il n'a pas déjà ce livre en cours
        emprunt_existant = Emprunt.objects.filter(
            utilisateur_id=utilisateur_id,
            livre_id=livre_id,
            statut__in=['EN_COURS', 'EN_RETARD']
        ).first()
        if emprunt_existant:
            return Response(
                {'error': 'Cet utilisateur a déjà emprunté ce livre.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 4. Réserver le livre (Service Livres)
        try:
            LivresClient.reserver_livre(livre_id)
        except ServiceException as e:
            return Response({'error': str(e)}, status=e.status_code or 400)

        # 5. Incrémenter le compteur (Service Utilisateurs)
        try:
            UtilisateursClient.incrementer_emprunts(utilisateur_id)
        except ServiceException as e:
            # Rollback : remettre le livre disponible
            LivresClient.retourner_livre(livre_id)
            return Response({'error': str(e)}, status=e.status_code or 400)

        # 6. Calculer la date de retour prévue
        type_u = utilisateur.get('type_utilisateur', 'ETUDIANT')
        duree = Emprunt.get_duree_par_defaut(type_u)
        date_retour = timezone.now().date() + __import__('datetime').timedelta(days=duree)

        # 7. Créer l'emprunt
        emprunt = Emprunt.objects.create(
            utilisateur_id=utilisateur_id,
            livre_id=livre_id,
            utilisateur_nom=f"{utilisateur.get('nom_complet', '')}",
            utilisateur_carte=utilisateur.get('numero_carte', ''),
            livre_titre=livre.get('titre', ''),
            livre_isbn=livre.get('isbn', ''),
            livre_auteur=livre.get('auteur', ''),
            date_retour_prevue=date_retour,
            notes=data.get('notes', ''),
        )

        return Response(
            EmpruntDetailSerializer(emprunt).data,
            status=status.HTTP_201_CREATED
        )

    # ------------------------------------------------------------------ #
    # Endpoint 2 — Retourner un livre
    # ------------------------------------------------------------------ #
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
            penalite = jours_retard * 200  # 200 FCFA/jour

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
        parameters=[OpenApiParameter('utilisateur_id', int, description='ID de l\'utilisateur')]
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

        page = self.paginate_queryset(emprunts)
        if page is not None:
            serializer = EmpruntListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

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

# ------------------------------------------------------------------ #
    # Endpoint 7 — Prolongation d'un emprunt
    # ------------------------------------------------------------------ #
    @extend_schema(request=ProlongationSerializer)
    @action(detail=True, methods=['post'])
    def prolonger(self, request, pk=None):
        """
        POST /api/emprunts/{id}/prolonger/
        Prolonge la date de retour prévue (maximum 2 prolongations, 14 jours max chacune).
        """
        import re
        import datetime

        emprunt = self.get_object()

        if emprunt.statut == 'RETOURNE':
            return Response(
                {'error': 'Impossible de prolonger un emprunt déjà retourné.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if emprunt.statut == 'PERDU':
            return Response(
                {'error': 'Impossible de prolonger un emprunt marqué comme perdu.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        nb_prolongations = int(emprunt.notes.split('__prolongations:')[1].split('__')[0]) \
            if '__prolongations:' in emprunt.notes else 0

        if nb_prolongations >= 2:
            return Response(
                {'error': 'Nombre maximum de prolongations (2) atteint pour cet emprunt.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ProlongationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        jours = serializer.validated_data['jours_supplementaires']
        ancienne_date = emprunt.date_retour_prevue
        emprunt.date_retour_prevue = ancienne_date + datetime.timedelta(days=jours)

        if emprunt.statut == 'EN_RETARD':
            emprunt.statut = 'EN_COURS'
            emprunt.jours_retard = 0
            emprunt.penalite_fcfa = 0

        nb_prolongations += 1
        tag = f'__prolongations:{nb_prolongations}__'
        if '__prolongations:' in emprunt.notes:
            emprunt.notes = re.sub(r'__prolongations:\d+__', tag, emprunt.notes)
        else:
            emprunt.notes = (emprunt.notes + ' ' + tag).strip()

        emprunt.save()

        return Response({
            **EmpruntDetailSerializer(emprunt).data,
            'message': (
                f'Prolongation accordée : {jours} jour(s) supplémentaire(s). '
                f'Nouvelle date de retour : {emprunt.date_retour_prevue}. '
                f'({nb_prolongations}/2 prolongations utilisées)'
            ),
        })

    # ------------------------------------------------------------------ #
    # Endpoint 8 — Mise à jour du statut (usage administrateur)
    # ------------------------------------------------------------------ #
    @action(detail=True, methods=['patch'])
    def statut(self, request, pk=None):
        """
        PATCH /api/emprunts/{id}/statut/
        Permet de forcer un statut (ex : PERDU). Réservé à l'administration.
        """
        emprunt = self.get_object()
        nouveau_statut = request.data.get('statut')
        statuts_valides = [s[0] for s in Emprunt.STATUT_CHOICES]

        if nouveau_statut not in statuts_valides:
            return Response(
                {'error': f'Statut invalide. Valeurs possibles : {statuts_valides}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ancien_statut = emprunt.statut
        emprunt.statut = nouveau_statut

        if nouveau_statut == 'PERDU' and ancien_statut != 'RETOURNE':
            try:
                LivresClient.retourner_livre(emprunt.livre_id)
            except ServiceException:
                pass

        emprunt.save()
        return Response(EmpruntDetailSerializer(emprunt).data)
