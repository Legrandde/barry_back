from typing import Any

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Section
from schemas.base import CamelModel
from schemas.sections import HIDEABLE_SECTIONS, SECTION_SCHEMAS, SectionKey
from services.exceptions import InvalidDataError, NotFoundError


def list_sections(db: Session) -> list[Section]:
    return list(db.scalars(select(Section).order_by(Section.key)))


def get_section(db: Session, key: SectionKey) -> Section:
    section = db.get(Section, key.value)
    if section is None:
        raise NotFoundError(f"Section « {key.value} » introuvable.")
    return section


def read_content(section: Section) -> CamelModel:
    return SECTION_SCHEMAS[SectionKey(section.key)].model_validate(section.content)


def get_content(db: Session, key: SectionKey) -> CamelModel:
    return read_content(get_section(db, key))


def set_visibility(db: Session, key: SectionKey, is_visible: bool) -> Section:
    if key not in HIDEABLE_SECTIONS:
        raise InvalidDataError("Cette section ne peut pas être masquée.")
    section = get_section(db, key)
    section.is_visible = is_visible
    db.commit()
    return section


def get_visible_content(db: Session, key: SectionKey) -> CamelModel:
    """Contenu public d'une section : introuvable si elle est masquée."""
    section = get_section(db, key)
    if not section.is_visible:
        raise NotFoundError(f"Section « {key.value} » introuvable.")
    return read_content(section)


def visibility_map(db: Session) -> dict[str, bool]:
    return {
        section.key: section.is_visible
        for section in list_sections(db)
        if SectionKey(section.key) in HIDEABLE_SECTIONS
    }


def replace_section(db: Session, key: SectionKey, payload: CamelModel) -> CamelModel:
    section = get_section(db, key)
    section.content = payload.model_dump(mode="json")
    db.commit()
    return read_content(section)


def patch_section(db: Session, key: SectionKey, changes: dict[str, Any]) -> CamelModel:
    """Met à jour uniquement les champs fournis (camelCase ou snake_case acceptés)."""
    schema = SECTION_SCHEMAS[key]
    section = get_section(db, key)

    by_alias = {info.alias or name: name for name, info in schema.model_fields.items()}
    normalized = {by_alias.get(field, field): value for field, value in changes.items()}
    try:
        validated = schema.model_validate({**section.content, **normalized})
    except ValidationError as exc:
        raise InvalidDataError(exc.errors(include_url=False, include_context=False)) from exc

    section.content = validated.model_dump(mode="json")
    db.commit()
    return validated
