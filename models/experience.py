from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base
from models.mixins import OrderedMixin, TimestampMixin


class Experience(OrderedMixin, TimestampMixin, Base):
    """Étape du parcours professionnel (section « Parcours »)."""

    __tablename__ = "experiences"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    company: Mapped[str] = mapped_column(String(200))
    period: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, default="")
    technologies: Mapped[list[str]] = mapped_column(JSON, default=list)
