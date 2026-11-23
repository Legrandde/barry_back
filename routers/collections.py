from fastapi import APIRouter, Depends, status

from core.deps import DbSession, get_current_admin
from schemas.base import CamelModel, ReorderRequest
from schemas.education import EducationCreate, EducationRead, EducationUpdate
from schemas.experience import ExperienceCreate, ExperienceRead, ExperienceUpdate
from schemas.project import ProjectCreate, ProjectRead, ProjectUpdate
from schemas.service import ServiceCreate, ServiceRead, ServiceUpdate
from schemas.skill_category import SkillCategoryCreate, SkillCategoryRead, SkillCategoryUpdate
from schemas.social_link import SocialLinkCreate, SocialLinkRead, SocialLinkUpdate
from schemas.testimonial import TestimonialCreate, TestimonialRead, TestimonialUpdate
from services import collections
from services.collections import CollectionService


def build_collection_router(
    *,
    path: str,
    tag: str,
    service: CollectionService,
    create_schema: type[CamelModel],
    update_schema: type[CamelModel],
    read_schema: type[CamelModel],
) -> APIRouter:
    """CRUD + réordonnancement pour une liste du site (accès admin uniquement)."""
    router = APIRouter(
        prefix=f"/api/admin/{path}",
        tags=[tag],
        dependencies=[Depends(get_current_admin)],
    )

    @router.get("", response_model=list[read_schema])
    def list_items(db: DbSession):
        """Tous les éléments, publiés ou non, dans l'ordre d'affichage."""
        return service.list(db)

    @router.post("", response_model=read_schema, status_code=status.HTTP_201_CREATED)
    def create_item(payload: create_schema, db: DbSession):
        return service.create(db, payload.model_dump())

    @router.put("/reorder", response_model=list[read_schema])
    def reorder_items(payload: ReorderRequest, db: DbSession):
        """Envoie tous les identifiants dans le nouvel ordre souhaité."""
        return service.reorder(db, payload.ids)

    @router.get("/{item_id}", response_model=read_schema)
    def get_item(item_id: int, db: DbSession):
        return service.get(db, item_id)

    @router.patch("/{item_id}", response_model=read_schema)
    def update_item(item_id: int, payload: update_schema, db: DbSession):
        return service.update(db, item_id, payload.model_dump(exclude_unset=True))

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_item(item_id: int, db: DbSession):
        service.delete(db, item_id)

    return router


projects_router = build_collection_router(
    path="projects",
    tag="Admin · Projets",
    service=collections.projects,
    create_schema=ProjectCreate,
    update_schema=ProjectUpdate,
    read_schema=ProjectRead,
)

services_router = build_collection_router(
    path="services",
    tag="Admin · Services",
    service=collections.services,
    create_schema=ServiceCreate,
    update_schema=ServiceUpdate,
    read_schema=ServiceRead,
)

skill_categories_router = build_collection_router(
    path="skill-categories",
    tag="Admin · Compétences",
    service=collections.skill_categories,
    create_schema=SkillCategoryCreate,
    update_schema=SkillCategoryUpdate,
    read_schema=SkillCategoryRead,
)

experiences_router = build_collection_router(
    path="experiences",
    tag="Admin · Parcours",
    service=collections.experiences,
    create_schema=ExperienceCreate,
    update_schema=ExperienceUpdate,
    read_schema=ExperienceRead,
)

educations_router = build_collection_router(
    path="educations",
    tag="Admin · Formation",
    service=collections.educations,
    create_schema=EducationCreate,
    update_schema=EducationUpdate,
    read_schema=EducationRead,
)

testimonials_router = build_collection_router(
    path="testimonials",
    tag="Admin · Témoignages",
    service=collections.testimonials,
    create_schema=TestimonialCreate,
    update_schema=TestimonialUpdate,
    read_schema=TestimonialRead,
)

social_links_router = build_collection_router(
    path="social-links",
    tag="Admin · Réseaux sociaux",
    service=collections.social_links,
    create_schema=SocialLinkCreate,
    update_schema=SocialLinkUpdate,
    read_schema=SocialLinkRead,
)

routers = [
    projects_router,
    services_router,
    skill_categories_router,
    experiences_router,
    educations_router,
    testimonials_router,
    social_links_router,
]
