from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Utilisateur


class UtilisateurListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes."""
    nom_complet = serializers.CharField(read_only=True)
    peut_emprunter = serializers.BooleanField(read_only=True)

    class Meta:
        model = Utilisateur
        fields = [
            'id', 'nom_complet', 'email', 'numero_carte',
            'type_utilisateur', 'statut', 'emprunts_en_cours',
            'quota_emprunts', 'peut_emprunter',
        ]


class UtilisateurDetailSerializer(serializers.ModelSerializer):
    """Serializer complet pour profil / création / modification."""
    nom_complet = serializers.CharField(read_only=True)
    peut_emprunter = serializers.BooleanField(read_only=True)
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = Utilisateur
        fields = [
            'id', 'email', 'nom', 'prenom', 'nom_complet',
            'numero_carte', 'type_utilisateur', 'statut',
            'telephone', 'adresse', 'date_naissance',
            'quota_emprunts', 'emprunts_en_cours', 'peut_emprunter',
            'date_inscription', 'date_modification',
            'is_active', 'password',
        ]
        read_only_fields = ['date_inscription', 'date_modification', 'emprunts_en_cours']

    def validate_email(self, value):
        return value.lower()

    def validate_numero_carte(self, value):
        return value.upper()

    def create(self, validated_data):
        password = validated_data.pop('password', 'DIT@2026!')
        user = Utilisateur(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


class ProfilPublicSerializer(serializers.ModelSerializer):
    """Profil public minimal (pour d'autres services)."""
    nom_complet = serializers.CharField(read_only=True)

    class Meta:
        model = Utilisateur
        fields = [
            'id', 'nom_complet', 'numero_carte',
            'type_utilisateur', 'statut',
            'quota_emprunts', 'emprunts_en_cours', 'peut_emprunter',
        ]


class EmpruntSyncSerializer(serializers.Serializer):
    """
    Utilisé par le service Emprunts pour mettre à jour
    le compteur d'emprunts en cours.
    """
    action = serializers.ChoiceField(choices=['incrementer', 'decrementer'])


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT enrichi avec les infos utilisateur."""
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['nom_complet'] = user.nom_complet
        token['type_utilisateur'] = user.type_utilisateur
        token['numero_carte'] = user.numero_carte
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['utilisateur'] = ProfilPublicSerializer(self.user).data
        return data
