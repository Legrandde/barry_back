from datetime import date, datetime

from sqlalchemy import JSON, Boolean, Date, DateTime, ForeignKey, Integer, String, Text, false, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base
from models.mixins import TimestampMixin


class Prospect(TimestampMixin, Base):
    """Dossier de prospection commerciale (mini-CRM personnel)."""

    __tablename__ = "prospects"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Informations générales
    name: Mapped[str] = mapped_column(String(200), index=True)
    cover_image: Mapped[str] = mapped_column(String(500), default="")
    logo: Mapped[str] = mapped_column(String(500), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    sector: Mapped[str] = mapped_column(String(120), default="", index=True)
    location: Mapped[str] = mapped_column(String(160), default="")
    website: Mapped[str] = mapped_column(String(500), default="")
    social_links: Mapped[list] = mapped_column(JSON, default=list)

    # Informations commerciales
    contact_name: Mapped[str] = mapped_column(String(160), default="")
    contact_role: Mapped[str] = mapped_column(String(160), default="")
    contact_email: Mapped[str] = mapped_column(String(255), default="")
    contact_phone: Mapped[str] = mapped_column(String(80), default="")
    identified_need: Mapped[str] = mapped_column(Text, default="")
    proposed_service: Mapped[str] = mapped_column(String(255), default="")
    estimated_budget: Mapped[str] = mapped_column(String(120), default="")
    priority: Mapped[str] = mapped_column(String(30), default="moyenne", index=True)

    # Suivi
    status: Mapped[str] = mapped_column(String(40), default="a_prospecter", index=True)
    first_contact_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_contact_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    next_follow_up_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    next_action: Mapped[str] = mapped_column(String(255), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false(), index=True)

    interactions: Mapped[list["ProspectInteraction"]] = relationship(
        back_populates="prospect",
        cascade="all, delete-orphan",
        order_by="desc(ProspectInteraction.interaction_date), desc(ProspectInteraction.id)",
    )
    documents: Mapped[list["ProspectDocument"]] = relationship(
        back_populates="prospect",
        cascade="all, delete-orphan",
        order_by="desc(ProspectDocument.created_at), desc(ProspectDocument.id)",
    )


class ProspectInteraction(TimestampMixin, Base):
    """Historique chronologique des échanges et actions sur un prospect."""

    __tablename__ = "prospect_interactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    prospect_id: Mapped[int] = mapped_column(ForeignKey("prospects.id", ondelete="CASCADE"), index=True)
    type: Mapped[str] = mapped_column(String(30), default="note")
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text, default="")
    interaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    prospect: Mapped[Prospect] = relationship(back_populates="interactions")


class ProspectDocument(TimestampMixin, Base):
    """Pièce jointe (PDF, devis, proposition, image) associée à un dossier prospect."""

    __tablename__ = "prospect_documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    prospect_id: Mapped[int] = mapped_column(ForeignKey("prospects.id", ondelete="CASCADE"), index=True)
    filename: Mapped[str] = mapped_column(String(255), unique=True)
    original_name: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(120))
    size: Mapped[int] = mapped_column(Integer)

    prospect: Mapped[Prospect] = relationship(back_populates="documents")
