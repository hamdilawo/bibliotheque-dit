"""
Script de peuplement — Service Emprunts.
Génère un historique réaliste pour alimenter le pipeline DVC/ML.
Lancer avec : python seed.py
"""
import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emprunts_service.settings')
django.setup()

from loans.models import Emprunt

# Données simulées (normalement récupérées via les services)
UTILISATEURS = [
    {'id': 1, 'nom': 'Moussa Ba', 'carte': 'ETU2026001', 'type': 'ETUDIANT'},
    {'id': 2, 'nom': 'Aissatou Fall', 'carte': 'ETU2026002', 'type': 'ETUDIANT'},
    {'id': 3, 'nom': 'Ibrahima Sow', 'carte': 'ETU2026003', 'type': 'ETUDIANT'},
    {'id': 4, 'nom': 'Mariama Kane', 'carte': 'ETU2026004', 'type': 'ETUDIANT'},
    {'id': 5, 'nom': 'Amadou Diallo', 'carte': 'PROF001', 'type': 'PROFESSEUR'},
    {'id': 6, 'nom': 'Fatou Ndiaye', 'carte': 'PROF002', 'type': 'PROFESSEUR'},
]

LIVRES = [
    {'id': 1, 'titre': 'Introduction à l\'IA', 'isbn': '9782744005084', 'auteur': 'Stuart Russell'},
    {'id': 2, 'titre': 'Deep Learning', 'isbn': '9782100780730', 'auteur': 'Ian Goodfellow'},
    {'id': 3, 'titre': 'Python pour la Data Science', 'isbn': '9782100790319', 'auteur': 'Jake VanderPlas'},
    {'id': 4, 'titre': 'Algorithmes', 'isbn': '9782100767717', 'auteur': 'Thomas Cormen'},
    {'id': 5, 'titre': 'Probabilités et Statistiques', 'isbn': '9782100715671', 'auteur': 'Hennequin'},
    {'id': 6, 'titre': 'NLP with Python', 'isbn': '9780596516499', 'auteur': 'Steven Bird'},
    {'id': 7, 'titre': 'Clean Code', 'isbn': '9780132350884', 'auteur': 'Robert C. Martin'},
]

print("Génération de l'historique des emprunts...")
Emprunt.objects.all().delete()

emprunts_crees = 0
today = date.today()

# Générer ~60 emprunts sur les 6 derniers mois
for _ in range(60):
    utilisateur = random.choice(UTILISATEURS)
    livre = random.choice(LIVRES)

    # Date d'emprunt aléatoire sur 6 mois
    jours_passes = random.randint(1, 180)
    date_emprunt = today - timedelta(days=jours_passes)

    # Durée selon le type
    duree = 14 if utilisateur['type'] == 'ETUDIANT' else 30
    date_retour_prevue = date_emprunt + timedelta(days=duree)

    # Décider si retourné ou en cours
    if date_retour_prevue < today:
        # Déjà dû être retourné
        retard = random.choice([0, 0, 0, random.randint(1, 15)])
        date_retour_effective = date_retour_prevue + timedelta(days=retard)
        if date_retour_effective > today:
            date_retour_effective = today
        statut = 'RETOURNE'
        jours_retard = retard
        penalite = retard * 200
    else:
        statut = 'EN_COURS'
        date_retour_effective = None
        jours_retard = 0
        penalite = 0

    emprunt = Emprunt(
        utilisateur_id=utilisateur['id'],
        livre_id=livre['id'],
        utilisateur_nom=utilisateur['nom'],
        utilisateur_carte=utilisateur['carte'],
        livre_titre=livre['titre'],
        livre_isbn=livre['isbn'],
        livre_auteur=livre['auteur'],
        date_retour_prevue=date_retour_prevue,
        date_retour_effective=date_retour_effective,
        statut=statut,
        jours_retard=jours_retard,
        penalite_fcfa=penalite,
    )
    # Bypass auto_now_add pour fixer la date
    Emprunt.objects.bulk_create([emprunt])
    emprunts_crees += 1

print(f"  {emprunts_crees} emprunts générés")
print(f"  {Emprunt.objects.filter(statut='RETOURNE').count()} retournés")
print(f"  {Emprunt.objects.filter(statut='EN_COURS').count()} en cours")
print(f"  {Emprunt.objects.filter(jours_retard__gt=0).count()} avec retard")
print("\nHistorique prêt pour l'export DVC !")
