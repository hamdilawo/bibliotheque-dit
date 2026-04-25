"""
Script de peuplement initial de la base de données du service Livres.
Lancer avec : python seed.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'livres_service.settings')
django.setup()

from books.models import Categorie, Livre

# --- Catégories ---
categories_data = [
    {'nom': 'Informatique', 'description': 'Programmation, algorithmes, réseaux, IA'},
    {'nom': 'Mathématiques', 'description': 'Algèbre, analyse, probabilités, statistiques'},
    {'nom': 'Intelligence Artificielle', 'description': 'Machine Learning, Deep Learning, NLP'},
    {'nom': 'Sciences', 'description': 'Physique, chimie, biologie'},
    {'nom': 'Littérature', 'description': 'Romans, nouvelles, poésie'},
]

categories = {}
for data in categories_data:
    cat, _ = Categorie.objects.get_or_create(nom=data['nom'], defaults=data)
    categories[cat.nom] = cat
    print(f"  Catégorie : {cat.nom}")

# --- Livres ---
livres_data = [
    {
        'titre': 'Introduction à l\'Intelligence Artificielle',
        'auteur': 'Stuart Russell',
        'isbn': '9782744005084',
        'editeur': 'Pearson',
        'annee_publication': 2022,
        'langue': 'fr',
        'categorie': categories['Intelligence Artificielle'],
        'quantite_totale': 5,
        'quantite_disponible': 5,
        'description': 'La référence mondiale en IA, couvrant tous les domaines du domaine.',
    },
    {
        'titre': 'Deep Learning',
        'auteur': 'Ian Goodfellow',
        'isbn': '9782100780730',
        'editeur': 'MIT Press',
        'annee_publication': 2016,
        'langue': 'fr',
        'categorie': categories['Intelligence Artificielle'],
        'quantite_totale': 3,
        'quantite_disponible': 3,
        'description': 'Le livre de référence sur le deep learning.',
    },
    {
        'titre': 'Python pour la Data Science',
        'auteur': 'Jake VanderPlas',
        'isbn': '9782100790319',
        'editeur': 'O\'Reilly',
        'annee_publication': 2020,
        'langue': 'fr',
        'categorie': categories['Informatique'],
        'quantite_totale': 4,
        'quantite_disponible': 4,
    },
    {
        'titre': 'Algorithmes — Notions de base',
        'auteur': 'Thomas Cormen',
        'isbn': '9782100767717',
        'editeur': 'Dunod',
        'annee_publication': 2019,
        'langue': 'fr',
        'categorie': categories['Informatique'],
        'quantite_totale': 6,
        'quantite_disponible': 6,
    },
    {
        'titre': 'Probabilités et Statistiques',
        'auteur': 'Paul-Louis Hennequin',
        'isbn': '9782100715671',
        'editeur': 'Dunod',
        'annee_publication': 2018,
        'langue': 'fr',
        'categorie': categories['Mathématiques'],
        'quantite_totale': 4,
        'quantite_disponible': 4,
    },
    {
        'titre': 'Natural Language Processing with Python',
        'auteur': 'Steven Bird',
        'isbn': '9780596516499',
        'editeur': 'O\'Reilly',
        'annee_publication': 2009,
        'langue': 'en',
        'categorie': categories['Intelligence Artificielle'],
        'quantite_totale': 2,
        'quantite_disponible': 2,
    },
    {
        'titre': 'Clean Code',
        'auteur': 'Robert C. Martin',
        'isbn': '9780132350884',
        'editeur': 'Prentice Hall',
        'annee_publication': 2008,
        'langue': 'en',
        'categorie': categories['Informatique'],
        'quantite_totale': 3,
        'quantite_disponible': 3,
    },
    {
        'titre': 'Les Misérables',
        'auteur': 'Victor Hugo',
        'isbn': '9782070409228',
        'editeur': 'Gallimard',
        'annee_publication': 1862,
        'langue': 'fr',
        'categorie': categories['Littérature'],
        'quantite_totale': 2,
        'quantite_disponible': 2,
    },
]

for data in livres_data:
    livre, created = Livre.objects.get_or_create(isbn=data['isbn'], defaults=data)
    action = 'Créé' if created else 'Existe déjà'
    print(f"  [{action}] {livre.titre}")

print(f"\nBase de données initialisée avec succès !")
print(f"  {Categorie.objects.count()} catégories")
print(f"  {Livre.objects.count()} livres")
