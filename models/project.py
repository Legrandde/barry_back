from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base
from models.mixins import OrderedMixin, TimestampMixin


class Project(OrderedMixin, TimestampMixin, Base):
    """Réalisation affichée dans la section « Projets » (carte + modale de détail)."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(150), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    main_image: Mapped[str] = mapped_column(String(500), default="")
    images: Mapped[list[str]] = mapped_column(JSON, default=list)
    type: Mapped[str] = mapped_column(String(20), default="web")
    category: Mapped[str] = mapped_column(String(100), default="Web Development")
    technologies: Mapped[list[str]] = mapped_column(JSON, default=list)
    live_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    demo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    github_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
