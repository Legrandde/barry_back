from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base
from models.mixins import OrderedMixin, TimestampMixin


class ServiceItem(OrderedMixin, TimestampMixin, Base):
    """Service proposé dans la section « Services »."""

    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text, default="")
    icon: Mapped[str] = mapped_column(String(50), default="code")
