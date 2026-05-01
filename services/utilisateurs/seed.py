"""
Script de peuplement initial - Service Utilisateurs.
Lancer avec : python seed.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'utilisateurs_service.settings')
django.setup()

from users.models import Utilisateur

utilisateurs_data = [
    {'email': 'admin@dit.sn', 'nom': 'Administrateur', 'prenom': 'DIT',
     'numero_carte': 'ADMIN001', 'type_utilisateur': 'ADMIN',
     'password': 'DIT@Admin2026!', 'is_staff': True, 'is_superuser': True,
     'telephone': '+221 33 000 00 00'},
    {'email': 'amadou.diallo@dit.sn', 'nom': 'Diallo', 'prenom': 'Amadou',
     'numero_carte': 'PROF001', 'type_utilisateur': 'PROFESSEUR',
     'password': 'Prof@2026!', 'telephone': '+221 77 100 00 01'},
    {'email': 'fatou.ndiaye@dit.sn', 'nom': 'Ndiaye', 'prenom': 'Fatou',
     'numero_carte': 'PROF002', 'type_utilisateur': 'PROFESSEUR',
     'password': 'Prof@2026!', 'telephone': '+221 77 100 00 02'},
    {'email': 'omar.cisse@dit.sn', 'nom': 'Cisse', 'prenom': 'Omar',
     'numero_carte': 'PROF003', 'type_utilisateur': 'PROFESSEUR',
     'password': 'Prof@2026!', 'telephone': '+221 77 100 00 03'},
    {'email': 'aminata.gueye@dit.sn', 'nom': 'Gueye', 'prenom': 'Aminata',
     'numero_carte': 'PROF004', 'type_utilisateur': 'PROFESSEUR',
     'password': 'Prof@2026!', 'telephone': '+221 77 100 00 04'},
    {'email': 'cheikh.sy@dit.sn', 'nom': 'Sy', 'prenom': 'Cheikh',
     'numero_carte': 'PROF005', 'type_utilisateur': 'PROFESSEUR',
     'password': 'Prof@2026!', 'telephone': '+221 77 100 00 05'},
    {'email': 'moussa.ba@etu.dit.sn', 'nom': 'Ba', 'prenom': 'Moussa',
     'numero_carte': 'ETU2026001', 'type_utilisateur': 'ETUDIANT',
     'password': 'Etu@2026!', 'telephone': '+221 77 200 00 01'},
    {'email': 'aissatou.fall@etu.dit.sn', 'nom': 'Fall', 'prenom': 'Aissatou',
     'numero_carte': 'ETU2026002', 'type_utilisateur': 'ETUDIANT',
     'password': 'Etu@2026!', 'telephone': '+221 77 200 00 02'},
    {'email': 'ibrahima.sow@etu.dit.sn', 'nom': 'Sow', 'prenom': 'Ibrahima',
     'numero_carte': 'ETU2026003', 'type_utilisateur': 'ETUDIANT',
     'password': 'Etu@2026!'},
    {'email': 'mariama.kane@etu.dit.sn', 'nom': 'Kane', 'prenom': 'Mariama',
     'numero_carte': 'ETU2026004', 'type_utilisateur': 'ETUDIANT',
     'password': 'Etu@2026!'},
    {'email': 'abdoulaye.diop@etu.dit.sn', 'nom': 'Diop', 'prenom': 'Abdoulaye',
     'numero_carte': 'ETU2026005', 'type_utilisateur': 'ETUDIANT',
     'password': 'Etu@2026!'},
    {'email': 'aida.thiam@etu.dit.sn', 'nom': 'Thiam', 'prenom': 'Aida',
     'numero_carte': 'ETU2026006', 'type_utilisateur': 'ETUDIANT',
     'password': 'Etu@2026!'},
    {'email': 'mamadou.diagne@etu.dit.sn', 'nom': 'Diagne', 'prenom': 'Mamadou',
     'numero_carte': 'ETU2026007', 'type_utilisateur': 'ETUDIANT',
     'password': 'Etu@2026!'},
    {'email': 'khadija.seck@etu.dit.sn', 'nom': 'Seck', 'prenom': 'Khadija',
     'numero_carte': 'ETU2026008', 'type_utilisateur': 'ETUDIANT',
     'password': 'Etu@2026!'},
    {'email': 'oumar.mbaye@etu.dit.sn', 'nom': 'Mbaye', 'prenom': 'Oumar',
     'numero_carte': 'ETU2026009', 'type_utilisateur': 'ETUDIANT',
     'password': 'Etu@2026!'},
    {'email': 'binta.faye@etu.dit.sn', 'nom': 'Faye', 'prenom': 'Binta',
     'numero_carte': 'ETU2026010', 'type_utilisateur': 'ETUDIANT',
     'password': 'Etu@2026!'},
    {'email': 'lamine.toure@etu.dit.sn', 'nom': 'Toure', 'prenom': 'Lamine',
     'numero_carte': 'ETU2026011', 'type_utilisateur': 'ETUDIANT',
     'password': 'Etu@2026!'},
    {'email': 'awa.dieng@etu.dit.sn', 'nom': 'Dieng', 'prenom': 'Awa',
     'numero_carte': 'ETU2026012', 'type_utilisateur': 'ETUDIANT',
     'password': 'Etu@2026!'},
    {'email': 'pape.sarr@etu.dit.sn', 'nom': 'Sarr', 'prenom': 'Pape',
     'numero_carte': 'ETU2026013', 'type_utilisateur': 'ETUDIANT',
     'password': 'Etu@2026!'},
    {'email': 'rama.ndoye@etu.dit.sn', 'nom': 'Ndoye', 'prenom': 'Rama',
     'numero_carte': 'ETU2026014', 'type_utilisateur': 'ETUDIANT',
     'password': 'Etu@2026!'},
    {'email': 'ousseynou.gaye@etu.dit.sn', 'nom': 'Gaye', 'prenom': 'Ousseynou',
     'numero_carte': 'ETU2026015', 'type_utilisateur': 'ETUDIANT',
     'password': 'Etu@2026!'},
    {'email': 'penda.lo@etu.dit.sn', 'nom': 'Lo', 'prenom': 'Penda',
     'numero_carte': 'ETU2026016', 'type_utilisateur': 'ETUDIANT',
     'password': 'Etu@2026!'},
    {'email': 'malick.camara@etu.dit.sn', 'nom': 'Camara', 'prenom': 'Malick',
     'numero_carte': 'ETU2026017', 'type_utilisateur': 'ETUDIANT',
     'password': 'Etu@2026!'},
    {'email': 'sokhna.ndiaye@etu.dit.sn', 'nom': 'Ndiaye', 'prenom': 'Sokhna',
     'numero_carte': 'ETU2026018', 'type_utilisateur': 'ETUDIANT',
     'password': 'Etu@2026!'},
    {'email': 'modou.sene@etu.dit.sn', 'nom': 'Sene', 'prenom': 'Modou',
     'numero_carte': 'ETU2026019', 'type_utilisateur': 'ETUDIANT',
     'password': 'Etu@2026!'},
    {'email': 'ndeye.diatta@etu.dit.sn', 'nom': 'Diatta', 'prenom': 'Ndeye',
     'numero_carte': 'ETU2026020', 'type_utilisateur': 'ETUDIANT',
     'password': 'Etu@2026!'},
    {'email': 'serigne.thiaw@etu.dit.sn', 'nom': 'Thiaw', 'prenom': 'Serigne',
     'numero_carte': 'ETU2026021', 'type_utilisateur': 'ETUDIANT',
     'password': 'Etu@2026!'},
    {'email': 'adji.niang@etu.dit.sn', 'nom': 'Niang', 'prenom': 'Adji',
     'numero_carte': 'ETU2026022', 'type_utilisateur': 'ETUDIANT',
     'password': 'Etu@2026!'},
    {'email': 'bibliothecaire@dit.sn', 'nom': 'Sarr', 'prenom': 'Ousmane',
     'numero_carte': 'PERS001', 'type_utilisateur': 'PERSONNEL',
     'password': 'Pers@2026!', 'telephone': '+221 77 300 00 01'},
    {'email': 'documentaliste@dit.sn', 'nom': 'Wade', 'prenom': 'Astou',
     'numero_carte': 'PERS002', 'type_utilisateur': 'PERSONNEL',
     'password': 'Pers@2026!', 'telephone': '+221 77 300 00 02'},
]

print("Creation des utilisateurs...")
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
        print(f"  [+] {user.nom_complet} ({user.type_utilisateur})")
    else:
        print(f"  [~] {email} existe deja")

print(f"\nBase initialisee : {Utilisateur.objects.count()} utilisateurs")
