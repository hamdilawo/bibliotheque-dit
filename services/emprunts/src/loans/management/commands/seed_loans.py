"""
Seed loans for ML model training.

Usage (on server):
    docker exec loans-api python manage.py seed_loans
    docker exec loans-api python manage.py seed_loans --reset
"""
import uuid
import random
import requests
from datetime import date, timedelta

from django.core.management.base import BaseCommand

from loans.adapters.database.models.emprunt import Emprunt

LIVRES_URL = "http://book-api:8001"
USERS_URL  = "http://utilisateurs:8002"

FAKE_USERS = [
    {"id": str(uuid.uuid4()), "nom": "Mamadou Diallo",   "email": "mdiallo@dit.sn",   "role": "STUDENT"},
    {"id": str(uuid.uuid4()), "nom": "Fatou Sow",        "email": "fsow@dit.sn",       "role": "STUDENT"},
    {"id": str(uuid.uuid4()), "nom": "Ibrahima Ba",      "email": "iba@dit.sn",         "role": "STUDENT"},
    {"id": str(uuid.uuid4()), "nom": "Aissatou Diop",    "email": "adiop@dit.sn",      "role": "PROFESSOR"},
    {"id": str(uuid.uuid4()), "nom": "Moussa Ndiaye",    "email": "mndiaye@dit.sn",    "role": "STUDENT"},
    {"id": str(uuid.uuid4()), "nom": "Mariama Balde",    "email": "mbalde@dit.sn",     "role": "STUDENT"},
    {"id": str(uuid.uuid4()), "nom": "Ousmane Thiam",    "email": "othiam@dit.sn",     "role": "STUDENT"},
    {"id": str(uuid.uuid4()), "nom": "Rokhaya Fall",     "email": "rfall@dit.sn",      "role": "PROFESSOR"},
    {"id": str(uuid.uuid4()), "nom": "Cheikh Sarr",      "email": "csarr@dit.sn",      "role": "STUDENT"},
    {"id": str(uuid.uuid4()), "nom": "Aminata Camara",   "email": "acamara@dit.sn",    "role": "STUDENT"},
]

# Loan patterns per user profile — index into books list by genre preference
PROFILES = {
    "STUDENT":   {"n_loans": (5, 12), "rating_range": (3, 5)},
    "PROFESSOR": {"n_loans": (8, 15), "rating_range": (4, 5)},
}


class Command(BaseCommand):
    help = "Seed realistic loan history for ML recommendation training"

    def add_arguments(self, parser):
        parser.add_argument("--reset", action="store_true", help="Delete all existing loans first")
        parser.add_argument("--users", type=int, default=10, help="Number of fake users (max 10)")

    def handle(self, *args, **options):
        if options["reset"]:
            count = Emprunt.objects.count()
            Emprunt.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Supprimé {count} emprunts existants."))

        # Fetch real books from livres service
        books = self._fetch_books()
        if not books:
            self.stdout.write(self.style.ERROR("Impossible de récupérer les livres. Service livres démarré ?"))
            return
        self.stdout.write(f"  {len(books)} livres récupérés.")

        # Try to get real users, fall back to fake ones
        users = self._fetch_real_users() or FAKE_USERS[: options["users"]]
        self.stdout.write(f"  {len(users)} utilisateurs.")

        created = 0
        today = date.today()

        for user in users:
            profile = PROFILES.get(user.get("role", "STUDENT"), PROFILES["STUDENT"])
            n = random.randint(*profile["n_loans"])
            chosen_books = random.sample(books, min(n, len(books)))

            for i, book in enumerate(chosen_books):
                borrow_date = today - timedelta(days=random.randint(30, 365))
                due_date    = borrow_date + timedelta(days=14)
                returned    = random.random() > 0.15  # 85% des livres rendus
                ret_date    = None
                jours_retard = 0
                statut = "approved"

                if returned:
                    ret_offset = random.randint(-3, 5)
                    ret_date   = due_date + timedelta(days=ret_offset)
                    jours_retard = max(0, ret_offset)
                    statut = "completed"

                rating = random.randint(*profile["rating_range"]) if returned else None

                Emprunt.objects.create(
                    id=uuid.uuid4(),
                    utilisateur_id=user["id"],
                    utilisateur_nom=user["nom"],
                    utilisateur_email=user.get("email", ""),
                    livre_id=book["id"],
                    livre_titre=book["titre"],
                    livre_auteur=book["auteur"],
                    livre_isbn=book.get("isbn", ""),
                    date_retour_prevue=due_date,
                    date_retour_effective=ret_date,
                    statut=statut,
                    jours_retard=jours_retard,
                    rating=rating,
                )
                created += 1

        self.stdout.write(self.style.SUCCESS(
            f"\n{created} emprunts créés pour {len(users)} utilisateurs sur {len(books)} livres."
        ))
        self.stdout.write(self.style.SUCCESS(
            "Lance maintenant : curl -X POST http://localhost:8004/train"
        ))

    def _fetch_books(self):
        try:
            resp = requests.get(f"{LIVRES_URL}/api/livres?page_size=100", timeout=10)
            resp.raise_for_status()
            return resp.json().get("results", [])
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Livres service : {e}"))
            return []

    def _fetch_real_users(self):
        try:
            resp = requests.get(f"{USERS_URL}/api/users/", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                results = data if isinstance(data, list) else data.get("results", [])
                users = []
                for u in results:
                    users.append({
                        "id": str(u.get("id", "")),
                        "nom": u.get("full_name") or f"{u.get('first_name','')} {u.get('last_name','')}".strip(),
                        "email": u.get("email", ""),
                        "role": u.get("role", "STUDENT"),
                    })
                return users if users else None
        except Exception:
            pass
        return None
