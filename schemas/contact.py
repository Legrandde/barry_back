from datetime import datetime
from typing import Annotated

from pydantic import Field, StringConstraints

from schemas.base import CamelModel

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=120)]
Email = Annotated[
    str,
    StringConstraints(strip_whitespace=True, to_lower=True, max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$"),
]
Phone = Annotated[str, StringConstraints(strip_whitespace=True, max_length=40)]
Subject = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=200)]
Body = Annotated[str, StringConstraints(strip_whitespace=True, min_length=5, max_length=5000)]


class ContactMessageCreate(CamelModel):
    """Envoyé par le formulaire de contact du portfolio."""

    name: Name
    email: Email
    phone: Phone | None = None
    subject: Subject
    message: Body
    # Piège à robots : champ caché du formulaire, qu'un humain laisse vide
    website: str = Field("", max_length=200, description="Laisser vide (anti-spam)")


class ContactMessageRead(CamelModel):
    id: int
    created_at: datetime
    name: str
    email: str
    phone: str | None
    subject: str
    message: str
    is_read: bool


class ContactMessageUpdate(CamelModel):
    is_read: bool


class UnreadCount(CamelModel):
    unread: int
