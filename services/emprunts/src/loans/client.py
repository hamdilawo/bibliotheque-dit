"""
Client HTTP pour communiquer avec les autres microservices.
Gère les appels vers : Service Livres et Service Utilisateurs.
"""
import requests
from django.conf import settings


class ServiceException(Exception):
    """Exception levée lors d'une erreur de communication inter-services."""

    def __init__(self, message, status_code=None):
        self.status_code = status_code
        super().__init__(message)


class LivresClient:
    """Client pour le Service Livres."""

    BASE_URL = None

    @classmethod
    def get_base_url(cls):
        if cls.BASE_URL is None:
            cls.BASE_URL = settings.SERVICE_LIVRES_URL
        return cls.BASE_URL

    @classmethod
    # get_livre_by_id --- IGNORE ---
    def get_livre(cls, livre_id: int) -> dict:
        """Récupère les infos d'un livre."""
        try:
            url = f"{cls.get_base_url()}/api/livres/{livre_id}/"
            response = requests.get(url, timeout=5)
            if response.status_code == 404:
                raise ServiceException(f"Livre #{livre_id} introuvable.", 404)
            response.raise_for_status()
            return response.json()
        except requests.ConnectionError:
            raise ServiceException("Service Livres indisponible.", 503)
        except requests.Timeout:
            raise ServiceException("Service Livres trop lent.", 504)

    @classmethod
    def reserver_livre(cls, livre_id: int) -> dict:
        """Décrémente la disponibilité du livre."""
        try:
            url = f"{cls.get_base_url()}/api/livres/{livre_id}/disponibilite/"
            response = requests.post(
                url, json={'action': 'reserver'}, timeout=5)
            if response.status_code == 400:
                raise ServiceException(response.json().get(
                    'error', 'Livre indisponible.'), 400)
            response.raise_for_status()
            return response.json()
        except requests.ConnectionError:
            raise ServiceException("Service Livres indisponible.", 503)

    @classmethod
    def retourner_livre(cls, livre_id: int) -> dict:
        """Incrémente la disponibilité du livre."""
        try:
            url = f"{cls.get_base_url()}/api/livres/{livre_id}/disponibilite/"
            response = requests.post(
                url, json={'action': 'retourner'}, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.ConnectionError:
            raise ServiceException("Service Livres indisponible.", 503)


class UtilisateursClient:
    """Client pour le Service Utilisateurs."""

    BASE_URL = None

    @classmethod
    def get_base_url(cls):
        if cls.BASE_URL is None:
            cls.BASE_URL = settings.SERVICE_UTILISATEURS_URL
        return cls.BASE_URL

    @classmethod
    def get_utilisateur(cls, utilisateur_id: int) -> dict:
        """Récupère le profil public d'un utilisateur."""
        try:
            url = f"{cls.get_base_url()}/api/utilisateurs/{utilisateur_id}/profil_public/"
            response = requests.get(url, timeout=5)
            if response.status_code == 404:
                raise ServiceException(
                    f"Utilisateur #{utilisateur_id} introuvable.", 404)
            response.raise_for_status()
            return response.json()
        except requests.ConnectionError:
            raise ServiceException("Service Utilisateurs indisponible.", 503)
        except requests.Timeout:
            raise ServiceException("Service Utilisateurs trop lent.", 504)

    @classmethod
    def incrementer_emprunts(cls, utilisateur_id: int) -> dict:
        """Incrémente le compteur d'emprunts de l'utilisateur."""
        try:
            url = f"{cls.get_base_url()}/api/utilisateurs/{utilisateur_id}/sync_emprunts/"
            response = requests.post(
                url, json={'action': 'incrementer'}, timeout=5)
            if response.status_code == 400:
                raise ServiceException(response.json().get(
                    'error', 'Quota dépassé.'), 400)
            response.raise_for_status()
            return response.json()
        except requests.ConnectionError:
            raise ServiceException("Service Utilisateurs indisponible.", 503)

    @classmethod
    def decrementer_emprunts(cls, utilisateur_id: int) -> dict:
        """Décrémente le compteur d'emprunts de l'utilisateur."""
        try:
            url = f"{cls.get_base_url()}/api/utilisateurs/{utilisateur_id}/sync_emprunts/"
            response = requests.post(
                url, json={'action': 'decrementer'}, timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.ConnectionError:
            raise ServiceException("Service Utilisateurs indisponible.", 503)
