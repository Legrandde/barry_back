from sqlalchemy.orm import Session

from schemas.content import (
    ContactContent,
    FormationContent,
    ParcoursContent,
    ProjectsContent,
    ServicesContent,
    SiteContent,
    SkillsContent,
    TestimonialsContent,
)
from schemas.education import EducationRead
from schemas.experience import ExperienceRead
from schemas.project import ProjectRead
from schemas.sections import SectionKey
from schemas.service import ServiceRead
from schemas.skill_category import SkillCategoryRead
from schemas.social_link import SocialLinkRead
from schemas.testimonial import TestimonialRead
from services import collections
from services import sections as sections_service


def _section(db: Session, key: SectionKey) -> dict:
    return sections_service.get_content(db, key).model_dump()


def _published[T](db: Session, service: collections.CollectionService, schema: type[T]) -> list[T]:
    return [schema.model_validate(item) for item in service.list(db, published_only=True)]


def _apply_visitor_localization(
    site: dict,
    contact: dict,
    cta: dict,
    visitor_country: str | None,
) -> tuple[dict, dict, dict]:
    """Adapte le numéro et la localisation pour les visiteurs situés au Sénégal (SN)."""
    if (visitor_country or "").upper() != "SN":
        return site, contact, cta

    sn_phone = site.get("senegal_phone")
    sn_location = site.get("senegal_location")
    sn_whatsapp = site.get("senegal_whatsapp_number")

    site = dict(site)
    contact = dict(contact)
    cta = dict(cta)

    if sn_phone:
        site["phone"] = sn_phone
        contact["phone"] = sn_phone
    if sn_location:
        site["location"] = sn_location
        contact["location"] = sn_location
    if sn_whatsapp:
        site["whatsapp_number"] = sn_whatsapp
        if str(cta.get("secondary_cta_href", "")).startswith("tel:"):
            cta["secondary_cta_href"] = f"tel:+{sn_whatsapp}"
    elif sn_phone and str(cta.get("secondary_cta_href", "")).startswith("tel:"):
        cta["secondary_cta_href"] = f"tel:{sn_phone.replace(' ', '')}"

    return site, contact, cta


def get_site_content(db: Session, *, visitor_country: str | None = None) -> SiteContent:
    """Assemble tout le contenu publié du portfolio en une seule réponse."""
    site_data = _section(db, SectionKey.SITE)
    contact_data = _section(db, SectionKey.CONTACT)
    cta_data = _section(db, SectionKey.CTA)
    site_data, contact_data, cta_data = _apply_visitor_localization(
        site_data, contact_data, cta_data, visitor_country
    )

    return SiteContent(
        visibility=sections_service.visibility_map(db),
        theme=_section(db, SectionKey.THEME),
        site=site_data,
        hero=_section(db, SectionKey.HERO),
        about=_section(db, SectionKey.ABOUT),
        services=ServicesContent(
            **_section(db, SectionKey.SERVICES),
            items=_published(db, collections.services, ServiceRead),
        ),
        skills=SkillsContent(
            **_section(db, SectionKey.SKILLS),
            categories=_published(db, collections.skill_categories, SkillCategoryRead),
        ),
        stats=_section(db, SectionKey.STATS),
        parcours=ParcoursContent(
            **_section(db, SectionKey.PARCOURS),
            items=_published(db, collections.experiences, ExperienceRead),
        ),
        formation=FormationContent(
            **_section(db, SectionKey.FORMATION),
            items=_published(db, collections.educations, EducationRead),
        ),
        process=_section(db, SectionKey.PROCESS),
        projects=ProjectsContent(
            **_section(db, SectionKey.PROJECTS),
            items=_published(db, collections.projects, ProjectRead),
        ),
        testimonials=TestimonialsContent(
            **_section(db, SectionKey.TESTIMONIALS),
            items=_published(db, collections.testimonials, TestimonialRead),
        ),
        contact=ContactContent(
            **contact_data,
            socials=_published(db, collections.social_links, SocialLinkRead),
        ),
        cta=cta_data,
    )
