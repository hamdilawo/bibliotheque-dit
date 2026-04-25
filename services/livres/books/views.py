from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Livre, Categorie
from .serializers import (
    LivreListSerializer, LivreDetailSerializer,
    CategorieSerializer, DisponibiliteSerializer,
)


class CategorieViewSet(viewsets.ModelViewSet):
    """
    CRUD complet des catégories de livres.
    """
    queryset = Categorie.objects.all()
    serializer_class = CategorieSerializer


class LivreViewSet(viewsets.ModelViewSet):
    """
    Gestion complète des livres.

    Endpoints disponibles :
    - GET    /api/livres/              → liste paginée
    - POST   /api/livres/              → créer un livre
    - GET    /api/livres/{id}/         → détail d'un livre
    - PUT    /api/livres/{id}/         → modifier un livre
    - PATCH  /api/livres/{id}/         → modification partielle
    - DELETE /api/livres/{id}/         → supprimer (désactiver)
    - GET    /api/livres/search/       → recherche avancée
    - GET    /api/livres/disponibles/  → livres disponibles uniquement
    - POST   /api/livres/{id}/disponibilite/ → mise à jour dispo (inter-services)
    """
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['titre', 'auteur', 'date_ajout', 'annee_publication']
    ordering = ['titre']

    def get_queryset(self):
        return Livre.objects.select_related('categorie').filter(actif=True)

    def get_serializer_class(self):
        if self.action == 'list':
            return LivreListSerializer
        return LivreDetailSerializer

    def destroy(self, request, *args, **kwargs):
        """Soft delete : désactive le livre sans le supprimer."""
        livre = self.get_object()
        livre.actif = False
        livre.save(update_fields=['actif'])
        return Response(
            {'message': f'Livre "{livre.titre}" désactivé avec succès.'},
            status=status.HTTP_200_OK
        )

    @extend_schema(
        parameters=[
            OpenApiParameter('q', str, description='Terme de recherche (titre, auteur, ISBN)'),
            OpenApiParameter('categorie', int, description='ID de la catégorie'),
            OpenApiParameter('langue', str, description='Code langue (fr, en, ar, es)'),
            OpenApiParameter('disponible', bool, description='Filtrer par disponibilité'),
        ]
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Endpoint 5 — Recherche avancée multi-critères.
        GET /api/livres/search/?q=python&categorie=2&langue=fr&disponible=true
        """
        queryset = self.get_queryset()

        # Recherche textuelle
        q = request.query_params.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                Q(titre__icontains=q) |
                Q(auteur__icontains=q) |
                Q(isbn__icontains=q) |
                Q(description__icontains=q) |
                Q(editeur__icontains=q)
            )

        # Filtre catégorie
        categorie_id = request.query_params.get('categorie')
        if categorie_id:
            queryset = queryset.filter(categorie_id=categorie_id)

        # Filtre langue
        langue = request.query_params.get('langue')
        if langue:
            queryset = queryset.filter(langue=langue)

        # Filtre disponibilité
        disponible = request.query_params.get('disponible')
        if disponible and disponible.lower() == 'true':
            queryset = queryset.filter(quantite_disponible__gt=0)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = LivreListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = LivreListSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data,
        })

    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        """
        Endpoint 6 — Liste des livres disponibles à l'emprunt.
        GET /api/livres/disponibles/
        """
        queryset = self.get_queryset().filter(quantite_disponible__gt=0)
        serializer = LivreListSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data,
        })

    @extend_schema(request=DisponibiliteSerializer)
    @action(detail=True, methods=['post'])
    def disponibilite(self, request, pk=None):
        """
        Endpoint 7 — Mise à jour de la disponibilité (appelé par le service Emprunts).
        POST /api/livres/{id}/disponibilite/
        Body: {"action": "reserver"} ou {"action": "retourner"}
        """
        livre = self.get_object()
        serializer = DisponibiliteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action_demandee = serializer.validated_data['action']
        try:
            if action_demandee == 'reserver':
                livre.reserver()
                message = f'Réservation effectuée. Disponible : {livre.quantite_disponible}/{livre.quantite_totale}'
            else:
                livre.retourner()
                message = f'Retour enregistré. Disponible : {livre.quantite_disponible}/{livre.quantite_totale}'
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'message': message,
            'quantite_disponible': livre.quantite_disponible,
            'quantite_totale': livre.quantite_totale,
        })
