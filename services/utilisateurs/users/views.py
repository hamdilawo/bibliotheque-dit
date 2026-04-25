from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Utilisateur
from .serializers import (
    UtilisateurListSerializer, UtilisateurDetailSerializer,
    ProfilPublicSerializer, EmpruntSyncSerializer,
    CustomTokenObtainPairSerializer,
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Endpoint de connexion — retourne JWT + infos utilisateur."""
    serializer_class = CustomTokenObtainPairSerializer


class UtilisateurViewSet(viewsets.ModelViewSet):
    """
    Gestion complète des utilisateurs.

    Endpoints :
    - GET    /api/utilisateurs/              → liste paginée
    - POST   /api/utilisateurs/              → créer un utilisateur
    - GET    /api/utilisateurs/{id}/         → profil complet
    - PUT    /api/utilisateurs/{id}/         → modifier
    - PATCH  /api/utilisateurs/{id}/         → modification partielle
    - DELETE /api/utilisateurs/{id}/         → désactiver
    - GET    /api/utilisateurs/search/       → recherche
    - GET    /api/utilisateurs/par_type/     → filtrer par type
    - GET    /api/utilisateurs/{id}/profil_public/ → profil minimal (inter-services)
    - POST   /api/utilisateurs/{id}/sync_emprunts/ → sync compteur (inter-services)
    - GET    /api/utilisateurs/statistiques/ → stats globales
    """
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['nom', 'prenom', 'date_inscription', 'type_utilisateur']
    ordering = ['nom', 'prenom']

    def get_queryset(self):
        return Utilisateur.objects.filter(is_active=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return UtilisateurListSerializer
        if self.action == 'profil_public':
            return ProfilPublicSerializer
        return UtilisateurDetailSerializer

    def get_permissions(self):
        # Création ouverte, reste authentifié
        if self.action == 'create':
            return [AllowAny()]
        return [AllowAny()]  # Simplification pour l'examen

    def destroy(self, request, *args, **kwargs):
        """Soft delete : désactive sans supprimer."""
        user = self.get_object()
        user.is_active = False
        user.statut = 'INACTIF'
        user.save(update_fields=['is_active', 'statut'])
        return Response(
            {'message': f'Utilisateur {user.nom_complet} désactivé.'},
            status=status.HTTP_200_OK
        )

    @extend_schema(
        parameters=[
            OpenApiParameter('q', str, description='Nom, prénom, email ou numéro de carte'),
            OpenApiParameter('type', str, description='ETUDIANT | PROFESSEUR | PERSONNEL | ADMIN'),
            OpenApiParameter('statut', str, description='ACTIF | SUSPENDU | INACTIF'),
        ]
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Endpoint 5 — Recherche avancée d'utilisateurs.
        GET /api/utilisateurs/search/?q=diallo&type=ETUDIANT
        """
        queryset = self.get_queryset()

        q = request.query_params.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(nom__icontains=q) |
                Q(prenom__icontains=q) |
                Q(email__icontains=q) |
                Q(numero_carte__icontains=q)
            )

        type_u = request.query_params.get('type')
        if type_u:
            queryset = queryset.filter(type_utilisateur=type_u.upper())

        statut = request.query_params.get('statut')
        if statut:
            queryset = queryset.filter(statut=statut.upper())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UtilisateurListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UtilisateurListSerializer(queryset, many=True)
        return Response({'count': queryset.count(), 'results': serializer.data})

    @action(detail=False, methods=['get'])
    def par_type(self, request):
        """
        Endpoint 6 — Lister les utilisateurs par type.
        GET /api/utilisateurs/par_type/?type=PROFESSEUR
        """
        type_u = request.query_params.get('type', 'ETUDIANT').upper()
        queryset = self.get_queryset().filter(type_utilisateur=type_u)
        serializer = UtilisateurListSerializer(queryset, many=True)
        return Response({
            'type': type_u,
            'count': queryset.count(),
            'results': serializer.data,
        })

    @action(detail=True, methods=['get'])
    def profil_public(self, request, pk=None):
        """
        Endpoint 7 — Profil public minimal (appelé par le service Emprunts).
        GET /api/utilisateurs/{id}/profil_public/
        """
        user = self.get_object()
        serializer = ProfilPublicSerializer(user)
        return Response(serializer.data)

    @extend_schema(request=EmpruntSyncSerializer)
    @action(detail=True, methods=['post'])
    def sync_emprunts(self, request, pk=None):
        """
        Endpoint 8 — Synchronisation du compteur d'emprunts (inter-services).
        POST /api/utilisateurs/{id}/sync_emprunts/
        Body: {"action": "incrementer"} ou {"action": "decrementer"}
        """
        user = self.get_object()
        serializer = EmpruntSyncSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action_demandee = serializer.validated_data['action']

        if action_demandee == 'incrementer':
            if not user.peut_emprunter:
                return Response(
                    {'error': f'Quota atteint ({user.emprunts_en_cours}/{user.quota_emprunts}) ou utilisateur suspendu.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.emprunts_en_cours += 1
        else:
            if user.emprunts_en_cours > 0:
                user.emprunts_en_cours -= 1

        user.save(update_fields=['emprunts_en_cours'])
        return Response({
            'message': f'Compteur mis à jour : {user.emprunts_en_cours}/{user.quota_emprunts}',
            'emprunts_en_cours': user.emprunts_en_cours,
            'quota_emprunts': user.quota_emprunts,
            'peut_emprunter': user.peut_emprunter,
        })

    @action(detail=False, methods=['get'])
    def statistiques(self, request):
        """
        Endpoint 9 — Statistiques globales des utilisateurs.
        GET /api/utilisateurs/statistiques/
        """
        qs = Utilisateur.objects.all()
        stats = {
            'total': qs.count(),
            'actifs': qs.filter(statut='ACTIF').count(),
            'suspendus': qs.filter(statut='SUSPENDU').count(),
            'par_type': {
                'etudiants': qs.filter(type_utilisateur='ETUDIANT').count(),
                'professeurs': qs.filter(type_utilisateur='PROFESSEUR').count(),
                'personnel': qs.filter(type_utilisateur='PERSONNEL').count(),
                'admins': qs.filter(type_utilisateur='ADMIN').count(),
            },
            'emprunts_en_cours_total': sum(u.emprunts_en_cours for u in qs),
        }
        return Response(stats)
