from rest_framework import viewsets, filters, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import User
from .serializers import (
    UserListSerializer,
    UserDetailSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserChangePasswordSerializer,
    UserDeactivateSerializer,
    LoginSerializer,
    
)

from rest_framework.mixins import (
    ListModelMixin,
    RetrieveModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
)
from rest_framework.viewsets import GenericViewSet


# Ce qui permet à Swagger de détecter automatiquement les champs 
# c'est GenericViewSet qui hérite de GenericAPIView, et 
# GenericAPIView expose get_serializer_class() 
# que Swagger lit automatiquement.
class UserViewSet(
                  ListModelMixin,
                  RetrieveModelMixin,
                  CreateModelMixin,
                  UpdateModelMixin,
                  GenericViewSet
):
    """
    Gestion complète des utilisateurs.

    Endpoints :
    - GET    /api/users/                   → Liste allégée
    - GET    /api/users/<id>/              → Détail complet
    - POST   /api/users/                   → Création
    - PATCH  /api/users/<id>/              → Mise à jour infos
    - PATCH  /api/users/<id>/password/     → Modification password
    - DELETE /api/users/<id>/deactivate/   → Soft delete
    """

    queryset = User.objects.all()

    # Filtres et tri
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields   = ['first_name', 'last_name', 'email', 'role']
    ordering_fields = ['first_name', 'last_name', 'date_joined', 'role']
    ordering        = ['first_name', 'last_name']  # tri par défaut

    

    # -------------------------------------------------------
    # Choix du serializer selon l'action
    # -------------------------------------------------------
    def get_serializer_class(self):
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'change_password':
            return UserChangePasswordSerializer
        elif self.action == 'deactivate':
            return UserDeactivateSerializer
        return UserDetailSerializer  # par défaut

    # -------------------------------------------------------
    # Permissions selon l'action
    # -------------------------------------------------------
    def get_permissions(self):
        if self.action == 'create':
            # inscription publique, sans authentification
            return [AllowAny()]
        elif self.action in ['deactivate']:
            # Soft delete réservé aux admins
            return [IsAuthenticated(), IsAdminUser()]
        elif self.action == 'list':
            # Liste réservée aux admins
            return [IsAuthenticated(), IsAdminUser()]
        else:
            # Reste → connecté uniquement
            return [IsAuthenticated()]

    # -------------------------------------------------------
    # GET /api/users/ → Liste allégée
    # -------------------------------------------------------
    @extend_schema(
        summary="Liste des utilisateurs",
        parameters=[
            OpenApiParameter('search', str, description='Recherche par nom, prénom, email ou rôle'),
            OpenApiParameter('role',   str, description='STUDENT | PROFESSOR | STAFF'),
            OpenApiParameter('ordering', str, description='first_name | last_name | date_joined'),
        ]
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # Filtre optionnel par rôle
        role = request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # -------------------------------------------------------
    # GET /api/users/<id>/ → Détail complet
    # -------------------------------------------------------
    @extend_schema(summary="Détail d'un utilisateur")
    def retrieve(self, request, *args, **kwargs):
        instance   = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # -------------------------------------------------------
    # POST /api/users/ → Création
    # -------------------------------------------------------
    @extend_schema(summary="Création d'un utilisateur")
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------
    # PATCH /api/users/<id>/ → Mise à jour partielle
    # -------------------------------------------------------
    @extend_schema(summary="Mise à jour d'un utilisateur")
    def partial_update(self, request, *args, **kwargs):
        instance   = self.get_object()

        # is_active réservé au superuser
        if 'is_active' in request.data and not request.user.is_superuser:
            return Response(
                {"is_active": "Seul un superuser peut modifier ce champ."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------
    # PATCH /api/users/<id>/password/ → Modification password
    # -------------------------------------------------------
    @extend_schema(summary="Modification du mot de passe")
    @action(detail=True, methods=['patch'], url_path='password')
    def change_password(self, request, pk=None):
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Mot de passe modifié avec succès."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------
    # DELETE /api/users/<id>/deactivate/ → Soft delete
    # -------------------------------------------------------
    @extend_schema(summary="Désactivation d'un utilisateur (soft delete)")
    @action(detail=True, methods=['delete'], url_path='deactivate')
    def deactivate(self, request, pk=None):
        user = self.get_object()

        #  Empêcher de se désactiver soi-même
        if user == request.user:
            return Response(
                {"error": "Vous ne pouvez pas vous désactiver vous-même."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(
            user,
            data={},
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": f"Utilisateur {user.email} désactivé avec succès."},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # -------------------------------------------------------
    # Désactiver PUT — on utilise uniquement PATCH
    # -------------------------------------------------------
    def update(self, request, *args, **kwargs):
        return Response(
            {"error": "Méthode PUT non autorisée. Utilisez PATCH."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )
    

# -------------------------------------------------------
# POST /api/auth/login/ → Connexion
# -------------------------------------------------------
class LoginView(APIView):
    """Vue de connexion — accessible sans authentification."""
    permission_classes = [AllowAny]  # pas besoin d'être connecté
    serializer_class = LoginSerializer  # Swagger détecte automatiquement

    @extend_schema(
            summary="Connexion d'un utilisateur",
            # Dans la view héritant de ModelViewSet(aussi GenericViewSet )  on pas  
            # besoin de spécifier request et body  
            #  Serializer détecté automatiquement via get_serializer_class() 
            # plus simplement , nous ajoutons 
            # 'serializer_class = LoginSerializer'
            # à LoginView(APIView)   pour ne plus ajouter request et response  
            # Swagger va détecter automatiquement   
    )
    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            user    = serializer.validated_data['user']
            access  = serializer.validated_data['access']
            refresh = serializer.validated_data['refresh']

            return Response({
                'access':    access,
                'refresh':   refresh,
                'id':        str(user.id),
                'email':     user.email,
                'full_name': user.full_name,  # @property
                'role':      user.role,
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)