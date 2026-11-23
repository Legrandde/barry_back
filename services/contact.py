from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models import ContactMessage
from schemas.contact import ContactMessageCreate
from services.exceptions import NotFoundError


def create_message(db: Session, data: ContactMessageCreate) -> None:
    """Enregistre le message. Un envoi qui a rempli le piège à robots est ignoré sans le signaler."""
    if data.website:
        return
    db.add(ContactMessage(**data.model_dump(exclude={"website", "phone"}), phone=data.phone or None))
    db.commit()


def list_messages(db: Session) -> list[ContactMessage]:
    """Les plus récents d'abord."""
    return list(
        db.scalars(select(ContactMessage).order_by(ContactMessage.created_at.desc(), ContactMessage.id.desc()))
    )


def count_unread(db: Session) -> int:
    return (
        db.scalar(select(func.count()).select_from(ContactMessage).where(ContactMessage.is_read.is_(False)))
        or 0
    )


def _get(db: Session, message_id: int) -> ContactMessage:
    message = db.get(ContactMessage, message_id)
    if message is None:
        raise NotFoundError("Message introuvable.")
    return message


def set_read(db: Session, message_id: int, is_read: bool) -> ContactMessage:
    message = _get(db, message_id)
    message.is_read = is_read
    db.commit()
    db.refresh(message)
    return message


def delete_message(db: Session, message_id: int) -> None:
    db.delete(_get(db, message_id))
    db.commit()
