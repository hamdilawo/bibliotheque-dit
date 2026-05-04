"""
Script de peuplement initial — Service Livres (Piccolo ORM)

Usage :
    python seed.py           # Peuple sans supprimer les données existantes
    python seed.py --reset   # Supprime tout et repart de zéro
"""
from __future__ import annotations

import asyncio
import os
import sys

# ── Configuration DB directe ─────────────────────────────────
from piccolo.engine.postgres import PostgresEngine
DB = PostgresEngine(config={
    "host":     os.getenv("DB_HOST", "db"),
    "port":     int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "livres_db"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres"),
})

from features.books.tables import Categorie, Livre


# ════════════════════════════════════════════════════════════
# Données de référence
# ════════════════════════════════════════════════════════════

CATEGORIES = [
    {"nom": "Informatique",             "description": "Programmation, algorithmes, réseaux, IA"},
    {"nom": "Mathématiques",            "description": "Algèbre, analyse, probabilités, statistiques"},
    {"nom": "Intelligence Artificielle","description": "Machine Learning, Deep Learning, NLP"},
    {"nom": "Sciences",                 "description": "Physique, chimie, biologie"},
    {"nom": "Littérature",              "description": "Romans, nouvelles, poésie"},
]

LIVRES = [
    # ── Intelligence Artificielle ─────────────────────────────
    {"titre": "Introduction à l'IA",          "auteur": "Stuart Russell",      "isbn": "9782744005084", "editeur": "Pearson",         "annee_publication": 2022, "langue": "fr", "categorie": "Intelligence Artificielle", "quantite_totale": 5},
    {"titre": "Deep Learning",                 "auteur": "Ian Goodfellow",      "isbn": "9782100780730", "editeur": "MIT Press",        "annee_publication": 2016, "langue": "fr", "categorie": "Intelligence Artificielle", "quantite_totale": 3},
    {"titre": "NLP with Python",               "auteur": "Steven Bird",         "isbn": "9780596516499", "editeur": "O'Reilly",         "annee_publication": 2009, "langue": "en", "categorie": "Intelligence Artificielle", "quantite_totale": 2},
    {"titre": "Pattern Recognition and ML",    "auteur": "Christopher Bishop",  "isbn": "9780387310732", "editeur": "Springer",         "annee_publication": 2006, "langue": "en", "categorie": "Intelligence Artificielle", "quantite_totale": 2},
    {"titre": "Hands-On Machine Learning",     "auteur": "Aurélien Géron",      "isbn": "9781492032649", "editeur": "O'Reilly",         "annee_publication": 2019, "langue": "en", "categorie": "Intelligence Artificielle", "quantite_totale": 4},
    {"titre": "Reinforcement Learning",        "auteur": "Richard Sutton",      "isbn": "9780262039246", "editeur": "MIT Press",        "annee_publication": 2018, "langue": "en", "categorie": "Intelligence Artificielle", "quantite_totale": 2},
    {"titre": "Speech and Language Processing","auteur": "Daniel Jurafsky",     "isbn": "9780131873216", "editeur": "Pearson",          "annee_publication": 2008, "langue": "en", "categorie": "Intelligence Artificielle", "quantite_totale": 2},
    {"titre": "Computer Vision",               "auteur": "Richard Szeliski",    "isbn": "9783030343712", "editeur": "Springer",         "annee_publication": 2022, "langue": "en", "categorie": "Intelligence Artificielle", "quantite_totale": 2},
    {"titre": "Deep Learning with Python",     "auteur": "François Chollet",    "isbn": "9781617294433", "editeur": "Manning",          "annee_publication": 2017, "langue": "en", "categorie": "Intelligence Artificielle", "quantite_totale": 3},
    {"titre": "Probabilistic Machine Learning","auteur": "Kevin Murphy",        "isbn": "9780262046824", "editeur": "MIT Press",        "annee_publication": 2022, "langue": "en", "categorie": "Intelligence Artificielle", "quantite_totale": 2},
    {"titre": "AI: A Modern Approach",         "auteur": "Peter Norvig",        "isbn": "9780134610993", "editeur": "Pearson",          "annee_publication": 2020, "langue": "en", "categorie": "Intelligence Artificielle", "quantite_totale": 4},
    {"titre": "L'IA expliquée",                "auteur": "Luc Julia",           "isbn": "9782845639300", "editeur": "First",            "annee_publication": 2019, "langue": "fr", "categorie": "Intelligence Artificielle", "quantite_totale": 3},
    {"titre": "GANs in Action",                "auteur": "Jakub Langr",         "isbn": "9781617295560", "editeur": "Manning",          "annee_publication": 2019, "langue": "en", "categorie": "Intelligence Artificielle", "quantite_totale": 1},
    {"titre": "Transformers for NLP",          "auteur": "Denis Rothman",       "isbn": "9781800565791", "editeur": "Packt",            "annee_publication": 2021, "langue": "en", "categorie": "Intelligence Artificielle", "quantite_totale": 2},
    {"titre": "Apprentissage Automatique",     "auteur": "Massih-Reza Amini",   "isbn": "9782212679090", "editeur": "Eyrolles",         "annee_publication": 2020, "langue": "fr", "categorie": "Intelligence Artificielle", "quantite_totale": 2},

    # ── Informatique ──────────────────────────────────────────
    {"titre": "Python pour la Data Science",   "auteur": "Jake VanderPlas",     "isbn": "9782100790319", "editeur": "O'Reilly",         "annee_publication": 2020, "langue": "fr", "categorie": "Informatique", "quantite_totale": 4},
    {"titre": "Algorithmes",                   "auteur": "Thomas Cormen",       "isbn": "9782100767717", "editeur": "Dunod",            "annee_publication": 2019, "langue": "fr", "categorie": "Informatique", "quantite_totale": 6},
    {"titre": "Clean Code",                    "auteur": "Robert C. Martin",    "isbn": "9780132350884", "editeur": "Prentice Hall",    "annee_publication": 2008, "langue": "en", "categorie": "Informatique", "quantite_totale": 3},
    {"titre": "The Pragmatic Programmer",      "auteur": "David Thomas",        "isbn": "9780135957059", "editeur": "Addison-Wesley",   "annee_publication": 2019, "langue": "en", "categorie": "Informatique", "quantite_totale": 3},
    {"titre": "Design Patterns",               "auteur": "Erich Gamma",         "isbn": "9780201633610", "editeur": "Addison-Wesley",   "annee_publication": 1994, "langue": "en", "categorie": "Informatique", "quantite_totale": 2},
    {"titre": "Refactoring",                   "auteur": "Martin Fowler",       "isbn": "9780134757599", "editeur": "Addison-Wesley",   "annee_publication": 2018, "langue": "en", "categorie": "Informatique", "quantite_totale": 2},
    {"titre": "Effective Python",              "auteur": "Brett Slatkin",       "isbn": "9780134853987", "editeur": "Addison-Wesley",   "annee_publication": 2019, "langue": "en", "categorie": "Informatique", "quantite_totale": 2},
    {"titre": "Designing Data-Intensive Apps", "auteur": "Martin Kleppmann",    "isbn": "9781449373320", "editeur": "O'Reilly",         "annee_publication": 2017, "langue": "en", "categorie": "Informatique", "quantite_totale": 3},
    {"titre": "Java: The Complete Reference",  "auteur": "Herbert Schildt",     "isbn": "9781260440232", "editeur": "McGraw-Hill",      "annee_publication": 2020, "langue": "en", "categorie": "Informatique", "quantite_totale": 2},
    {"titre": "Linux: The Complete Reference", "auteur": "Richard Petersen",    "isbn": "9780071496292", "editeur": "McGraw-Hill",      "annee_publication": 2008, "langue": "en", "categorie": "Informatique", "quantite_totale": 2},
    {"titre": "Computer Networks",             "auteur": "Andrew Tanenbaum",    "isbn": "9780132126953", "editeur": "Pearson",          "annee_publication": 2010, "langue": "en", "categorie": "Informatique", "quantite_totale": 3},
    {"titre": "Operating System Concepts",     "auteur": "Abraham Silberschatz","isbn": "9781119320913", "editeur": "Wiley",            "annee_publication": 2018, "langue": "en", "categorie": "Informatique", "quantite_totale": 2},
    {"titre": "Cracking the Coding Interview", "auteur": "Gayle McDowell",      "isbn": "9780984782857", "editeur": "CareerCup",        "annee_publication": 2015, "langue": "en", "categorie": "Informatique", "quantite_totale": 4},
    {"titre": "You Don't Know JS",             "auteur": "Kyle Simpson",        "isbn": "9781491904244", "editeur": "O'Reilly",         "annee_publication": 2015, "langue": "en", "categorie": "Informatique", "quantite_totale": 2},
    {"titre": "Docker en Pratique",            "auteur": "Pierre-Yves Cloux",   "isbn": "9782100787654", "editeur": "Dunod",            "annee_publication": 2021, "langue": "fr", "categorie": "Informatique", "quantite_totale": 3},

    # ── Mathématiques ─────────────────────────────────────────
    {"titre": "Probabilités et Statistiques",  "auteur": "Paul-Louis Hennequin","isbn": "9782100715671", "editeur": "Dunod",            "annee_publication": 2018, "langue": "fr", "categorie": "Mathématiques", "quantite_totale": 4},
    {"titre": "Algèbre Linéaire",              "auteur": "Joseph Grifone",      "isbn": "9782705681142", "editeur": "Cepadues",         "annee_publication": 2015, "langue": "fr", "categorie": "Mathématiques", "quantite_totale": 3},
    {"titre": "Analyse pour la Licence",       "auteur": "Daniel Fredon",       "isbn": "9782100727216", "editeur": "Dunod",            "annee_publication": 2015, "langue": "fr", "categorie": "Mathématiques", "quantite_totale": 3},
    {"titre": "Mathematics for Machine Learning","auteur": "Marc Deisenroth",   "isbn": "9781108455145", "editeur": "Cambridge",        "annee_publication": 2020, "langue": "en", "categorie": "Mathématiques", "quantite_totale": 3},
    {"titre": "Linear Algebra Done Right",     "auteur": "Sheldon Axler",       "isbn": "9783319110790", "editeur": "Springer",         "annee_publication": 2015, "langue": "en", "categorie": "Mathématiques", "quantite_totale": 2},
    {"titre": "Convex Optimization",           "auteur": "Stephen Boyd",        "isbn": "9780521833783", "editeur": "Cambridge",        "annee_publication": 2004, "langue": "en", "categorie": "Mathématiques", "quantite_totale": 2},
    {"titre": "Calculus",                      "auteur": "Michael Spivak",      "isbn": "9780914098911", "editeur": "Publish or Perish", "annee_publication": 2008, "langue": "en", "categorie": "Mathématiques", "quantite_totale": 2},
    {"titre": "Discrete Mathematics",          "auteur": "Kenneth Rosen",       "isbn": "9780073383095", "editeur": "McGraw-Hill",      "annee_publication": 2018, "langue": "en", "categorie": "Mathématiques", "quantite_totale": 3},
    {"titre": "Théorie des Graphes",           "auteur": "Aimée Lombardi",      "isbn": "9782705694326", "editeur": "Cepadues",         "annee_publication": 2017, "langue": "fr", "categorie": "Mathématiques", "quantite_totale": 2},
    {"titre": "Numerical Recipes",             "auteur": "William Press",       "isbn": "9780521880688", "editeur": "Cambridge",        "annee_publication": 2007, "langue": "en", "categorie": "Mathématiques", "quantite_totale": 2},

    # ── Sciences ──────────────────────────────────────────────
    {"titre": "Physique Générale",             "auteur": "Hugh Young",          "isbn": "9782761332293", "editeur": "Pearson",          "annee_publication": 2014, "langue": "fr", "categorie": "Sciences", "quantite_totale": 3},
    {"titre": "Chimie Organique",              "auteur": "Paula Bruice",        "isbn": "9782761379892", "editeur": "Pearson",          "annee_publication": 2017, "langue": "fr", "categorie": "Sciences", "quantite_totale": 2},
    {"titre": "Biologie Moléculaire",          "auteur": "James Watson",        "isbn": "9782807304277", "editeur": "De Boeck",         "annee_publication": 2018, "langue": "fr", "categorie": "Sciences", "quantite_totale": 2},
    {"titre": "A Brief History of Time",       "auteur": "Stephen Hawking",     "isbn": "9780553380163", "editeur": "Bantam",           "annee_publication": 1998, "langue": "en", "categorie": "Sciences", "quantite_totale": 2},
    {"titre": "The Selfish Gene",              "auteur": "Richard Dawkins",     "isbn": "9780198788607", "editeur": "Oxford",           "annee_publication": 2016, "langue": "en", "categorie": "Sciences", "quantite_totale": 2},

    # ── Littérature ───────────────────────────────────────────
    {"titre": "Les Misérables",                "auteur": "Victor Hugo",         "isbn": "9782070409228", "editeur": "Gallimard",        "annee_publication": 1862, "langue": "fr", "categorie": "Littérature", "quantite_totale": 2},
    {"titre": "Les Soleils des Indépendances", "auteur": "Ahmadou Kourouma",    "isbn": "9782020025348", "editeur": "Seuil",            "annee_publication": 1968, "langue": "fr", "categorie": "Littérature", "quantite_totale": 3},
    {"titre": "Une si longue lettre",          "auteur": "Mariama Bâ",          "isbn": "9782723601658", "editeur": "NEAS",             "annee_publication": 1979, "langue": "fr", "categorie": "Littérature", "quantite_totale": 4},
    {"titre": "L'Aventure ambiguë",            "auteur": "Cheikh Hamidou Kane", "isbn": "9782264025203", "editeur": "10/18",            "annee_publication": 1961, "langue": "fr", "categorie": "Littérature", "quantite_totale": 3},
    {"titre": "1984",                          "auteur": "George Orwell",       "isbn": "9780451524935", "editeur": "Signet",           "annee_publication": 1949, "langue": "en", "categorie": "Littérature", "quantite_totale": 3},
]


# ════════════════════════════════════════════════════════════
# Logique de seed
# ════════════════════════════════════════════════════════════

async def reset_db() -> None:
    """Supprime toutes les données existantes."""
    await Livre.alter().drop_table(if_exists=True).run()
    await Categorie.alter().drop_table(if_exists=True).run()
    await Categorie.create_table(if_not_exists=True).run()
    await Livre.create_table(if_not_exists=True).run()
    print("✓ Tables recréées.\n")


async def seed_categories() -> dict[str, int]:
    """Insère les catégories et retourne un mapping nom → id."""
    print("── Catégories ──────────────────────────")
    categories: dict[str, int] = {}

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


async def seed_livres(categories: dict[str, int]) -> tuple[int, int, int]:
    """Insère les livres. Retourne (créés, existants, erreurs)."""
    print("\n── Livres ──────────────────────────────")
    crees = existants = erreurs = 0

    for data in LIVRES:
        livre_data = dict(data)
        nom_cat = livre_data.pop("categorie")
        cat_id = categories.get(nom_cat)
        quantite = livre_data.get("quantite_totale", 1)

        try:
            existing = await Livre.objects().where(Livre.isbn == livre_data["isbn"]).first()
            if existing:
                existants += 1
                print(f"  ↩ Existe déjà : {existing.titre}")
                continue

            livre = Livre(
                **livre_data,
                categorie=cat_id,
                quantite_disponible=quantite,
                actif=True,
            )
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