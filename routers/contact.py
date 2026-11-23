from fastapi import APIRouter, Depends, status

from core.deps import DbSession, get_current_admin
from schemas.contact import ContactMessageCreate, ContactMessageRead, ContactMessageUpdate, UnreadCount
from services import contact as contact_service

public_router = APIRouter(prefix="/api/public", tags=["Site public"])

admin_router = APIRouter(
    prefix="/api/admin/messages",
    tags=["Admin · Messages"],
    dependencies=[Depends(get_current_admin)],
)


@public_router.post("/contact", status_code=status.HTTP_204_NO_CONTENT)
def send_message(data: ContactMessageCreate, db: DbSession):
    """Message du formulaire de contact, à lire dans l'espace admin."""
    contact_service.create_message(db, data)


@admin_router.get("", response_model=list[ContactMessageRead])
def list_messages(db: DbSession):
    return contact_service.list_messages(db)


@admin_router.get("/unread-count", response_model=UnreadCount)
def unread_count(db: DbSession):
    """Nombre de messages non lus (pastille du menu de l'admin)."""
    return UnreadCount(unread=contact_service.count_unread(db))


@admin_router.patch("/{message_id}", response_model=ContactMessageRead)
def update_message(message_id: int, data: ContactMessageUpdate, db: DbSession):
    """Marque le message comme lu ou non lu."""
    return contact_service.set_read(db, message_id, data.is_read)


@admin_router.delete("/{message_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_message(message_id: int, db: DbSession):
    contact_service.delete_message(db, message_id)
