from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base
from models.mixins import OrderedMixin, TimestampMixin


class SocialLink(OrderedMixin, TimestampMixin, Base):
    """Lien vers un réseau social ou un site (pied de page et section Contact)."""

    __tablename__ = "social_links"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(100))
    url: Mapped[str] = mapped_column(String(500))
    icon: Mapped[str] = mapped_column(String(50), default="website")
