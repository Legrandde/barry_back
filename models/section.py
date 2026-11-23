from typing import Any

from sqlalchemy import JSON, Boolean, String, true
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base
from models.mixins import TimestampMixin


class Section(TimestampMixin, Base):
    """Bloc de contenu unique du portfolio (bannière, à propos, stats, contact...).

    Le contenu est stocké en JSON et validé par le schéma Pydantic correspondant à la clé.
    """

    __tablename__ = "sections"

    key: Mapped[str] = mapped_column(String(50), primary_key=True)
    content: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    # Une section masquée n'est plus affichée sur le site (son contenu est conservé)
    is_visible: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())
