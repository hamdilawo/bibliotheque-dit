# Le serializer est un traducteur entre les données Python/Django et le format JSON de l'API, dans les deux sens.

from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Elle personnalise le token JWT pour y ajouter des informations supplémentaires 
    sur l'utilisateur, au-delà du contenu par défaut.
    """

    @classmethod
    def get_token(cls, user):
        # Récupère le token JWT standard
        token = super().get_token(user)

        # Ajout des infos de ton modèle User
        # Ajoute des infos personnalisées dans le token
        # convertir tous les types non sérialisables en str
        # super().get_token() ajoute automatiquement user_id
        # mais comme c'est un UUID il faut le forcer en str
        # user_id déjà ajouté automatiquement par simplejwt → supprimer
        # donc commentons la ligne
        # token['user_id']      = str(user.id) TODO: POurquoir commenter
        token['email'] = user.email
        token['full_name'] = str(user.full_name)   # @property
        token['role'] = user.role
        token['is_active'] = user.is_active

        return token

    def validate(self, attrs):
        #  Appelle la validation standard (email + password)
        # retourne access token + refresh token
        data = super().validate(attrs)

        # Tu peux aussi ajouter des infos dans la réponse API
        # sans les mettre dans le token
        # str() obligatoire pour UUID, UUID non sérialisable
        data['id'] = str(self.user.id)
        data['email'] = self.user.email
        data['full_name'] = self.user.full_name
        data['role'] = self.user.role

        return data


# Serializer allégé pour les listes GET /api/users/
class UserListSerializer(serializers.ModelSerializer):
    """
     Serializer allégé pour les listes:
     Retourne uniquement les infos essentielles
    """
    # read_only=True car c'est une valeur calculée, on ne peut pas la modifier directement.
    # lit/expose le @property du modèle
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        # champs à exposer dans la réponse
        fields = [

            'id',
            'full_name',   # @property → "Jean Fabrice"
            'email',
            'role',
        ]

# Serializer complet pour le détail GET /api/users/<id>/


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer complet pour le détail d'un utilisateur."""
    full_name = serializers.CharField(read_only=True)  # @property du modèle

    class Meta:
        model = User
        fields = [
            # Ne jamais exposer password dans une réponse API, même hashé.
            'id',
            'full_name',
            'first_name',
            'last_name',
            'email',
            'role',
            'is_active',
            'is_staff',
            'date_joined',
            'last_login',
        ]

        read_only_fields = [
            'id',           # UUID généré automatiquement
            'date_joined',  # généré automatiquement à la création
            'last_login',   # géré par Django automatiquement
        ]


# Serializer pour la création POST /api/users/
class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer pour la création d'un utilisateur."""
    password = serializers.CharField(
        write_only=True,               # jamais retourné dans la réponse
        required=True,                 # obligatoire
        min_length=8,                  # minimum 8 caractères
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'password',
            'first_name',
            'last_name',
            'role',
        ]
        # extra_kwargs permet d'ajouter ou modifier des options sur les champs directement dans class Meta, sans avoir à les redéclarer un par un en dehors.
        extra_kwargs = {
            'email':      {'required': True},
            'first_name': {'required': True},
            'last_name':  {'required': True},
            'role':       {'required': True},
        }

    def validate_email(self, value):
        """Vérifie que l'email n'est pas déjà utilisé."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value

    def validate_password(self, value):
        """Vérifie que le mot de passe n'est pas que des chiffres."""
        if value.isdigit():
            raise serializers.ValidationError(
                "Le mot de passe ne peut pas contenir uniquement des chiffres."
            )
        return value

    def create(self, validated_data):
        """Crée un utilisateur avec le mot de passe hashé."""
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # hashage du mot de passe
        user.save()
        return user

# Serializer pour la mise à jour PATCH /api/users/<id>/


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour d'un utilisateur."""

    class Meta:
        model = User
        fields = [
            'email',
            'first_name',
            'last_name',
            'role',
        ]
        read_only_fields = []  # aucun champ read_only ici, tout est modifiable
        extra_kwargs = {
            'email':      {'required': False},  # PATCH → champs optionnels
            'first_name': {'required': False},
            'last_name':  {'required': False},
            'role':       {'required': False},

        }

    def validate_email(self, value):
        """Vérifie que le nouvel email n'est pas déjà utilisé."""
        # instance = l'utilisateur en cours de modification
        if User.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value.lower().strip()  # normalise l'email

    def validate_role(self, value):
        """Vérifie que le rôle est valide."""
        roles_valides = [User.STUDENT, User.PROFESSOR, User.STAFF]
        if value not in roles_valides:
            raise serializers.ValidationError(
                f"Rôle invalide. Choisir parmi : {', '.join(roles_valides)}"
            )
        return value

    def validate_first_name(self, value):
        """Vérifie que le prénom n'est pas vide."""
        if value and len(value.strip()) == 0:
            raise serializers.ValidationError(
                "Le prénom ne peut pas être vide.")
        return value.strip()  # supprime les espaces inutiles

    def validate_last_name(self, value):
        """Vérifie que le nom n'est pas vide."""
        if value and len(value.strip()) == 0:
            raise serializers.ValidationError("Le nom ne peut pas être vide.")
        return value.strip()  # supprime les espaces inutiles

    def validate(self, data):
        """Validation globale — vérifie qu'au moins un champ est fourni."""
        if not data:
            raise serializers.ValidationError(
                "Au moins un champ doit être fourni pour la mise à jour."
            )
        return data

    def update(self, instance, validated_data):
        """Met à jour uniquement les champs fournis."""
        instance.first_name = validated_data.get(
            'first_name', instance.first_name)
        instance.last_name = validated_data.get(
            'last_name', instance.last_name)
        instance.role = validated_data.get('role', instance.role)
        instance.save()
        return instance

# Serializer pour la modification du mot de passe PATCH /api/users/change-password/


class UserChangePasswordSerializer(serializers.Serializer):
    """Serializer pour la modification du mot de passe."""

    #  On n'utilise pas ModelSerializer ici
    # car password n'est pas un champ direct du modèle

    old_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    def validate_old_password(self, value):
        """Vérifie que l'ancien mot de passe est correct."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Ancien mot de passe incorrect.")
        return value

    def validate_new_password(self, value):
        """Vérifie la complexité du nouveau mot de passe."""
        if value.isdigit():
            raise serializers.ValidationError(
                "Le mot de passe ne peut pas contenir uniquement des chiffres."
            )
        return value

    def validate(self, data):
        """Vérifie que les deux nouveaux mots de passe correspondent."""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {"confirm_password": "Les mots de passe ne correspondent pas."}
            )
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError(
                {"new_password": "Le nouveau mot de passe doit être différent de l'ancien."}
            )
        return data

    def save(self):
        """Applique le nouveau mot de passe."""
        user = self.context['request'].user
        # hashage automatique
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserDeactivateSerializer(serializers.ModelSerializer):
    """Serializer pour la désactivation d'un utilisateur (soft delete)."""

    class Meta:
        model = User
        fields = ['id', 'email', 'is_active']
        read_only_fields = ['id', 'email']  # non modifiables

    def validate(self, data):
        """Vérifie que l'utilisateur n'est pas déjà désactivé."""
        if not self.instance.is_active:
            raise serializers.ValidationError(
                {"is_active": "Cet utilisateur est déjà désactivé."}
            )
        return data

    def update(self, instance, validated_data):
        """Désactive l'utilisateur."""
        instance.is_active = False
        instance.save()
        return instance
