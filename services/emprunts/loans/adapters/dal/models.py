from django.db import models
from django.utils import timezone
from datetime import timedelta

#


class Emprunt(models.Model):
    STATUT_CHOICES = [
        ('EN_COURS', 'En cours'),
        ('RETOURNE', 'Retourné'),
        ('APPROVE', 'Apprové'),
        ('REJETE', 'Rejeté'),
    ]

    # New
    id = models.UUIDField(primary_key=True)

    # Références inter-services (IDs sans FK)
    utilisateur_id = models.CharField(max_length=255, db_index=True)
    livre_id = models.CharField(max_length=255, db_index=True)

    # Dénormalisation pour éviter les appels répétés aux autres services
    utilisateur_nom = models.CharField(max_length=200, blank=True)
    utilisateur_carte = models.CharField(max_length=20, blank=True)
    livre_titre = models.CharField(max_length=255, blank=True)
    livre_isbn = models.CharField(max_length=13, blank=True)
    # NEW FIELDS
    livre_id = models.CharField(max_length=13, blank=True)
    # END: NEW FIELDS
    livre_auteur = models.CharField(max_length=255, blank=True)

    # Dates
    date_emprunt = models.DateTimeField(auto_now_add=True)
    date_retour_prevue = models.DateField()
    date_retour_effective = models.DateField(null=True, blank=True)

    # Statut
    statut = models.CharField(
        max_length=20, choices=STATUT_CHOICES, default='EN_COURS')

    # Pénalités
    jours_retard = models.PositiveIntegerField(default=0)
    penalite_fcfa = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)

    # Notes
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_emprunt']
        indexes = [
            models.Index(fields=['utilisateur_id', 'statut']),
            models.Index(fields=['livre_id', 'statut']),
            models.Index(fields=['date_retour_prevue']),
        ]

    def __str__(self):
        return f"Emprunt #{self.pk} — {self.livre_titre} par {self.utilisateur_nom}"

    @classmethod
    def get_duree_par_defaut(cls, type_utilisateur='ETUDIANT'):
        """Durée d'emprunt selon le type d'utilisateur (en jours)."""
        durees = {
            'ETUDIANT': 14,
            'PROFESSEUR': 30,
            'PERSONNEL': 21,
            'ADMIN': 30,
        }
        return durees.get(type_utilisateur, 14)

    def calculer_retard(self):
        """Calcule les jours de retard et la pénalité (200 FCFA/jour)."""
        if self.statut == 'EN_COURS':
            today = timezone.now().date()
            if today > self.date_retour_prevue:
                self.jours_retard = (today - self.date_retour_prevue).days
                self.penalite_fcfa = self.jours_retard * 200
                self.statut = 'EN_RETARD'
                self.save(update_fields=[
                          'jours_retard', 'penalite_fcfa', 'statut'])
        return self.jours_retard

    @property
    def est_en_retard(self):
        if self.statut == 'RETOURNE':
            return False
        return timezone.now().date() > self.date_retour_prevue

    @property
    def jours_restants(self):
        if self.statut == 'RETOURNE':
            return 0
        delta = self.date_retour_prevue - timezone.now().date()
        return delta.days
