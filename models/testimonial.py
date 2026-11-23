from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base
from models.mixins import OrderedMixin, TimestampMixin


class Testimonial(OrderedMixin, TimestampMixin, Base):
    """Témoignage client (section « Témoignages »)."""

    __tablename__ = "testimonials"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150))
    role: Mapped[str] = mapped_column(String(150), default="")
    company: Mapped[str] = mapped_column(String(150), default="")
    image: Mapped[str] = mapped_column(String(500), default="")
    rating: Mapped[int] = mapped_column(Integer, default=5)
    text: Mapped[str] = mapped_column(Text, default="")
