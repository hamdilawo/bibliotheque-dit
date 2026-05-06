"""
Gestion du stockage des fichiers (images de couverture).
Pour l'instant stockage local — peut être étendu vers S3.
"""
import uuid
from pathlib import Path


UPLOAD_DIR = Path("/app/media/couvertures")
ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE_MB = 5


def get_upload_dir() -> Path:
    """Retourne le dossier d'upload, le crée si nécessaire."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    return UPLOAD_DIR


def save_couverture(file_bytes: bytes, content_type: str) -> str:
    """
    Sauvegarde une image de couverture.
    Retourne l'URL relative du fichier sauvegardé.
    """
    if content_type not in ALLOWED_TYPES:
        raise ValueError(f"Type de fichier non autorisé : {content_type}")

    if len(file_bytes) > MAX_SIZE_MB * 1024 * 1024:
        raise ValueError(f"Fichier trop volumineux (max {MAX_SIZE_MB}MB).")

    ext = content_type.split("/")[1]
    filename = f"{uuid.uuid4()}.{ext}"
    filepath = get_upload_dir() / filename

    with open(filepath, "wb") as f:
        f.write(file_bytes)

    return f"/media/couvertures/{filename}"


def delete_couverture(url: str) -> None:
    """Supprime une image de couverture."""
    if not url:
        return
    filename = url.split("/")[-1]
    filepath = get_upload_dir() / filename
    if filepath.exists():
        filepath.unlink()