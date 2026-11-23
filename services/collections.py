import re
import unicodedata
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from db.base import Base
from models import Education, Experience, Project, ServiceItem, SkillCategory, SocialLink, Testimonial
from services.exceptions import ConflictError, InvalidDataError, NotFoundError


class CollectionService[M: Base]:
    """Opérations communes aux listes ordonnées du site (projets, services, compétences, parcours...)."""

    def __init__(self, model: type[M], label: str):
        self.model = model
        self.label = label

    def list(self, db: Session, *, published_only: bool = False) -> list[M]:
        stmt = select(self.model).order_by(self.model.position, self.model.id)
        if published_only:
            stmt = stmt.where(self.model.is_published.is_(True))
        return list(db.scalars(stmt))

    def get(self, db: Session, item_id: int) -> M:
        item = db.get(self.model, item_id)
        if item is None:
            raise NotFoundError(f"{self.label} introuvable (id={item_id}).")
        return item

    def create(self, db: Session, data: dict[str, Any]) -> M:
        if data.get("position") is None:
            data["position"] = self._next_position(db)
        item = self.model(**self._prepare(db, data, None))
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def update(self, db: Session, item_id: int, data: dict[str, Any]) -> M:
        item = self.get(db, item_id)
        columns = self.model.__table__.columns
        for field, value in data.items():
            if value is None and not columns[field].nullable:
                raise InvalidDataError(f"Le champ « {field} » ne peut pas être vide.")
        for field, value in self._prepare(db, data, item).items():
            setattr(item, field, value)
        db.commit()
        db.refresh(item)
        return item

    def delete(self, db: Session, item_id: int) -> None:
        db.delete(self.get(db, item_id))
        db.commit()

    def reorder(self, db: Session, ids: list[int]) -> list[M]:
        items = {item.id: item for item in self.list(db)}
        if len(ids) != len(set(ids)) or set(ids) != set(items):
            raise InvalidDataError(
                "La liste doit contenir exactement une fois chaque identifiant existant."
            )
        for position, item_id in enumerate(ids):
            items[item_id].position = position
        db.commit()
        return self.list(db)

    def _next_position(self, db: Session) -> int:
        current = db.scalar(select(func.max(self.model.position)))
        return 0 if current is None else current + 1

    def _prepare(self, db: Session, data: dict[str, Any], item: M | None) -> dict[str, Any]:
        """Point d'extension pour les règles propres à une collection."""
        return data


def slugify(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-") or "projet"


class ProjectService(CollectionService[Project]):
    def get_published_by_slug(self, db: Session, slug: str) -> Project:
        project = db.scalar(
            select(Project).where(Project.slug == slug, Project.is_published.is_(True))
        )
        if project is None:
            raise NotFoundError(f"Projet « {slug} » introuvable.")
        return project

    def _prepare(self, db: Session, data: dict[str, Any], item: Project | None) -> dict[str, Any]:
        current_id = item.id if item else None
        if data.get("slug"):
            if self._slug_taken(db, data["slug"], current_id):
                raise ConflictError(f"Le slug « {data['slug']} » est déjà utilisé.")
        elif item is None:
            data["slug"] = self._unique_slug(db, slugify(data["title"]))
        return data

    def _slug_taken(self, db: Session, slug: str, exclude_id: int | None) -> bool:
        stmt = select(Project.id).where(Project.slug == slug)
        if exclude_id is not None:
            stmt = stmt.where(Project.id != exclude_id)
        return db.scalar(stmt) is not None

    def _unique_slug(self, db: Session, base: str) -> str:
        slug, suffix = base, 2
        while self._slug_taken(db, slug, None):
            slug, suffix = f"{base}-{suffix}", suffix + 1
        return slug


projects = ProjectService(Project, "Projet")
services = CollectionService(ServiceItem, "Service")
skill_categories = CollectionService(SkillCategory, "Catégorie de compétences")
experiences = CollectionService(Experience, "Étape du parcours")
educations = CollectionService(Education, "Formation")
testimonials = CollectionService(Testimonial, "Témoignage")
social_links = CollectionService(SocialLink, "Lien social")
