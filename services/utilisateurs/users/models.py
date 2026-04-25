from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UtilisateurManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('type_utilisateur', 'ADMIN')
        return self.create_user(email, password, **extra_fields)


class Utilisateur(AbstractBaseUser, PermissionsMixin):
    TYPE_CHOICES = [
        ('ETUDIANT', 'Étudiant'),
        ('PROFESSEUR', 'Professeur'),
        ('PERSONNEL', 'Personnel'),
        ('ADMIN', 'Administrateur'),
    ]

    STATUT_CHOICES = [
        ('ACTIF', 'Actif'),
        ('SUSPENDU', 'Suspendu'),
        ('INACTIF', 'Inactif'),
    ]

    # Identité
    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    numero_carte = models.CharField(max_length=20, unique=True, help_text='Numéro de carte étudiant/employé')

    # Type et statut
    type_utilisateur = models.CharField(max_length=20, choices=TYPE_CHOICES, default='ETUDIANT')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='ACTIF')

    # Informations complémentaires
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)
    date_naissance = models.DateField(null=True, blank=True)
    photo = models.ImageField(upload_to='photos/', null=True, blank=True)

    # Quota d'emprunts selon le type
    quota_emprunts = models.PositiveIntegerField(default=3, help_text='Nombre max de livres simultanés')
    emprunts_en_cours = models.PositiveIntegerField(default=0)

    # Dates
    date_inscription = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    derniere_connexion_api = models.DateTimeField(null=True, blank=True)

    # Django auth
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UtilisateurManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom', 'numero_carte']

    class Meta:
        ordering = ['nom', 'prenom']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['numero_carte']),
            models.Index(fields=['type_utilisateur']),
        ]

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.type_utilisateur})"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    @property
    def peut_emprunter(self):
        return (
            self.statut == 'ACTIF' and
            self.emprunts_en_cours < self.quota_emprunts
        )

    def get_quota_par_defaut(self):
        """Retourne le quota selon le type d'utilisateur."""
        quotas = {
            'ETUDIANT': 3,
            'PROFESSEUR': 10,
            'PERSONNEL': 5,
            'ADMIN': 20,
        }
        return quotas.get(self.type_utilisateur, 3)

    def save(self, *args, **kwargs):
        # Auto-assigne le quota par défaut si non modifié
        if not self.pk:
            self.quota_emprunts = self.get_quota_par_defaut()
        super().save(*args, **kwargs)
