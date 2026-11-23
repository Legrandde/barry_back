from datetime import datetime

from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base
from models.mixins import utcnow


class AnalyticsEvent(Base):
    """Visite (name="pageview") ou action d'un visiteur sur le site (clic WhatsApp, ouverture d'un projet...).

    Aucune donnée personnelle n'est conservée : le visiteur est identifié par un hash
    de son IP et de son navigateur, qui change chaque jour. Le pays/région/ville est déduit
    localement de l'IP sans jamais conserver l'IP elle-même.
    """

    __tablename__ = "analytics_events"
    __table_args__ = (Index("ix_analytics_events_name_created_at", "name", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    name: Mapped[str] = mapped_column(String(50))
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    path: Mapped[str] = mapped_column(String(500), default="/")
    referrer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    utm_source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    visitor_hash: Mapped[str] = mapped_column(String(64), index=True)
    device: Mapped[str] = mapped_column(String(20))
    browser: Mapped[str] = mapped_column(String(50))
    os: Mapped[str] = mapped_column(String(50))
    language: Mapped[str | None] = mapped_column(String(10), nullable=True)
    country: Mapped[str | None] = mapped_column(String(2), nullable=True, index=True)
    region: Mapped[str | None] = mapped_column(String(120), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
