from loans.adapters.dal.models import Emprunt
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta


class EmpruntListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes."""
    est_en_retard = serializers.BooleanField(read_only=True)
    jours_restants = serializers.IntegerField(read_only=True)

    class Meta:
        model = Emprunt
        fields = [
            'id', 'utilisateur_id', 'utilisateur_nom', 'utilisateur_carte',
            'livre_id', 'livre_titre', 'livre_auteur', 'livre_isbn',
            'date_emprunt', 'date_retour_prevue', 'date_retour_effective',
            'statut', 'est_en_retard', 'jours_restants',
            'jours_retard', 'penalite_fcfa',
        ]


class EmpruntDetailSerializer(serializers.ModelSerializer):
    """Serializer complet."""
    est_en_retard = serializers.BooleanField(read_only=True)
    jours_restants = serializers.IntegerField(read_only=True)

    class Meta:
        model = Emprunt
        fields = '__all__'
        read_only_fields = [
            'date_emprunt', 'statut', 'jours_retard', 'penalite_fcfa',
            'utilisateur_nom', 'utilisateur_carte',
            'livre_titre', 'livre_isbn', 'livre_auteur',
        ]


class CreerEmpruntSerializer(serializers.Serializer):
    """Serializer pour créer un emprunt."""
    user_id = serializers.CharField()
    livre_id = serializers.CharField()
    notes = serializers.CharField(required=False, allow_blank=True)


class RetourEmpruntSerializer(serializers.Serializer):
    """Serializer pour enregistrer un retour."""
    notes = serializers.CharField(required=False, allow_blank=True)


class EmpruntExportSerializer(serializers.ModelSerializer):
    """Serializer pour export CSV destiné au pipeline DVC/ML."""
    class Meta:
        model = Emprunt
        fields = [
            'id', 'utilisateur_id', 'livre_id',
            'date_emprunt', 'date_retour_effective',
            'statut', 'jours_retard',
        ]
