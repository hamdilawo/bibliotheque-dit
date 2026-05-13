"""
Script de peuplement - Service Emprunts.
Genere un historique realiste avec patterns de comportement
pour alimenter le pipeline DVC/ML.

Strategie :
- Chaque utilisateur a une "categorie favorite" (1 parmi 5)
- 70% de ses emprunts sont dans sa categorie favorite
- 30% sont disperses dans les autres categories
- Cette structure cree du signal pour SVD/KNN

Lancer avec : python seed.py
"""
import os
import django
import random
from datetime import date, timedelta
from collections import Counter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'emprunts_service.settings')
django.setup()

from loans.models import Emprunt

random.seed(42)

UTILISATEURS = [
    {'id': 1,  'nom': 'Administrateur DIT', 'carte': 'ADMIN001',   'type': 'ADMIN'},
    {'id': 2,  'nom': 'Amadou Diallo',      'carte': 'PROF001',    'type': 'PROFESSEUR'},
    {'id': 3,  'nom': 'Fatou Ndiaye',       'carte': 'PROF002',    'type': 'PROFESSEUR'},
    {'id': 4,  'nom': 'Omar Cisse',         'carte': 'PROF003',    'type': 'PROFESSEUR'},
    {'id': 5,  'nom': 'Aminata Gueye',      'carte': 'PROF004',    'type': 'PROFESSEUR'},
    {'id': 6,  'nom': 'Cheikh Sy',          'carte': 'PROF005',    'type': 'PROFESSEUR'},
    {'id': 7,  'nom': 'Moussa Ba',          'carte': 'ETU2026001', 'type': 'ETUDIANT'},
    {'id': 8,  'nom': 'Aissatou Fall',      'carte': 'ETU2026002', 'type': 'ETUDIANT'},
    {'id': 9,  'nom': 'Ibrahima Sow',       'carte': 'ETU2026003', 'type': 'ETUDIANT'},
    {'id': 10, 'nom': 'Mariama Kane',       'carte': 'ETU2026004', 'type': 'ETUDIANT'},
    {'id': 11, 'nom': 'Abdoulaye Diop',     'carte': 'ETU2026005', 'type': 'ETUDIANT'},
    {'id': 12, 'nom': 'Aida Thiam',         'carte': 'ETU2026006', 'type': 'ETUDIANT'},
    {'id': 13, 'nom': 'Mamadou Diagne',     'carte': 'ETU2026007', 'type': 'ETUDIANT'},
    {'id': 14, 'nom': 'Khadija Seck',       'carte': 'ETU2026008', 'type': 'ETUDIANT'},
    {'id': 15, 'nom': 'Oumar Mbaye',        'carte': 'ETU2026009', 'type': 'ETUDIANT'},
    {'id': 16, 'nom': 'Binta Faye',         'carte': 'ETU2026010', 'type': 'ETUDIANT'},
    {'id': 17, 'nom': 'Lamine Toure',       'carte': 'ETU2026011', 'type': 'ETUDIANT'},
    {'id': 18, 'nom': 'Awa Dieng',          'carte': 'ETU2026012', 'type': 'ETUDIANT'},
    {'id': 19, 'nom': 'Pape Sarr',          'carte': 'ETU2026013', 'type': 'ETUDIANT'},
    {'id': 20, 'nom': 'Rama Ndoye',         'carte': 'ETU2026014', 'type': 'ETUDIANT'},
    {'id': 21, 'nom': 'Ousseynou Gaye',     'carte': 'ETU2026015', 'type': 'ETUDIANT'},
    {'id': 22, 'nom': 'Penda Lo',           'carte': 'ETU2026016', 'type': 'ETUDIANT'},
    {'id': 23, 'nom': 'Malick Camara',      'carte': 'ETU2026017', 'type': 'ETUDIANT'},
    {'id': 24, 'nom': 'Sokhna Ndiaye',      'carte': 'ETU2026018', 'type': 'ETUDIANT'},
    {'id': 25, 'nom': 'Modou Sene',         'carte': 'ETU2026019', 'type': 'ETUDIANT'},
    {'id': 26, 'nom': 'Ndeye Diatta',       'carte': 'ETU2026020', 'type': 'ETUDIANT'},
    {'id': 27, 'nom': 'Serigne Thiaw',      'carte': 'ETU2026021', 'type': 'ETUDIANT'},
    {'id': 28, 'nom': 'Adji Niang',         'carte': 'ETU2026022', 'type': 'ETUDIANT'},
    {'id': 29, 'nom': 'Ousmane Sarr',       'carte': 'PERS001',    'type': 'PERSONNEL'},
    {'id': 30, 'nom': 'Astou Wade',         'carte': 'PERS002',    'type': 'PERSONNEL'},
]

LIVRES_RAW = [
    (1,  "Introduction a l'IA",           '9782744005084', 'Stuart Russell',     'IA'),
    (2,  'Deep Learning',                  '9782100780730', 'Ian Goodfellow',     'IA'),
    (3,  'NLP with Python',                '9780596516499', 'Steven Bird',        'IA'),
    (4,  'Pattern Recognition and ML',     '9780387310732', 'Christopher Bishop', 'IA'),
    (5,  'Hands-On Machine Learning',      '9781492032649', 'Aurelien Geron',     'IA'),
    (6,  'Reinforcement Learning',         '9780262039246', 'Richard Sutton',     'IA'),
    (7,  'Speech and Language Processing', '9780131873216', 'Daniel Jurafsky',    'IA'),
    (8,  'Computer Vision',                '9783030343712', 'Richard Szeliski',   'IA'),
    (9,  'Deep Learning with Python',      '9781617294433', 'Francois Chollet',   'IA'),
    (10, 'Probabilistic Machine Learning', '9780262046824', 'Kevin Murphy',       'IA'),
    (11, 'AI: A Modern Approach',          '9780134610993', 'Peter Norvig',       'IA'),
    (12, "L'IA expliquee",                 '9782845639300', 'Luc Julia',          'IA'),
    (13, 'GANs in Action',                 '9781617295560', 'Jakub Langr',        'IA'),
    (14, 'Transformers for NLP',           '9781800565791', 'Denis Rothman',      'IA'),
    (15, 'Apprentissage Automatique',      '9782212679090', 'Massih-Reza Amini',  'IA'),
    (16, 'Python pour la Data Science',    '9782100790319', 'Jake VanderPlas',    'INFO'),
    (17, 'Algorithmes',                    '9782100767717', 'Thomas Cormen',      'INFO'),
    (18, 'Clean Code',                     '9780132350884', 'Robert C. Martin',   'INFO'),
    (19, 'The Pragmatic Programmer',       '9780135957059', 'David Thomas',       'INFO'),
    (20, 'Design Patterns',                '9780201633610', 'Erich Gamma',        'INFO'),
    (21, 'Refactoring',                    '9780134757599', 'Martin Fowler',      'INFO'),
    (22, 'Effective Python',               '9780134853987', 'Brett Slatkin',      'INFO'),
    (23, 'Designing Data-Intensive Apps',  '9781449373320', 'Martin Kleppmann',   'INFO'),
    (24, 'Java: The Complete Reference',   '9781260440232', 'Herbert Schildt',    'INFO'),
    (25, 'Linux: The Complete Reference',  '9780071496292', 'Richard Petersen',   'INFO'),
    (26, 'Computer Networks',              '9780132126953', 'Andrew Tanenbaum',   'INFO'),
    (27, 'Operating System Concepts',      '9781119320913', 'Abraham Silberschatz', 'INFO'),
    (28, 'Cracking the Coding Interview',  '9780984782857', 'Gayle McDowell',     'INFO'),
    (29, "You Don't Know JS",              '9781491904244', 'Kyle Simpson',       'INFO'),
    (30, 'Docker en Pratique',             '9782100787654', 'Pierre-Yves Cloux',  'INFO'),
    (31, 'Probabilites et Statistiques',   '9782100715671', 'Hennequin',          'MATH'),
    (32, 'Algebre Lineaire',               '9782705681142', 'Joseph Grifone',     'MATH'),
    (33, 'Analyse pour la Licence',        '9782100727216', 'Daniel Fredon',      'MATH'),
    (34, 'Mathematics for Machine Learning', '9781108455145', 'Marc Deisenroth',  'MATH'),
    (35, 'Linear Algebra Done Right',      '9783319110790', 'Sheldon Axler',      'MATH'),
    (36, 'Convex Optimization',            '9780521833783', 'Stephen Boyd',       'MATH'),
    (37, 'Calculus',                       '9780914098911', 'Michael Spivak',     'MATH'),
    (38, 'Discrete Mathematics',           '9780073383095', 'Kenneth Rosen',      'MATH'),
    (39, 'Theorie des Graphes',            '9782705694326', 'Aimee Lombardi',     'MATH'),
    (40, 'Numerical Recipes',              '9780521880688', 'William Press',      'MATH'),
    (41, 'Physique Generale',              '9782761332293', 'Hugh Young',         'SCI'),
    (42, 'Chimie Organique',               '9782761379892', 'Paula Bruice',       'SCI'),
    (43, 'Biologie Moleculaire',           '9782807304277', 'James Watson',       'SCI'),
    (44, 'A Brief History of Time',        '9780553380163', 'Stephen Hawking',    'SCI'),
    (45, 'The Selfish Gene',               '9780198788607', 'Richard Dawkins',    'SCI'),
    (46, 'Les Miserables',                 '9782070409228', 'Victor Hugo',        'LIT'),
    (47, 'Les Soleils des Independances',  '9782020025348', 'Ahmadou Kourouma',   'LIT'),
    (48, 'Une si longue lettre',           '9782723601658', 'Mariama Ba',         'LIT'),
    (49, "L'Aventure ambigue",             '9782264025203', 'Cheikh Hamidou Kane', 'LIT'),
    (50, '1984',                           '9780451524935', 'George Orwell',      'LIT'),
]

LIVRES = [{'id': i, 'titre': t, 'isbn': isbn, 'auteur': a, 'cat': c}
          for (i, t, isbn, a, c) in LIVRES_RAW]

LIVRES_PAR_CAT = {}
for livre in LIVRES:
    LIVRES_PAR_CAT.setdefault(livre['cat'], []).append(livre)

PROBA_CATEGORIE = ['IA', 'IA', 'IA', 'INFO', 'INFO', 'INFO', 'MATH', 'MATH', 'SCI', 'LIT']
PREF_UTILISATEUR = {u['id']: random.choice(PROBA_CATEGORIE) for u in UTILISATEURS}

print("Generation de l'historique des emprunts (avec patterns)...")
Emprunt.objects.all().delete()

NB_EMPRUNTS_CIBLE = 500
PROBA_FAVORITE = 0.70

today = date.today()
emprunts_a_creer = []

for _ in range(NB_EMPRUNTS_CIBLE):
    utilisateur = random.choice(UTILISATEURS)
    pref = PREF_UTILISATEUR[utilisateur['id']]

    if random.random() < PROBA_FAVORITE:
        livre = random.choice(LIVRES_PAR_CAT[pref])
    else:
        livre = random.choice(LIVRES)

    jours_passes = random.randint(1, 180)
    date_emprunt = today - timedelta(days=jours_passes)

    if utilisateur['type'] == 'ETUDIANT':
        duree = 14
    elif utilisateur['type'] == 'PROFESSEUR':
        duree = 30
    elif utilisateur['type'] == 'PERSONNEL':
        duree = 21
    else:
        duree = 60

    date_retour_prevue = date_emprunt + timedelta(days=duree)

    if date_retour_prevue < today:
        if random.random() < 0.75:
            retard = 0
        else:
            retard = random.randint(1, 20)
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

    emprunts_a_creer.append(Emprunt(
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
    ))

Emprunt.objects.bulk_create(emprunts_a_creer)

print(f"  {len(emprunts_a_creer)} emprunts generes")
print(f"  {Emprunt.objects.filter(statut='RETOURNE').count()} retournes")
print(f"  {Emprunt.objects.filter(statut='EN_COURS').count()} en cours")
print(f"  {Emprunt.objects.filter(jours_retard__gt=0).count()} avec retard")

print("\nDistribution des preferences :")
distribution = Counter(PREF_UTILISATEUR.values())
for cat, n in sorted(distribution.items(), key=lambda x: -x[1]):
    print(f"  {cat:5s} : {n} utilisateurs")

print("\nHistorique pret pour l'export DVC !")
