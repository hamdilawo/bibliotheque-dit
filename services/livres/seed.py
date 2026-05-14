"""
Script de peuplement initial — Service Livres (Piccolo ORM)

Usage :
    python seed.py           # Peuple sans supprimer les données existantes
    python seed.py --reset   # Supprime tout et repart de zéro
"""
from __future__ import annotations

import asyncio
import sys
from typing import Any, cast
from uuid import UUID

from features.books.tables import Categorie, Livre

OL = "https://covers.openlibrary.org/b/isbn"

def cover(isbn: str) -> str:
    return f"{OL}/{isbn}-L.jpg"


CATEGORIES = [
    {"nom": "Informatique",          "description": "Programmation, algorithmes, réseaux, systèmes"},
    {"nom": "Data Engineering",      "description": "Pipelines de données, ETL, architectures data"},
    {"nom": "Data Science",          "description": "Analyse de données, visualisation, statistiques"},
    {"nom": "Intelligence Artificielle", "description": "Machine Learning, Deep Learning, NLP"},
    {"nom": "Mathématiques",         "description": "Algèbre, analyse, probabilités, statistiques"},
    {"nom": "Sciences",              "description": "Physique, chimie, biologie"},
    {"nom": "Littérature",           "description": "Romans, nouvelles, poésie"},
]

LIVRES = [

    # ══════════════════════════════════════════════════════════════
    # Data Engineering
    # ══════════════════════════════════════════════════════════════
    {
        "titre": "Fundamentals of Data Engineering",
        "auteur": "Joe Reis & Matt Housley",
        "isbn": "9781098108298",
        "editeur": "O'Reilly",
        "annee_publication": 2022,
        "langue": "en",
        "nombre_pages": 414,
        "categorie": "Data Engineering",
        "quantite_totale": 5,
        "description": "Un guide complet pour comprendre le cycle de vie des données : ingestion, stockage, transformation et diffusion. Couvre les architectures modernes (lakehouse, streaming), les outils phares et les bonnes pratiques du data engineer.",
        "couverture_url": cover("9781098108298"),
    },
    {
        "titre": "Data Engineering with Python",
        "auteur": "Paul Crickard",
        "isbn": "9781839214189",
        "editeur": "Packt",
        "annee_publication": 2020,
        "langue": "en",
        "nombre_pages": 358,
        "categorie": "Data Engineering",
        "quantite_totale": 4,
        "description": "Apprenez à construire des pipelines de données robustes avec Python, Apache Airflow, Kafka et NiFi. Des projets pratiques couvrant l'ingestion, le traitement en batch/streaming et la livraison des données.",
        "couverture_url": cover("9781839214189"),
    },
    {
        "titre": "Designing Data-Intensive Applications",
        "auteur": "Martin Kleppmann",
        "isbn": "9781449373320",
        "editeur": "O'Reilly",
        "annee_publication": 2017,
        "langue": "en",
        "nombre_pages": 616,
        "categorie": "Data Engineering",
        "quantite_totale": 5,
        "description": "La référence absolue sur les systèmes distribués et les bases de données modernes. Couvre la réplication, le partitionnement, les transactions, les flux de données et les compromis architecturaux pour les systèmes à grande échelle.",
        "couverture_url": cover("9781449373320"),
    },
    {
        "titre": "The Data Warehouse Toolkit",
        "auteur": "Ralph Kimball & Margy Ross",
        "isbn": "9781118530801",
        "editeur": "Wiley",
        "annee_publication": 2013,
        "langue": "en",
        "nombre_pages": 600,
        "categorie": "Data Engineering",
        "quantite_totale": 3,
        "description": "La bible du dimensional modeling. Explique comment concevoir des entrepôts de données avec les techniques éprouvées de Kimball : tables de faits, dimensions, modèles en étoile et en flocon de neige.",
        "couverture_url": cover("9781118530801"),
    },
    {
        "titre": "Spark: The Definitive Guide",
        "auteur": "Bill Chambers & Matei Zaharia",
        "isbn": "9781491912218",
        "editeur": "O'Reilly",
        "annee_publication": 2018,
        "langue": "en",
        "nombre_pages": 604,
        "categorie": "Data Engineering",
        "quantite_totale": 4,
        "description": "Le guide complet d'Apache Spark par ses créateurs. Couvre l'API Structured Streaming, Spark SQL, le machine learning distribué et les optimisations pour le traitement de données à grande échelle.",
        "couverture_url": cover("9781491912218"),
    },
    {
        "titre": "Kafka: The Definitive Guide",
        "auteur": "Gwen Shapira & Neha Narkhede",
        "isbn": "9781492043089",
        "editeur": "O'Reilly",
        "annee_publication": 2021,
        "langue": "en",
        "nombre_pages": 500,
        "categorie": "Data Engineering",
        "quantite_totale": 3,
        "description": "Maîtrisez Apache Kafka, le système de streaming distribué. Producteurs, consommateurs, Kafka Streams et ksqlDB — tout pour construire des architectures event-driven à haute disponibilité.",
        "couverture_url": cover("9781492043089"),
    },
    {
        "titre": "Data Pipelines Pocket Reference",
        "auteur": "James Densmore",
        "isbn": "9781492087830",
        "editeur": "O'Reilly",
        "annee_publication": 2021,
        "langue": "en",
        "nombre_pages": 260,
        "categorie": "Data Engineering",
        "quantite_totale": 3,
        "description": "Un guide pratique pour concevoir, construire et maintenir des pipelines de données modernes. Couvre l'extraction, la transformation, le chargement (ETL/ELT) et les tests de qualité des données.",
        "couverture_url": cover("9781492087830"),
    },
    {
        "titre": "Learning dbt",
        "auteur": "Amy Chen & Karrie Zhao",
        "isbn": "9781098149819",
        "editeur": "O'Reilly",
        "annee_publication": 2023,
        "langue": "en",
        "nombre_pages": 320,
        "categorie": "Data Engineering",
        "quantite_totale": 3,
        "description": "Apprenez dbt (data build tool), l'outil qui transforme la façon dont les équipes data gèrent leurs transformations SQL. Tests, documentation, lineage et déploiement continu dans votre entrepôt de données.",
        "couverture_url": cover("9781098149819"),
    },

    # ══════════════════════════════════════════════════════════════
    # Data Science
    # ══════════════════════════════════════════════════════════════
    {
        "titre": "Python Data Science Handbook",
        "auteur": "Jake VanderPlas",
        "isbn": "9781491912058",
        "editeur": "O'Reilly",
        "annee_publication": 2016,
        "langue": "en",
        "nombre_pages": 548,
        "categorie": "Data Science",
        "quantite_totale": 5,
        "description": "La référence complète pour la Data Science avec Python. NumPy, Pandas, Matplotlib, Scikit-learn et IPython/Jupyter — tout ce qu'il faut pour analyser des données, les visualiser et construire des modèles.",
        "couverture_url": cover("9781491912058"),
    },
    {
        "titre": "Practical Statistics for Data Scientists",
        "auteur": "Peter Bruce & Andrew Bruce",
        "isbn": "9781492072942",
        "editeur": "O'Reilly",
        "annee_publication": 2020,
        "langue": "en",
        "nombre_pages": 368,
        "categorie": "Data Science",
        "quantite_totale": 4,
        "description": "Les concepts statistiques essentiels présentés de façon pragmatique pour les data scientists. Tests d'hypothèses, régression, classification, et bootstrapping expliqués avec R et Python.",
        "couverture_url": cover("9781492072942"),
    },
    {
        "titre": "Data Science from Scratch",
        "auteur": "Joel Grus",
        "isbn": "9781492041139",
        "editeur": "O'Reilly",
        "annee_publication": 2019,
        "langue": "en",
        "nombre_pages": 406,
        "categorie": "Data Science",
        "quantite_totale": 4,
        "description": "Implémentez les algorithmes de Data Science from scratch en Python pur, sans bibliothèques. Apprenez les fondamentaux de l'algèbre linéaire, des statistiques, du machine learning et du NLP en construisant tout vous-même.",
        "couverture_url": cover("9781492041139"),
    },
    {
        "titre": "Storytelling with Data",
        "auteur": "Cole Nussbaumer Knaflic",
        "isbn": "9781119002253",
        "editeur": "Wiley",
        "annee_publication": 2015,
        "langue": "en",
        "nombre_pages": 288,
        "categorie": "Data Science",
        "quantite_totale": 4,
        "description": "Apprenez à créer des visualisations de données percutantes et à raconter des histoires avec vos données. Les principes de perception visuelle et de communication appliqués à la Data Science.",
        "couverture_url": cover("9781119002253"),
    },
    {
        "titre": "Introduction to Statistical Learning",
        "auteur": "Gareth James & Trevor Hastie",
        "isbn": "9781461471370",
        "editeur": "Springer",
        "annee_publication": 2021,
        "langue": "en",
        "nombre_pages": 426,
        "categorie": "Data Science",
        "quantite_totale": 3,
        "description": "Le livre de référence pour l'apprentissage statistique appliqué. Régression, classification, SVM, arbres de décision, et méthodes non supervisées, avec des labs en R. Version accessible des 'Elements of Statistical Learning'.",
        "couverture_url": cover("9781461471370"),
    },
    {
        "titre": "Feature Engineering for Machine Learning",
        "auteur": "Alice Zheng & Amanda Casari",
        "isbn": "9781491953235",
        "editeur": "O'Reilly",
        "annee_publication": 2018,
        "langue": "en",
        "nombre_pages": 218,
        "categorie": "Data Science",
        "quantite_totale": 3,
        "description": "Maîtrisez l'art de la création et sélection de variables pour le machine learning. Encodage, binning, normalisation, transformation de texte et d'images — les techniques qui font la différence dans vos modèles.",
        "couverture_url": cover("9781491953235"),
    },

    # ══════════════════════════════════════════════════════════════
    # Intelligence Artificielle
    # ══════════════════════════════════════════════════════════════
    {
        "titre": "Hands-On Machine Learning",
        "auteur": "Aurélien Géron",
        "isbn": "9781492032649",
        "editeur": "O'Reilly",
        "annee_publication": 2019,
        "langue": "en",
        "nombre_pages": 856,
        "categorie": "Intelligence Artificielle",
        "quantite_totale": 5,
        "description": "Le guide pratique par excellence pour le Machine Learning et le Deep Learning avec Scikit-Learn, Keras et TensorFlow. Des réseaux de neurones aux transformers, en passant par les SVM et les forêts aléatoires.",
        "couverture_url": cover("9781492032649"),
    },
    {
        "titre": "Deep Learning",
        "auteur": "Ian Goodfellow, Yoshua Bengio & Aaron Courville",
        "isbn": "9780262035613",
        "editeur": "MIT Press",
        "annee_publication": 2016,
        "langue": "en",
        "nombre_pages": 800,
        "categorie": "Intelligence Artificielle",
        "quantite_totale": 3,
        "description": "La référence académique du Deep Learning par ses pionniers. Couvre les fondements mathématiques, les réseaux convolutifs, récurrents, les autoencodeurs et les GANs. Incontournable pour comprendre les bases théoriques.",
        "couverture_url": cover("9780262035613"),
    },
    {
        "titre": "Deep Learning with Python",
        "auteur": "François Chollet",
        "isbn": "9781617294433",
        "editeur": "Manning",
        "annee_publication": 2021,
        "langue": "en",
        "nombre_pages": 504,
        "categorie": "Intelligence Artificielle",
        "quantite_totale": 4,
        "description": "Créé par l'auteur de Keras, ce livre enseigne le Deep Learning de façon intuitive et pratique. CNNs, RNNs, attention, transformers et techniques avancées, avec des exemples concrets en Python.",
        "couverture_url": cover("9781617294433"),
    },
    {
        "titre": "AI: A Modern Approach",
        "auteur": "Stuart Russell & Peter Norvig",
        "isbn": "9780134610993",
        "editeur": "Pearson",
        "annee_publication": 2020,
        "langue": "en",
        "nombre_pages": 1132,
        "categorie": "Intelligence Artificielle",
        "quantite_totale": 4,
        "description": "La bible de l'Intelligence Artificielle, utilisée dans des centaines d'universités. Couvre la recherche, la représentation des connaissances, la planification, l'apprentissage automatique et la robotique.",
        "couverture_url": cover("9780134610993"),
    },
    {
        "titre": "Natural Language Processing with Transformers",
        "auteur": "Lewis Tunstall & Leandro von Werra",
        "isbn": "9781098103248",
        "editeur": "O'Reilly",
        "annee_publication": 2022,
        "langue": "en",
        "nombre_pages": 406,
        "categorie": "Intelligence Artificielle",
        "quantite_totale": 4,
        "description": "Maîtrisez les transformers (BERT, GPT, T5) avec la librairie Hugging Face. Classification de texte, reconnaissance d'entités, question-answering, génération de texte et traduction — avec du code PyTorch.",
        "couverture_url": cover("9781098103248"),
    },
    {
        "titre": "Reinforcement Learning",
        "auteur": "Richard Sutton & Andrew Barto",
        "isbn": "9780262039246",
        "editeur": "MIT Press",
        "annee_publication": 2018,
        "langue": "en",
        "nombre_pages": 552,
        "categorie": "Intelligence Artificielle",
        "quantite_totale": 2,
        "description": "La référence incontournable sur l'apprentissage par renforcement. Q-Learning, policy gradient, Actor-Critic et algorithmes modernes. Fondement théorique pour comprendre AlphaGo, ChatGPT et les agents autonomes.",
        "couverture_url": cover("9780262039246"),
    },
    {
        "titre": "Building Machine Learning Pipelines",
        "auteur": "Hannes Hapke & Catherine Nelson",
        "isbn": "9781492053194",
        "editeur": "O'Reilly",
        "annee_publication": 2020,
        "langue": "en",
        "nombre_pages": 392,
        "categorie": "Intelligence Artificielle",
        "quantite_totale": 3,
        "description": "Construisez des pipelines ML de production avec TensorFlow Extended (TFX). Ingestion, validation, transformation, entraînement, évaluation et déploiement continu des modèles de machine learning.",
        "couverture_url": cover("9781492053194"),
    },

    # ══════════════════════════════════════════════════════════════
    # Informatique (Python & Dev)
    # ══════════════════════════════════════════════════════════════
    {
        "titre": "Fluent Python",
        "auteur": "Luciano Ramalho",
        "isbn": "9781492056355",
        "editeur": "O'Reilly",
        "annee_publication": 2022,
        "langue": "en",
        "nombre_pages": 1012,
        "categorie": "Informatique",
        "quantite_totale": 4,
        "description": "Maîtrisez les idiomes Pythoniques avancés. Décorateurs, générateurs, métaclasses, protocoles, typage et asyncio — tout pour écrire un code Python élégant, performant et maintenable.",
        "couverture_url": cover("9781492056355"),
    },
    {
        "titre": "Effective Python",
        "auteur": "Brett Slatkin",
        "isbn": "9780134853987",
        "editeur": "Addison-Wesley",
        "annee_publication": 2019,
        "langue": "en",
        "nombre_pages": 448,
        "categorie": "Informatique",
        "quantite_totale": 3,
        "description": "90 façons concrètes d'écrire un meilleur code Python. Chaque item présente un problème commun et sa solution pythonique optimale, avec des conseils sur les performances, la concurrence et la maintenabilité.",
        "couverture_url": cover("9780134853987"),
    },
    {
        "titre": "Python Crash Course",
        "auteur": "Eric Matthes",
        "isbn": "9781593279288",
        "editeur": "No Starch Press",
        "annee_publication": 2019,
        "langue": "en",
        "nombre_pages": 544,
        "categorie": "Informatique",
        "quantite_totale": 5,
        "description": "Le meilleur livre pour apprendre Python rapidement. Bases du langage, projets pratiques (jeu, visualisation de données, application web Django). Idéal pour les débutants qui veulent progresser vite.",
        "couverture_url": cover("9781593279288"),
    },
    {
        "titre": "Clean Code",
        "auteur": "Robert C. Martin",
        "isbn": "9780132350884",
        "editeur": "Prentice Hall",
        "annee_publication": 2008,
        "langue": "en",
        "nombre_pages": 431,
        "categorie": "Informatique",
        "quantite_totale": 4,
        "description": "Le livre fondamental sur l'écriture de code propre et maintenable. Nommage, fonctions, commentaires, tests et refactoring. Une lecture obligatoire pour tout développeur soucieux de la qualité de son code.",
        "couverture_url": cover("9780132350884"),
    },
    {
        "titre": "The Pragmatic Programmer",
        "auteur": "David Thomas & Andrew Hunt",
        "isbn": "9780135957059",
        "editeur": "Addison-Wesley",
        "annee_publication": 2019,
        "langue": "en",
        "nombre_pages": 352,
        "categorie": "Informatique",
        "quantite_totale": 3,
        "description": "Un classique mis à jour sur le métier de développeur pragmatique. DRY, orthogonalité, prototypes, automatisation et gestion de carrière — les principes intemporels du bon développement logiciel.",
        "couverture_url": cover("9780135957059"),
    },
    {
        "titre": "Cracking the Coding Interview",
        "auteur": "Gayle Laakmann McDowell",
        "isbn": "9780984782857",
        "editeur": "CareerCup",
        "annee_publication": 2015,
        "langue": "en",
        "nombre_pages": 696,
        "categorie": "Informatique",
        "quantite_totale": 5,
        "description": "189 questions d'entretiens de programmation avec solutions détaillées. Structures de données, algorithmes, conception système et conseils comportementaux pour réussir les entretiens chez les grandes entreprises tech.",
        "couverture_url": cover("9780984782857"),
    },
    {
        "titre": "Introduction to Algorithms",
        "auteur": "Thomas Cormen & al.",
        "isbn": "9780262046305",
        "editeur": "MIT Press",
        "annee_publication": 2022,
        "langue": "en",
        "nombre_pages": 1312,
        "categorie": "Informatique",
        "quantite_totale": 5,
        "description": "La référence mondiale des algorithmes (CLRS), 4ème édition. Tri, graphes, arbres, programmation dynamique, algorithmes d'approximation — une analyse rigoureuse des complexités et des preuves de correction.",
        "couverture_url": cover("9780262046305"),
    },

    # ══════════════════════════════════════════════════════════════
    # Mathématiques
    # ══════════════════════════════════════════════════════════════
    {
        "titre": "Mathematics for Machine Learning",
        "auteur": "Marc Peter Deisenroth & al.",
        "isbn": "9781108455145",
        "editeur": "Cambridge University Press",
        "annee_publication": 2020,
        "langue": "en",
        "nombre_pages": 398,
        "categorie": "Mathématiques",
        "quantite_totale": 4,
        "description": "Les fondements mathématiques nécessaires pour le machine learning. Algèbre linéaire, calcul, statistiques et probabilités, expliqués dans le contexte des algorithmes d'apprentissage automatique.",
        "couverture_url": cover("9781108455145"),
    },
    {
        "titre": "Linear Algebra Done Right",
        "auteur": "Sheldon Axler",
        "isbn": "9783319110790",
        "editeur": "Springer",
        "annee_publication": 2015,
        "langue": "en",
        "nombre_pages": 340,
        "categorie": "Mathématiques",
        "quantite_totale": 3,
        "description": "Une approche élégante et moderne de l'algèbre linéaire, axée sur les espaces vectoriels plutôt que sur les matrices. Approche conceptuelle rigoureuse, idéale pour les étudiants en mathématiques et en IA.",
        "couverture_url": cover("9783319110790"),
    },
    {
        "titre": "Probability Theory: The Logic of Science",
        "auteur": "E.T. Jaynes",
        "isbn": "9780521592710",
        "editeur": "Cambridge University Press",
        "annee_publication": 2003,
        "langue": "en",
        "nombre_pages": 727,
        "categorie": "Mathématiques",
        "quantite_totale": 3,
        "description": "Une vision bayésienne de la théorie des probabilités. Jaynes montre que la probabilité est une extension de la logique pour raisonner sous incertitude, avec des applications en physique, statistiques et IA.",
        "couverture_url": cover("9780521592710"),
    },
    {
        "titre": "Convex Optimization",
        "auteur": "Stephen Boyd & Lieven Vandenberghe",
        "isbn": "9780521833783",
        "editeur": "Cambridge University Press",
        "annee_publication": 2004,
        "langue": "en",
        "nombre_pages": 716,
        "categorie": "Mathématiques",
        "quantite_totale": 2,
        "description": "La référence sur l'optimisation convexe, fondement de nombreux algorithmes de machine learning. Théorie duale, méthodes de descente de gradient, SVM et applications en statistiques et ingénierie.",
        "couverture_url": cover("9780521833783"),
    },

    # ══════════════════════════════════════════════════════════════
    # Sciences
    # ══════════════════════════════════════════════════════════════
    {
        "titre": "A Brief History of Time",
        "auteur": "Stephen Hawking",
        "isbn": "9780553380163",
        "editeur": "Bantam Books",
        "annee_publication": 1998,
        "langue": "en",
        "nombre_pages": 212,
        "categorie": "Sciences",
        "quantite_totale": 3,
        "description": "Le livre de vulgarisation scientifique le plus vendu au monde. Stephen Hawking explique l'origine de l'univers, les trous noirs, le temps et la théorie du tout — avec une clarté et un humour remarquables.",
        "couverture_url": cover("9780553380163"),
    },
    {
        "titre": "The Selfish Gene",
        "auteur": "Richard Dawkins",
        "isbn": "9780198788607",
        "editeur": "Oxford University Press",
        "annee_publication": 2016,
        "langue": "en",
        "nombre_pages": 544,
        "categorie": "Sciences",
        "quantite_totale": 2,
        "description": "Un livre révolutionnaire qui explique l'évolution du point de vue du gène. Dawkins introduit le concept de mème et montre comment la sélection naturelle opère au niveau moléculaire.",
        "couverture_url": cover("9780198788607"),
    },
    {
        "titre": "University Physics",
        "auteur": "Hugh Young & Roger Freedman",
        "isbn": "9780321982582",
        "editeur": "Pearson",
        "annee_publication": 2015,
        "langue": "en",
        "nombre_pages": 1600,
        "categorie": "Sciences",
        "quantite_totale": 3,
        "description": "Le manuel de référence en physique universitaire. Mécanique classique, thermodynamique, électromagnétisme, optique et physique moderne — avec des centaines d'exercices corrigés.",
        "couverture_url": cover("9780321982582"),
    },

    # ══════════════════════════════════════════════════════════════
    # Littérature
    # ══════════════════════════════════════════════════════════════
    {
        "titre": "1984",
        "auteur": "George Orwell",
        "isbn": "9780451524935",
        "editeur": "Signet Classic",
        "annee_publication": 1949,
        "langue": "en",
        "nombre_pages": 328,
        "categorie": "Littérature",
        "quantite_totale": 4,
        "description": "Le roman dystopique emblématique d'Orwell. Dans un futur totalitaire, Winston Smith tente de résister au régime du Parti et de Big Brother. Une réflexion profonde sur la liberté, la vérité et le pouvoir.",
        "couverture_url": cover("9780451524935"),
    },
    {
        "titre": "Brave New World",
        "auteur": "Aldous Huxley",
        "isbn": "9780060850524",
        "editeur": "Harper Perennial",
        "annee_publication": 1932,
        "langue": "en",
        "nombre_pages": 311,
        "categorie": "Littérature",
        "quantite_totale": 3,
        "description": "Un monde futuriste où le bonheur est fabriqué par la science et le conditionnement. Huxley dépeint une dystopie de confort absolu où liberté et humanité ont été sacrifiées. Un contrepoint fascinant à 1984.",
        "couverture_url": cover("9780060850524"),
    },
    {
        "titre": "The Alchemist",
        "auteur": "Paulo Coelho",
        "isbn": "9780062315007",
        "editeur": "HarperOne",
        "annee_publication": 1988,
        "langue": "en",
        "nombre_pages": 208,
        "categorie": "Littérature",
        "quantite_totale": 4,
        "description": "Le roman le plus vendu au monde, traduit en 80 langues. Santiago, jeune berger andalou, suit son rêve jusqu'aux pyramides d'Égypte. Une fable universelle sur l'écoute de son destin personnel.",
        "couverture_url": cover("9780062315007"),
    },
    {
        "titre": "Things Fall Apart",
        "auteur": "Chinua Achebe",
        "isbn": "9780385474542",
        "editeur": "Anchor Books",
        "annee_publication": 1958,
        "langue": "en",
        "nombre_pages": 209,
        "categorie": "Littérature",
        "quantite_totale": 3,
        "description": "Le roman africain le plus lu au monde. Okonkwo, guerrier igbo au Nigeria, voit son monde s'effondrer avec l'arrivée des colonisateurs. Un chef-d'œuvre sur la dignité, la tradition et le choc des civilisations.",
        "couverture_url": cover("9780385474542"),
    },
    {
        "titre": "Atomic Habits",
        "auteur": "James Clear",
        "isbn": "9780735211292",
        "editeur": "Avery",
        "annee_publication": 2018,
        "langue": "en",
        "nombre_pages": 320,
        "categorie": "Littérature",
        "quantite_totale": 5,
        "description": "Un guide pratique pour construire de bonnes habitudes et éliminer les mauvaises. James Clear explique comment de minuscules changements quotidiens génèrent des résultats remarquables à long terme.",
        "couverture_url": cover("9780735211292"),
    },
]


# ════════════════════════════════════════════════════════════
# Logique de seed
# ════════════════════════════════════════════════════════════

async def reset_db() -> None:
    await Livre.alter().drop_table(if_exists=True).run()
    await Categorie.alter().drop_table(if_exists=True).run()
    await Categorie.create_table(if_not_exists=True).run()
    await Livre.create_table(if_not_exists=True).run()
    print("✓ Tables recréées.\n")


async def seed_categories() -> dict[str, UUID]:
    print("── Catégories ──────────────────────────")
    categories: dict[str, UUID] = {}
    for data in CATEGORIES:
        existing = await Categorie.objects().where(Categorie.nom == data["nom"]).first()
        if existing:
            categories[existing.nom] = existing.id
            print(f"  ↩ Existe déjà : {existing.nom}")
        else:
            cat = Categorie(nom=data["nom"], description=data["description"])
            await cat.save().run()
            categories[cat.nom] = cat.id
            print(f"  ✓ Créée       : {cat.nom}")
    return categories


async def seed_livres(categories: dict[str, UUID]) -> tuple[int, int, int]:
    print("\n── Livres ──────────────────────────────")
    crees = existants = erreurs = 0
    for data in LIVRES:
        livre_data: dict[str, Any] = dict(data)
        nom_cat = cast(str, livre_data.pop("categorie"))
        cat_id = categories.get(nom_cat)
        try:
            existing = await Livre.objects().where(Livre.isbn == livre_data["isbn"]).first()
            if existing:
                existants += 1
                print(f"  ↩ Existe déjà : {existing.titre}")
                continue
            livre = Livre(**livre_data, categorie=cat_id, actif=True)
            await livre.save().run()
            crees += 1
            print(f"  ✓ Créé        : {livre.titre}")
        except Exception as exc:
            erreurs += 1
            print(f"  ✗ Erreur sur '{livre_data.get('titre', '?')}' : {exc}")
    return crees, existants, erreurs


async def run() -> None:
    if "--reset" in sys.argv:
        confirm = input("⚠️  Supprimer tous les livres et catégories ? (oui/non) : ")
        if confirm.strip().lower() == "oui":
            await reset_db()
        else:
            print("Annulé.")
            return

    categories = await seed_categories()
    crees, existants, erreurs = await seed_livres(categories)

    nb_cats = await Categorie.count().run()
    nb_livres = await Livre.count().run()

    print(f"""
╔══════════════════════════════════════════╗
║         Seed terminé avec succès         ║
╠══════════════════════════════════════════╣
║  Catégories en base : {nb_cats:<20}║
║  Livres créés       : {crees:<20}║
║  Déjà existants     : {existants:<20}║
║  Erreurs            : {erreurs:<20}║
║  Total livres en DB : {nb_livres:<20}║
╚══════════════════════════════════════════╝
    """)

    if erreurs:
        print("⚠️  Des erreurs ont eu lieu. Relancez avec --reset pour repartir de zéro.")


if __name__ == "__main__":
    asyncio.run(run())
