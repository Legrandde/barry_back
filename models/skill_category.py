from typing import Any

from sqlalchemy import JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base
from models.mixins import OrderedMixin, TimestampMixin


class SkillCategory(OrderedMixin, TimestampMixin, Base):
    """Catégorie de compétences techniques (Frontend, Backend, Mobile, Cloud & DevOps, Outils)."""

    __tablename__ = "skill_categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    icon: Mapped[str] = mapped_column(String(50), default="code")
    skills: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
