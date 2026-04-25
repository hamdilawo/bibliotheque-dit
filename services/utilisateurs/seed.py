"""
Script de peuplement initial — Service Utilisateurs.
Lancer avec : python seed.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'utilisateurs_service.settings')
django.setup()

from users.models import Utilisateur

utilisateurs_data = [
    # Admin
    {
        'email': 'admin@dit.sn',
        'nom': 'Administrateur',
        'prenom': 'DIT',
        'numero_carte': 'ADMIN001',
        'type_utilisateur': 'ADMIN',
        'password': 'DIT@Admin2026!',
        'is_staff': True,
        'is_superuser': True,
        'telephone': '+221 33 000 00 00',
    },
    # Professeurs
    {
        'email': 'amadou.diallo@dit.sn',
        'nom': 'Diallo',
        'prenom': 'Amadou',
        'numero_carte': 'PROF001',
        'type_utilisateur': 'PROFESSEUR',
        'password': 'Prof@2026!',
        'telephone': '+221 77 100 00 01',
    },
    {
        'email': 'fatou.ndiaye@dit.sn',
        'nom': 'Ndiaye',
        'prenom': 'Fatou',
        'numero_carte': 'PROF002',
        'type_utilisateur': 'PROFESSEUR',
        'password': 'Prof@2026!',
        'telephone': '+221 77 100 00 02',
    },
    # Étudiants
    {
        'email': 'moussa.ba@etu.dit.sn',
        'nom': 'Ba',
        'prenom': 'Moussa',
        'numero_carte': 'ETU2026001',
        'type_utilisateur': 'ETUDIANT',
        'password': 'Etu@2026!',
        'telephone': '+221 77 200 00 01',
    },
    {
        'email': 'aissatou.fall@etu.dit.sn',
        'nom': 'Fall',
        'prenom': 'Aissatou',
        'numero_carte': 'ETU2026002',
        'type_utilisateur': 'ETUDIANT',
        'password': 'Etu@2026!',
        'telephone': '+221 77 200 00 02',
    },
    {
        'email': 'ibrahima.sow@etu.dit.sn',
        'nom': 'Sow',
        'prenom': 'Ibrahima',
        'numero_carte': 'ETU2026003',
        'type_utilisateur': 'ETUDIANT',
        'password': 'Etu@2026!',
    },
    {
        'email': 'mariama.kane@etu.dit.sn',
        'nom': 'Kane',
        'prenom': 'Mariama',
        'numero_carte': 'ETU2026004',
        'type_utilisateur': 'ETUDIANT',
        'password': 'Etu@2026!',
    },
    # Personnel
    {
        'email': 'bibliothecaire@dit.sn',
        'nom': 'Sarr',
        'prenom': 'Ousmane',
        'numero_carte': 'PERS001',
        'type_utilisateur': 'PERSONNEL',
        'password': 'Pers@2026!',
        'telephone': '+221 77 300 00 01',
    },
]

print("Création des utilisateurs...")
for data in utilisateurs_data:
    email = data.pop('email')
    password = data.pop('password')
    is_staff = data.pop('is_staff', False)
    is_superuser = data.pop('is_superuser', False)

    if not Utilisateur.objects.filter(email=email).exists():
        user = Utilisateur.objects.create_user(
            email=email,
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser,
            **data
        )
        print(f"  ✓ {user.nom_complet} ({user.type_utilisateur}) — quota: {user.quota_emprunts}")
    else:
        print(f"  ~ {email} existe déjà")

print(f"\nBase initialisée : {Utilisateur.objects.count()} utilisateurs")
