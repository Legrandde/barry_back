from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends

from core.deps import DbSession, get_current_admin
from schemas.base import CamelModel
from schemas.sections import (
    HIDEABLE_SECTIONS,
    SECTION_SCHEMAS,
    SectionKey,
    SectionRead,
    SectionVisibility,
    SectionVisibilityUpdate,
)
from services import sections as sections_service

router = APIRouter(
    prefix="/api/admin/sections",
    tags=["Admin · Sections"],
    dependencies=[Depends(get_current_admin)],
)


@router.get("", response_model=list[SectionRead])
def list_sections(db: DbSession):
    return [
        SectionRead(
            key=section.key,
            is_visible=section.is_visible,
            content=sections_service.read_content(section).model_dump(by_alias=True, mode="json"),
            updated_at=section.updated_at,
        )
        for section in sections_service.list_sections(db)
    ]


def _register_section_routes(key: SectionKey, schema: type[CamelModel]) -> None:
    """Déclare GET / PUT / PATCH typés pour une section, afin d'avoir une doc Swagger précise."""

    @router.get(f"/{key.value}", response_model=schema, name=f"get_{key.value}_section")
    def get_section(db: DbSession):
        return sections_service.get_content(db, key)

    @router.put(f"/{key.value}", response_model=schema, name=f"replace_{key.value}_section")
    def replace_section(payload: schema, db: DbSession):
        return sections_service.replace_section(db, key, payload)

    @router.patch(f"/{key.value}", response_model=schema, name=f"patch_{key.value}_section")
    def patch_section(changes: Annotated[dict[str, Any], Body()], db: DbSession):
        """Modifie uniquement les champs envoyés."""
        return sections_service.patch_section(db, key, changes)


for _key, _schema in SECTION_SCHEMAS.items():
    _register_section_routes(_key, _schema)


def _visibility(section) -> SectionVisibility:
    key = SectionKey(section.key)
    return SectionVisibility(key=key, is_visible=section.is_visible, hideable=key in HIDEABLE_SECTIONS)


@router.get("/{key}/visibility", response_model=SectionVisibility)
def get_visibility(key: SectionKey, db: DbSession):
    return _visibility(sections_service.get_section(db, key))


@router.put("/{key}/visibility", response_model=SectionVisibility)
def set_visibility(key: SectionKey, payload: SectionVisibilityUpdate, db: DbSession):
    """Affiche ou masque une section sur le site, sans toucher à son contenu."""
    return _visibility(sections_service.set_visibility(db, key, payload.is_visible))
