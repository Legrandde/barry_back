from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base
from models.mixins import OrderedMixin, TimestampMixin


class Education(OrderedMixin, TimestampMixin, Base):
    """Diplôme ou formation académique (section « Formation »)."""

    __tablename__ = "educations"

    id: Mapped[int] = mapped_column(primary_key=True)
    degree: Mapped[str] = mapped_column(String(200))
    institution: Mapped[str] = mapped_column(String(200))
    period: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, default="")
    achievements: Mapped[list[str]] = mapped_column(JSON, default=list)
