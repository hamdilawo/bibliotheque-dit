from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import Emprunt


class EmpruntListSerializer(serializers.ModelSerializer):
    """Serializer allege pour les listes."""
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
    """Serializer pour creer un emprunt."""
    utilisateur_id = serializers.IntegerField()
    livre_id = serializers.IntegerField()
    notes = serializers.CharField(required=False, allow_blank=True)


class RetourEmpruntSerializer(serializers.Serializer):
    """Serializer pour enregistrer un retour."""
    notes = serializers.CharField(required=False, allow_blank=True)


class EmpruntExportSerializer(serializers.ModelSerializer):
    """Serializer pour export CSV destine au pipeline DVC/ML."""
    class Meta:
        model = Emprunt
        fields = [
            'id', 'utilisateur_id', 'livre_id',
            'date_emprunt', 'date_retour_effective',
            'statut', 'jours_retard',
        ]


class ProlongationSerializer(serializers.Serializer):
    """Serializer pour une demande de prolongation d'emprunt."""
    jours_supplementaires = serializers.IntegerField(
        min_value=1,
        max_value=14,
        help_text='Nombre de jours supplementaires (1 a 14).'
    )
    raison = serializers.CharField(
        required=False,
        allow_blank=True,
        default='',
        help_text='Motif de la prolongation (optionnel).'
    )