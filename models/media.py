from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base
from models.mixins import TimestampMixin


class Media(TimestampMixin, Base):
    """Fichier (image ou vidéo) téléversé par l'admin et servi sous /media.

    Les vidéos lourdes sont compressées en arrière-plan après l'envoi.
    """

    __tablename__ = "media"

    id: Mapped[int] = mapped_column(primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), unique=True)
    original_name: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(100))
    size: Mapped[int] = mapped_column(Integer)
    # "processing" pendant la compression d'une vidéo, sinon "ready"
    status: Mapped[str] = mapped_column(String(20), default="ready", server_default="ready")
    # Taille avant compression (None si le fichier n'a pas été compressé)
    original_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
