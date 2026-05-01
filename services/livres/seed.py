"""
Script de peuplement initial de la base de donnees du service Livres.
Lancer avec : python seed.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'livres_service.settings')
django.setup()

from books.models import Categorie, Livre

categories_data = [
    {'nom': 'Informatique', 'description': 'Programmation, algorithmes, reseaux, IA'},
    {'nom': 'Mathematiques', 'description': 'Algebre, analyse, probabilites, statistiques'},
    {'nom': 'Intelligence Artificielle', 'description': 'Machine Learning, Deep Learning, NLP'},
    {'nom': 'Sciences', 'description': 'Physique, chimie, biologie'},
    {'nom': 'Litterature', 'description': 'Romans, nouvelles, poesie'},
]

categories = {}
for data in categories_data:
    cat, _ = Categorie.objects.get_or_create(nom=data['nom'], defaults=data)
    categories[cat.nom] = cat
    print(f"  Categorie : {cat.nom}")

livres_data = [
    {'titre': "Introduction a l'IA", 'auteur': 'Stuart Russell', 'isbn': '9782744005084', 'editeur': 'Pearson', 'annee_publication': 2022, 'langue': 'fr', 'categorie': categories['Intelligence Artificielle'], 'quantite_totale': 5, 'quantite_disponible': 5},
    {'titre': 'Deep Learning', 'auteur': 'Ian Goodfellow', 'isbn': '9782100780730', 'editeur': 'MIT Press', 'annee_publication': 2016, 'langue': 'fr', 'categorie': categories['Intelligence Artificielle'], 'quantite_totale': 3, 'quantite_disponible': 3},
    {'titre': 'NLP with Python', 'auteur': 'Steven Bird', 'isbn': '9780596516499', 'editeur': "O'Reilly", 'annee_publication': 2009, 'langue': 'en', 'categorie': categories['Intelligence Artificielle'], 'quantite_totale': 2, 'quantite_disponible': 2},
    {'titre': 'Pattern Recognition and ML', 'auteur': 'Christopher Bishop', 'isbn': '9780387310732', 'editeur': 'Springer', 'annee_publication': 2006, 'langue': 'en', 'categorie': categories['Intelligence Artificielle'], 'quantite_totale': 2, 'quantite_disponible': 2},
    {'titre': 'Hands-On Machine Learning', 'auteur': 'Aurelien Geron', 'isbn': '9781492032649', 'editeur': "O'Reilly", 'annee_publication': 2019, 'langue': 'en', 'categorie': categories['Intelligence Artificielle'], 'quantite_totale': 4, 'quantite_disponible': 4},
    {'titre': 'Reinforcement Learning', 'auteur': 'Richard Sutton', 'isbn': '9780262039246', 'editeur': 'MIT Press', 'annee_publication': 2018, 'langue': 'en', 'categorie': categories['Intelligence Artificielle'], 'quantite_totale': 2, 'quantite_disponible': 2},
    {'titre': 'Speech and Language Processing', 'auteur': 'Daniel Jurafsky', 'isbn': '9780131873216', 'editeur': 'Pearson', 'annee_publication': 2008, 'langue': 'en', 'categorie': categories['Intelligence Artificielle'], 'quantite_totale': 2, 'quantite_disponible': 2},
    {'titre': 'Computer Vision', 'auteur': 'Richard Szeliski', 'isbn': '9783030343712', 'editeur': 'Springer', 'annee_publication': 2022, 'langue': 'en', 'categorie': categories['Intelligence Artificielle'], 'quantite_totale': 2, 'quantite_disponible': 2},
    {'titre': 'Deep Learning with Python', 'auteur': 'Francois Chollet', 'isbn': '9781617294433', 'editeur': 'Manning', 'annee_publication': 2017, 'langue': 'en', 'categorie': categories['Intelligence Artificielle'], 'quantite_totale': 3, 'quantite_disponible': 3},
    {'titre': 'Probabilistic Machine Learning', 'auteur': 'Kevin Murphy', 'isbn': '9780262046824', 'editeur': 'MIT Press', 'annee_publication': 2022, 'langue': 'en', 'categorie': categories['Intelligence Artificielle'], 'quantite_totale': 2, 'quantite_disponible': 2},
    {'titre': 'AI: A Modern Approach', 'auteur': 'Peter Norvig', 'isbn': '9780134610993', 'editeur': 'Pearson', 'annee_publication': 2020, 'langue': 'en', 'categorie': categories['Intelligence Artificielle'], 'quantite_totale': 4, 'quantite_disponible': 4},
    {'titre': "L'IA expliquee", 'auteur': 'Luc Julia', 'isbn': '9782845639300', 'editeur': 'First', 'annee_publication': 2019, 'langue': 'fr', 'categorie': categories['Intelligence Artificielle'], 'quantite_totale': 3, 'quantite_disponible': 3},
    {'titre': 'GANs in Action', 'auteur': 'Jakub Langr', 'isbn': '9781617295560', 'editeur': 'Manning', 'annee_publication': 2019, 'langue': 'en', 'categorie': categories['Intelligence Artificielle'], 'quantite_totale': 1, 'quantite_disponible': 1},
    {'titre': 'Transformers for NLP', 'auteur': 'Denis Rothman', 'isbn': '9781800565791', 'editeur': 'Packt', 'annee_publication': 2021, 'langue': 'en', 'categorie': categories['Intelligence Artificielle'], 'quantite_totale': 2, 'quantite_disponible': 2},
    {'titre': 'Apprentissage Automatique', 'auteur': 'Massih-Reza Amini', 'isbn': '9782212679090', 'editeur': 'Eyrolles', 'annee_publication': 2020, 'langue': 'fr', 'categorie': categories['Intelligence Artificielle'], 'quantite_totale': 2, 'quantite_disponible': 2},
    {'titre': 'Python pour la Data Science', 'auteur': 'Jake VanderPlas', 'isbn': '9782100790319', 'editeur': "O'Reilly", 'annee_publication': 2020, 'langue': 'fr', 'categorie': categories['Informatique'], 'quantite_totale': 4, 'quantite_disponible': 4},
    {'titre': 'Algorithmes', 'auteur': 'Thomas Cormen', 'isbn': '9782100767717', 'editeur': 'Dunod', 'annee_publication': 2019, 'langue': 'fr', 'categorie': categories['Informatique'], 'quantite_totale': 6, 'quantite_disponible': 6},
    {'titre': 'Clean Code', 'auteur': 'Robert C. Martin', 'isbn': '9780132350884', 'editeur': 'Prentice Hall', 'annee_publication': 2008, 'langue': 'en', 'categorie': categories['Informatique'], 'quantite_totale': 3, 'quantite_disponible': 3},
    {'titre': 'The Pragmatic Programmer', 'auteur': 'David Thomas', 'isbn': '9780135957059', 'editeur': 'Addison-Wesley', 'annee_publication': 2019, 'langue': 'en', 'categorie': categories['Informatique'], 'quantite_totale': 3, 'quantite_disponible': 3},
    {'titre': 'Design Patterns', 'auteur': 'Erich Gamma', 'isbn': '9780201633610', 'editeur': 'Addison-Wesley', 'annee_publication': 1994, 'langue': 'en', 'categorie': categories['Informatique'], 'quantite_totale': 2, 'quantite_disponible': 2},
    {'titre': 'Refactoring', 'auteur': 'Martin Fowler', 'isbn': '9780134757599', 'editeur': 'Addison-Wesley', 'annee_publication': 2018, 'langue': 'en', 'categorie': categories['Informatique'], 'quantite_totale': 2, 'quantite_disponible': 2},
    {'titre': 'Effective Python', 'auteur': 'Brett Slatkin', 'isbn': '9780134853987', 'editeur': 'Addison-Wesley', 'annee_publication': 2019, 'langue': 'en', 'categorie': categories['Informatique'], 'quantite_totale': 2, 'quantite_disponible': 2},
    {'titre': 'Designing Data-Intensive Apps', 'auteur': 'Martin Kleppmann', 'isbn': '9781449373320', 'editeur': "O'Reilly", 'annee_publication': 2017, 'langue': 'en', 'categorie': categories['Informatique'], 'quantite_totale': 3, 'quantite_disponible': 3},
    {'titre': 'Java: The Complete Reference', 'auteur': 'Herbert Schildt', 'isbn': '9781260440232', 'editeur': 'McGraw-Hill', 'annee_publication': 2020, 'langue': 'en', 'categorie': categories['Informatique'], 'quantite_totale': 2, 'quantite_disponible': 2},
    {'titre': 'Linux: The Complete Reference', 'auteur': 'Richard Petersen', 'isbn': '9780071496292', 'editeur': 'McGraw-Hill', 'annee_publication': 2008, 'langue': 'en', 'categorie': categories['Informatique'], 'quantite_totale': 2, 'quantite_disponible': 2},
    {'titre': 'Computer Networks', 'auteur': 'Andrew Tanenbaum', 'isbn': '9780132126953', 'editeur': 'Pearson', 'annee_publication': 2010, 'langue': 'en', 'categorie': categories['Informatique'], 'quantite_totale': 3, 'quantite_disponible': 3},
    {'titre': 'Operating System Concepts', 'auteur': 'Abraham Silberschatz', 'isbn': '9781119320913', 'editeur': 'Wiley', 'annee_publication': 2018, 'langue': 'en', 'categorie': categories['Informatique'], 'quantite_totale': 2, 'quantite_disponible': 2},
    {'titre': 'Cracking the Coding Interview', 'auteur': 'Gayle McDowell', 'isbn': '9780984782857', 'editeur': 'CareerCup', 'annee_publication': 2015, 'langue': 'en', 'categorie': categories['Informatique'], 'quantite_totale': 4, 'quantite_disponible': 4},
    {'titre': "You Don't Know JS", 'auteur': 'Kyle Simpson', 'isbn': '9781491904244', 'editeur': "O'Reilly", 'annee_publication': 2015, 'langue': 'en', 'categorie': categories['Informatique'], 'quantite_totale': 2, 'quantite_disponible': 2},
    {'titre': 'Docker en Pratique', 'auteur': 'Pierre-Yves Cloux', 'isbn': '9782100787654', 'editeur': 'Dunod', 'annee_publication': 2021, 'langue': 'fr', 'categorie': categories['Informatique'], 'quantite_totale': 3, 'quantite_disponible': 3},
    {'titre': 'Probabilites et Statistiques', 'auteur': 'Paul-Louis Hennequin', 'isbn': '9782100715671', 'editeur': 'Dunod', 'annee_publication': 2018, 'langue': 'fr', 'categorie': categories['Mathematiques'], 'quantite_totale': 4, 'quantite_disponible': 4},
    {'titre': 'Algebre Lineaire', 'auteur': 'Joseph Grifone', 'isbn': '9782705681142', 'editeur': 'Cepadues', 'annee_publication': 2015, 'langue': 'fr', 'categorie': categories['Mathematiques'], 'quantite_totale': 3, 'quantite_disponible': 3},
    {'titre': 'Analyse pour la Licence', 'auteur': 'Daniel Fredon', 'isbn': '9782100727216', 'editeur': 'Dunod', 'annee_publication': 2015, 'langue': 'fr', 'categorie': categories['Mathematiques'], 'quantite_totale': 3, 'quantite_disponible': 3},
    {'titre': 'Mathematics for Machine Learning', 'auteur': 'Marc Deisenroth', 'isbn': '9781108455145', 'editeur': 'Cambridge', 'annee_publication': 2020, 'langue': 'en', 'categorie': categories['Mathematiques'], 'quantite_totale': 3, 'quantite_disponible': 3},
    {'titre': 'Linear Algebra Done Right', 'auteur': 'Sheldon Axler', 'isbn': '9783319110790', 'editeur': 'Springer', 'annee_publication': 2015, 'langue': 'en', 'categorie': categories['Mathematiques'], 'quantite_totale': 2, 'quantite_disponible': 2},
    {'titre': 'Convex Optimization', 'auteur': 'Stephen Boyd', 'isbn': '9780521833783', 'editeur': 'Cambridge', 'annee_publication': 2004, 'langue': 'en', 'categorie': categories['Mathematiques'], 'quantite_totale': 2, 'quantite_disponible': 2},
    {'titre': 'Calculus', 'auteur': 'Michael Spivak', 'isbn': '9780914098911', 'editeur': 'Publish or Perish', 'annee_publication': 2008, 'langue': 'en', 'categorie': categories['Mathematiques'], 'quantite_totale': 2, 'quantite_disponible': 2},
    {'titre': 'Discrete Mathematics', 'auteur': 'Kenneth Rosen', 'isbn': '9780073383095', 'editeur': 'McGraw-Hill', 'annee_publication': 2018, 'langue': 'en', 'categorie': categories['Mathematiques'], 'quantite_totale': 3, 'quantite_disponible': 3},
    {'titre': 'Theorie des Graphes', 'auteur': 'Aimee Lombardi', 'isbn': '9782705694326', 'editeur': 'Cepadues', 'annee_publication': 2017, 'langue': 'fr', 'categorie': categories['Mathematiques'], 'quantite_totale': 2, 'quantite_disponible': 2},
    {'titre': 'Numerical Recipes', 'auteur': 'William Press', 'isbn': '9780521880688', 'editeur': 'Cambridge', 'annee_publication': 2007, 'langue': 'en', 'categorie': categories['Mathematiques'], 'quantite_totale': 2, 'quantite_disponible': 2},
    {'titre': 'Physique Generale', 'auteur': 'Hugh Young', 'isbn': '9782761332293', 'editeur': 'Pearson', 'annee_publication': 2014, 'langue': 'fr', 'categorie': categories['Sciences'], 'quantite_totale': 3, 'quantite_disponible': 3},
    {'titre': 'Chimie Organique', 'auteur': 'Paula Bruice', 'isbn': '9782761379892', 'editeur': 'Pearson', 'annee_publication': 2017, 'langue': 'fr', 'categorie': categories['Sciences'], 'quantite_totale': 2, 'quantite_disponible': 2},
    {'titre': 'Biologie Moleculaire', 'auteur': 'James Watson', 'isbn': '9782807304277', 'editeur': 'De Boeck', 'annee_publication': 2018, 'langue': 'fr', 'categorie': categories['Sciences'], 'quantite_totale': 2, 'quantite_disponible': 2},
    {'titre': 'A Brief History of Time', 'auteur': 'Stephen Hawking', 'isbn': '9780553380163', 'editeur': 'Bantam', 'annee_publication': 1998, 'langue': 'en', 'categorie': categories['Sciences'], 'quantite_totale': 2, 'quantite_disponible': 2},
    {'titre': 'The Selfish Gene', 'auteur': 'Richard Dawkins', 'isbn': '9780198788607', 'editeur': 'Oxford', 'annee_publication': 2016, 'langue': 'en', 'categorie': categories['Sciences'], 'quantite_totale': 2, 'quantite_disponible': 2},
    {'titre': 'Les Miserables', 'auteur': 'Victor Hugo', 'isbn': '9782070409228', 'editeur': 'Gallimard', 'annee_publication': 1862, 'langue': 'fr', 'categorie': categories['Litterature'], 'quantite_totale': 2, 'quantite_disponible': 2},
    {'titre': 'Les Soleils des Independances', 'auteur': 'Ahmadou Kourouma', 'isbn': '9782020025348', 'editeur': 'Seuil', 'annee_publication': 1968, 'langue': 'fr', 'categorie': categories['Litterature'], 'quantite_totale': 3, 'quantite_disponible': 3},
    {'titre': 'Une si longue lettre', 'auteur': 'Mariama Ba', 'isbn': '9782723601658', 'editeur': 'NEAS', 'annee_publication': 1979, 'langue': 'fr', 'categorie': categories['Litterature'], 'quantite_totale': 4, 'quantite_disponible': 4},
    {'titre': "L'Aventure ambigue", 'auteur': 'Cheikh Hamidou Kane', 'isbn': '9782264025203', 'editeur': '10/18', 'annee_publication': 1961, 'langue': 'fr', 'categorie': categories['Litterature'], 'quantite_totale': 3, 'quantite_disponible': 3},
    {'titre': '1984', 'auteur': 'George Orwell', 'isbn': '9780451524935', 'editeur': 'Signet', 'annee_publication': 1949, 'langue': 'en', 'categorie': categories['Litterature'], 'quantite_totale': 3, 'quantite_disponible': 3},
]

for data in livres_data:
    livre, created = Livre.objects.get_or_create(isbn=data['isbn'], defaults=data)
    action = 'Cree' if created else 'Existe deja'
    print(f"  [{action}] {livre.titre}")

print(f"\nBase de donnees initialisee avec succes !")
print(f"  {Categorie.objects.count()} categories")
print(f"  {Livre.objects.count()} livres")
