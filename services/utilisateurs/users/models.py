from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
import uuid


class UserManager(BaseUserManager):
    # password est obligatoire 
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        # Le password n'est jamais stocké en clair
        # Django le hashe automatiquement via set_password()
        user.set_password(password)
        user.save(using=self._db)
        return user
    # password est obligatoire
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    STUDENT = 'STUDENT'
    PROFESSOR = 'PROFESSOR'
    STAFF = 'STAFF'

    ROLE_CHOICES = (
        (STUDENT, 'Etudiant'),
        (PROFESSOR, 'Professeur'),
        (STAFF, 'Personnel'),
    )

    id = models.UUIDField(  
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="Identifiant unique"
    )
    email = models.EmailField(unique=True, verbose_name="Email")
    first_name = models.CharField(max_length=50, verbose_name="Prénom")
    last_name = models.CharField(max_length=50, verbose_name="Nom")
    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        verbose_name="Rôle",
        # à vérifier pour ces deux derniers champs
        # blank=True et default='' sur role
        # pour éviter une erreur à la création si role n'est pas fourni
        blank=True,
        default=''
    )
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    is_staff = models.BooleanField(default=False, verbose_name="Staff")
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    last_login = models.DateTimeField(null=True, blank=True, verbose_name="Dernière connexion")

    objects = UserManager()

    USERNAME_FIELD = 'email'        #  login avec email
    REQUIRED_FIELDS = ['first_name', 'last_name']  # champs obligatoires pour createsuperuser
    
    # Contient les métadonnées du modèle, c'est-à-dire des options qui ne sont pas des champs.
    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        # ordering Définit le tri par défaut des résultats de requêtes.
        # '-last_name':tri decroissant sur le champ last_name'
        ordering = ['first_name', 'last_name'] # tri alphabétique croissant 

        #Les index accélèrent les recherches en base de données sur les champs fréquemment utilisés dans les filtres et requêtes.
        #Sans index :Django parcourt TOUTE la table pour trouver l'email(lent)
        #Avec index :Django utilise l'index pour trouver directement(rapide)
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]



    def __str__(self):
        return f"{self.email} ({self.role})"
    
    # @property est un décorateur Python qui permet d'accéder à une méthode comme si c'était un attribut, sans parenthèses.
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"