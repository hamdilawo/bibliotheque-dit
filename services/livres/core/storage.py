"""
Gestion du stockage des fichiers via MinIO (compatible S3).

Responsabilités :
- Upload d'images de couverture dans le bucket MinIO
- Suppression d'images
- Génération d'URLs publiques

Le client MinIO est initialisé une seule fois (singleton via get_minio_client).
"""
import uuid
import logging
from io import BytesIO

from minio import Minio
from minio.error import S3Error

from core.settings import get_settings

logger = logging.getLogger(__name__)

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE_MB = 5
_client: Minio | None = None


def get_minio_client() -> Minio:
    """Retourne le client MinIO (singleton)."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_use_ssl,
        )
    return _client


def _ensure_bucket(bucket: str) -> None:
    """Crée le bucket s'il n'existe pas (sécurité en cas de minio-init raté)."""
    client = get_minio_client()
    if not client.bucket_exists(bucket):
        client.make_bucket(bucket)
        logger.info(f"Bucket '{bucket}' créé.")


def upload_couverture(file_bytes: bytes, content_type: str) -> str:
    """
    Upload une image de couverture dans MinIO.

    Args:
        file_bytes: contenu binaire de l'image
        content_type: type MIME (image/jpeg, image/png, image/webp)

    Returns:
        token de l'objet (object_name) — stocké dans couverture_url en base

    Raises:
        ValueError: si le type ou la taille est invalide
        S3Error: si MinIO est inaccessible
    """
    if content_type not in ALLOWED_TYPES:
        raise ValueError(f"Type de fichier non autorisé : {content_type}")

    if len(file_bytes) > MAX_SIZE_MB * 1024 * 1024:
        raise ValueError(f"Fichier trop volumineux (max {MAX_SIZE_MB} Mo).")

    settings = get_settings()
    bucket = settings.minio_bucket_couvertures
    _ensure_bucket(bucket)

    ext = content_type.split("/")[1]
    object_name = f"couvertures/{uuid.uuid4()}.{ext}"

    client = get_minio_client()
    client.put_object(
        bucket_name=bucket,
        object_name=object_name,
        data=BytesIO(file_bytes),
        length=len(file_bytes),
        content_type=content_type,
    )

    logger.info(f"Couverture uploadée : {object_name}")
    return object_name  # c'est ce token qui est stocké dans couverture_url


def delete_couverture(object_name: str) -> None:
    """
    Supprime une image de couverture dans MinIO.

    Args:
        object_name: token stocké dans couverture_url (ex: couvertures/uuid.jpg)
    """
    if not object_name:
        return
    try:
        settings = get_settings()
        client = get_minio_client()
        client.remove_object(
            bucket_name=settings.minio_bucket_couvertures,
            object_name=object_name,
        )
        logger.info(f"Couverture supprimée : {object_name}")
    except S3Error as e:
        logger.warning(f"Impossible de supprimer la couverture '{object_name}' : {e}")


def get_couverture_url(object_name: str) -> str:
    """
    Construit l'URL publique d'une couverture à partir du token stocké en base.

    Args:
        object_name: valeur de couverture_url en base de données

    Returns:
        URL HTTP complète accessible depuis le navigateur
    """
    if not object_name:
        return ""
    settings = get_settings()
    return f"{settings.minio_public_url}/{settings.minio_bucket_couvertures}/{object_name}"
