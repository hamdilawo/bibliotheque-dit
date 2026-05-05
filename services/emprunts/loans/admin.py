from django.contrib import admin
from django.utils.html import format_html
from .models import Emprunt


@admin.register(Emprunt)
class EmpruntAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'utilisateur_nom', 'livre_titre',
        'date_emprunt', 'date_retour_prevue', 'statut_badge',
        'jours_retard', 'penalite_fcfa',
    ]
    list_filter = ['statut', 'date_emprunt']
    search_fields = ['utilisateur_nom', 'utilisateur_carte', 'livre_titre', 'livre_isbn']
    readonly_fields = ['date_emprunt', 'jours_retard', 'penalite_fcfa']
    ordering = ['-date_emprunt']

    def statut_badge(self, obj):
        colors = {
            'EN_COURS':  '#2ecc71',
            'RETOURNE':  '#3498db',
            'EN_RETARD': '#e74c3c',
            'PERDU':     '#95a5a6',
        }
        color = colors.get(obj.statut, '#999')
        return format_html(
            '<span style="background:{};color:white;padding:3px 8px;border-radius:4px;font-size:11px">{}</span>',
            color, obj.get_statut_display()
        )
    statut_badge.short_description = 'Statut'