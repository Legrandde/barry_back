from sqlalchemy import func, inspect, select
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateColumn

import models  # noqa: F401  (enregistre toutes les tables dans Base.metadata)
from core.config import settings
from db import seed_data
from db.base import Base
from db.session import SessionLocal, engine
from models import (
    Education,
    Experience,
    Project,
    Section,
    ServiceItem,
    SkillCategory,
    SocialLink,
    Testimonial,
)
from schemas.sections import SECTION_SCHEMAS
from services.analytics import purge_old_events
from services.auth import ensure_admin
from services.media import reset_interrupted_compressions


def seed_content(db: Session) -> None:
    first_run = not db.scalar(select(func.count()).select_from(Section))

    # Les sections manquantes sont toujours créées (utile si une nouvelle section est ajoutée au site)
    existing = set(db.scalars(select(Section.key)))
    for key, content in seed_data.SECTIONS.items():
        if key.value not in existing:
            validated = SECTION_SCHEMAS[key].model_validate(content)
            db.add(Section(key=key.value, content=validated.model_dump(mode="json")))

    # Les listes ne sont remplies qu'au tout premier démarrage, pour ne jamais recréer
    # des éléments que l'admin aurait volontairement supprimés.
    if first_run:
        for model, rows in (
            (ServiceItem, seed_data.SERVICES),
            (SkillCategory, seed_data.SKILL_CATEGORIES),
            (Experience, seed_data.EXPERIENCES),
            (Education, seed_data.EDUCATIONS),
            (Project, seed_data.PROJECTS),
            (Testimonial, seed_data.TESTIMONIALS),
            (SocialLink, seed_data.SOCIAL_LINKS),
        ):
            for position, row in enumerate(rows):
                db.add(model(**row, position=position))


def add_missing_columns() -> None:
    """create_all ne modifie pas les tables existantes : ajoute les colonnes apparues depuis."""
    inspector = inspect(engine)
    with engine.begin() as connection:
        for table in Base.metadata.sorted_tables:
            if not inspector.has_table(table.name):
                continue
            existing = {column["name"] for column in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name not in existing:
                    ddl = CreateColumn(column).compile(dialect=engine.dialect)
                    connection.exec_driver_sql(f"ALTER TABLE {table.name} ADD COLUMN {ddl}")


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    add_missing_columns()
    settings.media_dir.mkdir(parents=True, exist_ok=True)
    with SessionLocal() as db:
        ensure_admin(db, settings.admin_username, settings.admin_password)
        seed_content(db)
        purge_old_events(db)
        reset_interrupted_compressions(db)
        db.commit()
