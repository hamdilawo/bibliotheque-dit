from django.db import models


class Categorie(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Catégorie'
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Livre(models.Model):
    LANGUE_CHOICES = [
        ('fr', 'Français'),
        ('en', 'Anglais'),
        ('ar', 'Arabe'),
        ('es', 'Espagnol'),
    ]

    titre = models.CharField(max_length=255)
    auteur = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, unique=True)
    editeur = models.CharField(max_length=255, blank=True)
    annee_publication = models.PositiveIntegerField(null=True, blank=True)
    langue = models.CharField(max_length=2, choices=LANGUE_CHOICES, default='fr')
    description = models.TextField(blank=True)
    nombre_pages = models.PositiveIntegerField(null=True, blank=True)
    categorie = models.ForeignKey(
        Categorie, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='livres'
    )
    quantite_totale = models.PositiveIntegerField(default=1)
    quantite_disponible = models.PositiveIntegerField(default=1)
    date_ajout = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    couverture_url = models.URLField(blank=True)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ['titre']
        indexes = [
            models.Index(fields=['isbn']),
            models.Index(fields=['auteur']),
            models.Index(fields=['titre']),
        ]

    def __str__(self):
        return f"{self.titre} — {self.auteur}"

    @property
    def disponible(self):
        return self.quantite_disponible > 0

    def reserver(self):
        """Décrémente la quantité disponible lors d'un emprunt."""
        if self.quantite_disponible <= 0:
            raise ValueError("Aucun exemplaire disponible.")
        self.quantite_disponible -= 1
        self.save(update_fields=['quantite_disponible'])

    def retourner(self):
        """Incrémente la quantité disponible lors d'un retour."""
        if self.quantite_disponible >= self.quantite_totale:
            raise ValueError("Tous les exemplaires sont déjà disponibles.")
        self.quantite_disponible += 1
        self.save(update_fields=['quantite_disponible'])
