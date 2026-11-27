import uuid
from datetime import UTC, date, datetime
from pathlib import Path
from typing import BinaryIO

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from core.config import settings
from models.prospect import Prospect, ProspectDocument, ProspectInteraction
from schemas.prospects import ProspectCreate, ProspectInteractionCreate, ProspectUpdate
from services.exceptions import NotFoundError, PayloadTooLargeError, UnsupportedMediaError

_CHUNK_SIZE = 1024 * 1024
_PROSPECT_DOCS_SUBDIR = "prospects"

STATUS_LABELS: dict[str, str] = {
    "a_prospecter": "À prospecter",
    "a_contacter": "À contacter",
    "contacte": "Contacté",
    "en_discussion": "En discussion",
    "proposition_envoyee": "Proposition envoyée",
    "en_negociation": "En négociation",
    "gagne": "Gagné",
    "perdu": "Perdu",
    "en_pause": "En pause",
}

CONTACT_INTERACTION_TYPES = {"email", "appel", "rendez_vous", "relance", "proposition"}

ALLOWED_DOCUMENT_TYPES: dict[str, str] = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "text/plain": ".txt",
    "text/csv": ".csv",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.ms-excel": ".xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
    "application/zip": ".zip",
}


def _matches_doc_signature(content_type: str, head: bytes) -> bool:
    match content_type:
        case "application/pdf":
            return head.startswith(b"%PDF-")
        case "image/jpeg":
            return head.startswith(b"\xff\xd8\xff")
        case "image/png":
            return head.startswith(b"\x89PNG\r\n\x1a\n")
        case "image/webp":
            return head[:4] == b"RIFF" and head[8:12] == b"WEBP"
        case (
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            | "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            | "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            | "application/zip"
        ):
            return head.startswith(b"PK\x03\x04") or head.startswith(b"PK\x05\x06")
        case "application/msword" | "application/vnd.ms-excel":
            return head.startswith(b"\xd0\xcf\x11\xe0")
        case "text/plain" | "text/csv":
            return b"\x00" not in head
    return False


def build_document_url(filename: str, base_url: str) -> str:
    base = (settings.public_base_url or base_url).rstrip("/")
    return f"{base}{settings.media_url_path}/{_PROSPECT_DOCS_SUBDIR}/{filename}"


def list_prospects(
    db: Session,
    *,
    search: str | None = None,
    status: str | None = None,
    sector: str | None = None,
    priority: str | None = None,
    archived: bool = False,
    sort: str = "updated_at",
) -> list[Prospect]:
    query = select(Prospect).where(Prospect.is_archived == archived)

    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.where(
            or_(
                Prospect.name.ilike(term),
                Prospect.sector.ilike(term),
                Prospect.location.ilike(term),
                Prospect.contact_name.ilike(term),
                Prospect.contact_email.ilike(term),
                Prospect.proposed_service.ilike(term),
                Prospect.description.ilike(term),
            )
        )
    if status:
        query = query.where(Prospect.status == status)
    if sector:
        query = query.where(Prospect.sector == sector)
    if priority:
        query = query.where(Prospect.priority == priority)

    if sort == "created_at":
        query = query.order_by(Prospect.created_at.desc(), Prospect.id.desc())
    elif sort == "next_follow_up_date":
        query = query.order_by(Prospect.next_follow_up_date.is_(None), Prospect.next_follow_up_date.asc(), Prospect.id.desc())
    else:
        query = query.order_by(Prospect.updated_at.desc(), Prospect.id.desc())

    return list(db.scalars(query))


def get_stats(db: Session) -> dict[str, int]:
    today = date.today()
    active_filter = Prospect.is_archived.is_(False)

    total = db.scalar(select(func.count()).select_from(Prospect).where(active_filter)) or 0
    a_contacter = (
        db.scalar(
            select(func.count())
            .select_from(Prospect)
            .where(active_filter, Prospect.status.in_(("a_prospecter", "a_contacter")))
        )
        or 0
    )
    en_discussion = (
        db.scalar(
            select(func.count())
            .select_from(Prospect)
            .where(active_filter, Prospect.status.in_(("contacte", "en_discussion", "en_negociation")))
        )
        or 0
    )
    propositions_envoyees = (
        db.scalar(
            select(func.count())
            .select_from(Prospect)
            .where(active_filter, Prospect.status == "proposition_envoyee")
        )
        or 0
    )
    gagnes = (
        db.scalar(
            select(func.count())
            .select_from(Prospect)
            .where(active_filter, Prospect.status == "gagne")
        )
        or 0
    )
    archived = db.scalar(select(func.count()).select_from(Prospect).where(Prospect.is_archived.is_(True))) or 0

    open_statuses = ("a_prospecter", "a_contacter", "contacte", "en_discussion", "proposition_envoyee", "en_negociation")
    overdue_follow_ups = (
        db.scalar(
            select(func.count())
            .select_from(Prospect)
            .where(
                active_filter,
                Prospect.status.in_(open_statuses),
                Prospect.next_follow_up_date.is_not(None),
                Prospect.next_follow_up_date < today,
            )
        )
        or 0
    )
    today_follow_ups = (
        db.scalar(
            select(func.count())
            .select_from(Prospect)
            .where(
                active_filter,
                Prospect.status.in_(open_statuses),
                Prospect.next_follow_up_date == today,
            )
        )
        or 0
    )

    return {
        "total": total,
        "a_contacter": a_contacter,
        "en_discussion": en_discussion,
        "propositions_envoyees": propositions_envoyees,
        "gagnes": gagnes,
        "archived": archived,
        "overdue_follow_ups": overdue_follow_ups,
        "today_follow_ups": today_follow_ups,
    }


def get_prospect(db: Session, prospect_id: int) -> Prospect:
    prospect = db.scalar(
        select(Prospect)
        .options(selectinload(Prospect.interactions), selectinload(Prospect.documents))
        .where(Prospect.id == prospect_id)
    )
    if prospect is None:
        raise NotFoundError(f"Dossier prospect introuvable (id={prospect_id}).")
    return prospect


def create_prospect(db: Session, payload: ProspectCreate) -> Prospect:
    data = payload.model_dump()
    if data.get("first_contact_date") and not data.get("last_contact_date"):
        data["last_contact_date"] = data["first_contact_date"]

    prospect = Prospect(**data)
    db.add(prospect)
    db.flush()

    db.add(
        ProspectInteraction(
            prospect_id=prospect.id,
            type="statut",
            title="Dossier créé",
            content=f"Statut initial : {STATUS_LABELS.get(prospect.status, prospect.status)}.",
            interaction_date=datetime.now(UTC),
        )
    )
    db.commit()
    db.expire_all()
    return get_prospect(db, prospect.id)


def update_prospect(db: Session, prospect_id: int, payload: ProspectUpdate) -> Prospect:
    prospect = get_prospect(db, prospect_id)
    old_status = prospect.status
    updates = payload.model_dump(exclude_unset=True)

    for key, value in updates.items():
        setattr(prospect, key, value)

    if "status" in updates and updates["status"] != old_status:
        old_label = STATUS_LABELS.get(old_status, old_status)
        new_label = STATUS_LABELS.get(prospect.status, prospect.status)
        db.add(
            ProspectInteraction(
                prospect_id=prospect.id,
                type="statut",
                title=f"Statut modifié : {new_label}",
                content=f"Passage de « {old_label} » à « {new_label} ».",
                interaction_date=datetime.now(UTC),
            )
        )

    db.commit()
    db.expire_all()
    return get_prospect(db, prospect.id)


def delete_prospect(db: Session, prospect_id: int) -> None:
    prospect = get_prospect(db, prospect_id)
    docs_dir = settings.media_dir / _PROSPECT_DOCS_SUBDIR
    for doc in prospect.documents:
        (docs_dir / doc.filename).unlink(missing_ok=True)
    db.delete(prospect)
    db.commit()


def add_interaction(db: Session, prospect_id: int, payload: ProspectInteractionCreate) -> ProspectInteraction:
    prospect = get_prospect(db, prospect_id)
    when = payload.interaction_date or datetime.now(UTC)
    interaction = ProspectInteraction(
        prospect_id=prospect.id,
        type=payload.type,
        title=payload.title,
        content=payload.content,
        interaction_date=when,
    )
    db.add(interaction)

    # Met à jour automatiquement la date du dernier contact pour les échanges réels
    if payload.type in CONTACT_INTERACTION_TYPES:
        contact_day = when.date()
        if prospect.last_contact_date is None or contact_day >= prospect.last_contact_date:
            prospect.last_contact_date = contact_day
        if prospect.first_contact_date is None:
            prospect.first_contact_date = contact_day

    db.commit()
    db.refresh(interaction)
    return interaction


def delete_interaction(db: Session, prospect_id: int, interaction_id: int) -> None:
    interaction = db.scalar(
        select(ProspectInteraction).where(
            ProspectInteraction.id == interaction_id,
            ProspectInteraction.prospect_id == prospect_id,
        )
    )
    if interaction is None:
        raise NotFoundError(f"Interaction introuvable (id={interaction_id}).")
    db.delete(interaction)
    db.commit()


def upload_document(
    db: Session,
    prospect_id: int,
    stream: BinaryIO,
    original_name: str,
    content_type: str | None,
) -> ProspectDocument:
    prospect = get_prospect(db, prospect_id)
    extension = ALLOWED_DOCUMENT_TYPES.get(content_type or "")
    if extension is None:
        raise UnsupportedMediaError(
            "Type de document non autorisé. Formats acceptés : PDF, images (JPG/PNG/WebP), Word, Excel, PowerPoint, TXT, CSV, ZIP."
        )

    head = stream.read(16)
    if not _matches_doc_signature(content_type or "", head):
        raise UnsupportedMediaError("Le contenu du fichier ne correspond pas au format déclaré.")

    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    docs_dir = settings.media_dir / _PROSPECT_DOCS_SUBDIR
    docs_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4().hex}{extension}"
    destination = docs_dir / filename

    size = len(head)
    try:
        with destination.open("wb") as out:
            out.write(head)
            while chunk := stream.read(_CHUNK_SIZE):
                size += len(chunk)
                if size > max_bytes:
                    raise PayloadTooLargeError(f"Fichier trop volumineux (maximum {settings.max_upload_size_mb} Mo).")
                out.write(chunk)
    except BaseException:
        destination.unlink(missing_ok=True)
        raise

    doc = ProspectDocument(
        prospect_id=prospect.id,
        filename=filename,
        original_name=Path(original_name or filename).name[:255],
        content_type=content_type or "application/octet-stream",
        size=size,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def delete_document(db: Session, prospect_id: int, doc_id: int) -> None:
    doc = db.scalar(
        select(ProspectDocument).where(
            ProspectDocument.id == doc_id,
            ProspectDocument.prospect_id == prospect_id,
        )
    )
    if doc is None:
        raise NotFoundError(f"Document introuvable (id={doc_id}).")
    (settings.media_dir / _PROSPECT_DOCS_SUBDIR / doc.filename).unlink(missing_ok=True)
    db.delete(doc)
    db.commit()
