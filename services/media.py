import logging
import os
import time
import uuid
from pathlib import Path
from typing import BinaryIO

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from core.config import settings
from db.session import SessionLocal
from models import Media
from services import video
from services.exceptions import NotFoundError, PayloadTooLargeError, UnsupportedMediaError

logger = logging.getLogger("uvicorn.error")

_CHUNK_SIZE = 1024 * 1024

# Type MIME -> extension enregistrée
ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "image/avif": ".avif",
    "video/mp4": ".mp4",
    "video/webm": ".webm",
}


def _matches_signature(content_type: str, head: bytes) -> bool:
    """Vérifie les premiers octets du fichier pour ne pas se fier uniquement au type déclaré."""
    match content_type:
        case "image/jpeg":
            return head.startswith(b"\xff\xd8\xff")
        case "image/png":
            return head.startswith(b"\x89PNG\r\n\x1a\n")
        case "image/gif":
            return head.startswith((b"GIF87a", b"GIF89a"))
        case "image/webp":
            return head[:4] == b"RIFF" and head[8:12] == b"WEBP"
        case "image/avif" | "video/mp4":
            return head[4:8] == b"ftyp"
        case "video/webm":
            return head.startswith(b"\x1a\x45\xdf\xa3")
    return False


def build_url(filename: str, base_url: str) -> str:
    base = (settings.public_base_url or base_url).rstrip("/")
    return f"{base}{settings.media_url_path}/{filename}"


def list_media(db: Session) -> list[Media]:
    return list(db.scalars(select(Media).order_by(Media.created_at.desc(), Media.id.desc())))


def save_upload(db: Session, stream: BinaryIO, original_name: str, content_type: str | None) -> Media:
    extension = ALLOWED_TYPES.get(content_type or "")
    if extension is None:
        allowed = ", ".join(ALLOWED_TYPES)
        raise UnsupportedMediaError(f"Type de fichier non autorisé. Types acceptés : {allowed}.")

    head = stream.read(16)
    if not _matches_signature(content_type, head):
        raise UnsupportedMediaError("Le contenu du fichier ne correspond pas à son type.")

    is_video = content_type.startswith("video/")
    max_mb = settings.max_video_upload_size_mb if is_video else settings.max_upload_size_mb
    max_bytes = max_mb * 1024 * 1024
    settings.media_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{extension}"
    destination = settings.media_dir / filename

    size = len(head)
    try:
        with destination.open("wb") as out:
            out.write(head)
            while chunk := stream.read(_CHUNK_SIZE):
                size += len(chunk)
                if size > max_bytes:
                    raise PayloadTooLargeError(
                        f"Fichier trop volumineux (maximum {max_mb} Mo)."
                    )
                out.write(chunk)
    except BaseException:
        destination.unlink(missing_ok=True)
        raise

    media = Media(
        filename=filename,
        original_name=Path(original_name or filename).name[:255],
        content_type=content_type,
        size=size,
        status="processing" if is_video and size > settings.video_compression_threshold_mb * 1024 * 1024 else "ready",
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return media


def delete_media(db: Session, media_id: int) -> None:
    media = db.get(Media, media_id)
    if media is None:
        raise NotFoundError(f"Média introuvable (id={media_id}).")
    (settings.media_dir / media.filename).unlink(missing_ok=True)
    db.delete(media)
    db.commit()


def _replace_file(source: Path, destination: Path) -> bool:
    """Remplace le fichier ; réessaie si Windows le verrouille (vidéo en cours de lecture)."""
    for _ in range(10):
        try:
            os.replace(source, destination)
            return True
        except PermissionError:
            time.sleep(0.5)
    source.unlink(missing_ok=True)
    return False


def compress_media(media_id: int) -> None:
    """Tâche de fond : compresse une vidéo lourde puis remplace le fichier (même URL)."""
    with SessionLocal() as db:
        media = db.get(Media, media_id)
        if media is None or media.status != "processing":
            return
        path = settings.media_dir / media.filename
        compressed = video.compress_video(path) if path.exists() else None
        if compressed is not None and _replace_file(compressed, path):
            logger.info(
                "Vidéo %s compressée : %.1f Mo -> %.1f Mo",
                media.filename,
                media.size / 1e6,
                path.stat().st_size / 1e6,
            )
            media.original_size = media.size
            media.size = path.stat().st_size
        media.status = "ready"
        db.commit()


def reset_interrupted_compressions(db: Session) -> None:
    """Au démarrage : une compression interrompue (redémarrage) garde simplement la vidéo d'origine."""
    db.execute(update(Media).where(Media.status == "processing").values(status="ready"))
