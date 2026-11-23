"""Contenu complet du portfolio, tel que consommé par le front en un seul appel."""

from schemas.base import CamelModel
from schemas.education import EducationRead
from schemas.experience import ExperienceRead
from schemas.project import ProjectRead
from schemas.sections import (
    AboutSection,
    ContactSection,
    CtaSection,
    FormationSection,
    HeroSection,
    ParcoursSection,
    ProcessSection,
    ProjectsSection,
    ServicesSection,
    SiteSection,
    SkillsSection,
    StatsSection,
    TestimonialsSection,
    ThemeSection,
)
from schemas.service import ServiceRead
from schemas.skill_category import SkillCategoryRead
from schemas.social_link import SocialLinkRead
from schemas.testimonial import TestimonialRead


class ServicesContent(ServicesSection):
    items: list[ServiceRead]


class SkillsContent(SkillsSection):
    categories: list[SkillCategoryRead]


class ParcoursContent(ParcoursSection):
    items: list[ExperienceRead]


class FormationContent(FormationSection):
    items: list[EducationRead]


class ProjectsContent(ProjectsSection):
    items: list[ProjectRead]


class TestimonialsContent(TestimonialsSection):
    items: list[TestimonialRead]


class ContactContent(ContactSection):
    socials: list[SocialLinkRead]


class SiteContent(CamelModel):
    # Clé de section -> affichée ou non (les sections masquées ne doivent pas être rendues)
    visibility: dict[str, bool]
    theme: ThemeSection
    site: SiteSection
    hero: HeroSection
    about: AboutSection
    services: ServicesContent
    skills: SkillsContent
    stats: StatsSection
    parcours: ParcoursContent
    formation: FormationContent
    process: ProcessSection
    projects: ProjectsContent
    testimonials: TestimonialsContent
    contact: ContactContent
    cta: CtaSection
