from rest_framework import serializers
from .models import Livre, Categorie


class CategorieSerializer(serializers.ModelSerializer):
    nombre_livres = serializers.SerializerMethodField()

    class Meta:
        model = Categorie
        fields = ['id', 'nom', 'description', 'nombre_livres']

    def get_nombre_livres(self, obj):
        return obj.livres.filter(actif=True).count()


class LivreListSerializer(serializers.ModelSerializer):
    """Serializer allégé pour les listes."""
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    disponible = serializers.BooleanField(read_only=True)

    class Meta:
        model = Livre
        fields = [
            'id', 'titre', 'auteur', 'isbn', 'langue',
            'categorie_nom', 'quantite_disponible',
            'quantite_totale', 'disponible', 'couverture_url',
        ]


class LivreDetailSerializer(serializers.ModelSerializer):
    """Serializer complet pour détail / création / modification."""
    categorie_nom = serializers.CharField(source='categorie.nom', read_only=True)
    disponible = serializers.BooleanField(read_only=True)

    class Meta:
        model = Livre
        fields = [
            'id', 'titre', 'auteur', 'isbn', 'editeur',
            'annee_publication', 'langue', 'description',
            'nombre_pages', 'categorie', 'categorie_nom',
            'quantite_totale', 'quantite_disponible', 'disponible',
            'couverture_url', 'actif', 'date_ajout', 'date_modification',
        ]
        read_only_fields = ['date_ajout', 'date_modification']

    def validate_isbn(self, value):
        value = value.replace('-', '').replace(' ', '')
        if len(value) not in (10, 13):
            raise serializers.ValidationError("L'ISBN doit contenir 10 ou 13 chiffres.")
        return value

    def validate(self, data):
        quantite_totale = data.get('quantite_totale', 1)
        quantite_disponible = data.get('quantite_disponible', quantite_totale)
        if quantite_disponible > quantite_totale:
            raise serializers.ValidationError(
                "La quantité disponible ne peut pas dépasser la quantité totale."
            )
        return data


class DisponibiliteSerializer(serializers.Serializer):
    """Utilisé par le service Emprunts pour mettre à jour la dispo."""
    action = serializers.ChoiceField(choices=['reserver', 'retourner'])
