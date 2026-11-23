"""Schémas des blocs de contenu uniques du portfolio d'Alhassane Barry.

Dans les titres, un retour à la ligne (\\n) correspond à un <br /> dans le site.
"""

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Any, Literal

from pydantic import Field, StringConstraints

from schemas.base import CamelModel, LongText, MediaPath, RequiredText, ShortText


class SectionKey(StrEnum):
    SITE = "site"
    THEME = "theme"
    HERO = "hero"
    ABOUT = "about"
    SERVICES = "services"
    SKILLS = "skills"
    STATS = "stats"
    PARCOURS = "parcours"
    FORMATION = "formation"
    PROCESS = "process"
    PROJECTS = "projects"
    TESTIMONIALS = "testimonials"
    CONTACT = "contact"
    CTA = "cta"


class SiteSection(CamelModel):
    """Informations générales : en-tête, bouton WhatsApp, coordonnées et pied de page."""

    first_name: RequiredText
    last_name: RequiredText
    tagline: ShortText
    location: ShortText
    phone: ShortText
    email: Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")]
    whatsapp_number: Annotated[str, StringConstraints(pattern=r"^\d{6,15}$")] = Field(
        description="Numéro international sans + ni espaces, ex: 224626014552"
    )
    senegal_location: ShortText = Field(
        "Dakar, Guédiawaye",
        description="Localisation affichée automatiquement aux visiteurs situés au Sénégal",
    )
    senegal_phone: ShortText = Field(
        "+221 77 487 40 73",
        description="Numéro affiché automatiquement aux visiteurs situés au Sénégal",
    )
    senegal_whatsapp_number: Annotated[str, StringConstraints(pattern=r"^$|^\d{6,15}$")] = Field(
        "221774874073",
        description="Numéro WhatsApp (sans + ni espaces) pour les visiteurs situés au Sénégal",
    )
    footer_description: LongText
    footer_tagline: ShortText


# Polices proposées
HeadingFont = Literal[
    "Inter",
    "Poppins",
    "Montserrat",
    "DM Sans",
    "Satoshi",
    "Bricolage Grotesque",
    "Playfair Display",
    "Lora",
    "system-sans",
]
BodyFont = Literal[
    "Inter",
    "DM Sans",
    "Manrope",
    "Poppins",
    "Lato",
    "Open Sans",
    "Nunito",
    "Satoshi",
    "system-sans",
]


class ThemeSection(CamelModel):
    """Charte graphique : couleur d'accentuation, mode par défaut et polices."""

    accent_color: Annotated[str, StringConstraints(pattern=r"^#[0-9a-fA-F]{6}$")] = Field(
        description="Couleur principale, format #RRGGBB (ex: #f59e0b)"
    )
    default_mode: Literal["light", "dark", "system"] = "light"
    heading_font: HeadingFont = "Inter"
    body_font: BodyFont = "Inter"


class HeroSection(CamelModel):
    """Bannière principale (Banner) en haut du portfolio."""

    greeting: ShortText = "Bonjour, je suis"
    first_name: RequiredText
    last_name: RequiredText
    role: RequiredText
    description: LongText
    image: MediaPath = ""
    image_alt: ShortText = ""
    cta_label: RequiredText
    cta_href: ShortText = "#projets"
    tech_logos: list[ShortText] = Field(
        default_factory=list,
        max_length=12,
        description="Clés des logos flottants autour du portrait (github, docker, django, laravel, react, tailwindcss, nestjs, postgresql...)",
    )


class AboutSection(CamelModel):
    """Section « À propos »."""

    eyebrow: ShortText
    title: RequiredText
    image: MediaPath = ""
    image_alt: ShortText = ""
    paragraphs: list[LongText] = Field(min_length=1)
    cta_label: RequiredText
    cta_href: ShortText = "#contact"


class ServicesSection(CamelModel):
    """En-tête de la section « Services »."""

    eyebrow: ShortText
    title: RequiredText
    description: LongText = ""


class SkillsSection(CamelModel):
    """En-tête de la section « Compétences »."""

    eyebrow: ShortText
    title: RequiredText
    description: LongText = ""


StatIcon = Literal["projects", "users", "award", "code", "clock", "star", "default"]


class StatItem(CamelModel):
    """Chiffre clé animé dans la section « En quelques chiffres »."""

    value: Annotated[int, Field(ge=0)]
    suffix: ShortText = "+"
    label: RequiredText
    icon: StatIcon = "projects"
    color: ShortText = Field("from-amber-500 to-amber-600", description="Dégradé Tailwind, ex: from-blue-500 to-blue-600")


class StatsSection(CamelModel):
    """Section « Réalisations / En quelques chiffres »."""

    eyebrow: ShortText
    title: RequiredText
    items: list[StatItem] = Field(default_factory=list, max_length=6)


class ParcoursSection(CamelModel):
    """En-tête de la section « Parcours professionnel »."""

    eyebrow: ShortText
    title: RequiredText
    description: LongText = ""


class FormationSection(CamelModel):
    """En-tête de la section « Parcours académique / Formation »."""

    eyebrow: ShortText
    title: RequiredText
    description: LongText = ""


ProcessIcon = Literal["search", "lightbulb", "code", "rocket", "check", "default"]


class ProcessStep(CamelModel):
    """Étape de la méthodologie de travail."""

    number: RequiredText = Field(description="Numéro affiché, ex: 01")
    title: RequiredText
    description: LongText = ""
    icon: ProcessIcon = "code"


class ProcessSection(CamelModel):
    """Section « Comment je travaille »."""

    eyebrow: ShortText
    title: RequiredText
    description: LongText = ""
    steps: list[ProcessStep] = Field(default_factory=list, max_length=8)


class ProjectsSection(CamelModel):
    """En-tête de la section « Mes réalisations »."""

    eyebrow: ShortText
    title: RequiredText
    description: LongText = ""


class TestimonialsSection(CamelModel):
    """En-tête de la section « Témoignages »."""

    eyebrow: ShortText
    title: RequiredText
    description: LongText = ""


class ContactSection(CamelModel):
    """Section « Contact » et coordonnées affichées à côté du formulaire."""

    eyebrow: ShortText
    title: RequiredText
    description: LongText = ""
    email: Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")]
    phone: ShortText
    location: ShortText
    cta_label: RequiredText


class CtaSection(CamelModel):
    """Bandeau d'appel à l'action (CTA) avant le pied de page."""

    title: RequiredText
    highlight_word: ShortText = ""
    description: LongText = ""
    primary_cta_label: RequiredText
    primary_cta_href: ShortText = "#contact"
    secondary_cta_label: ShortText = ""
    secondary_cta_href: ShortText = ""
    footnote: ShortText = ""


SECTION_SCHEMAS: dict[SectionKey, type[CamelModel]] = {
    SectionKey.SITE: SiteSection,
    SectionKey.THEME: ThemeSection,
    SectionKey.HERO: HeroSection,
    SectionKey.ABOUT: AboutSection,
    SectionKey.SERVICES: ServicesSection,
    SectionKey.SKILLS: SkillsSection,
    SectionKey.STATS: StatsSection,
    SectionKey.PARCOURS: ParcoursSection,
    SectionKey.FORMATION: FormationSection,
    SectionKey.PROCESS: ProcessSection,
    SectionKey.PROJECTS: ProjectsSection,
    SectionKey.TESTIMONIALS: TestimonialsSection,
    SectionKey.CONTACT: ContactSection,
    SectionKey.CTA: CtaSection,
}


# Sections qu'on peut masquer : celles affichées comme un bloc de la page
HIDEABLE_SECTIONS = frozenset(SectionKey) - {SectionKey.SITE, SectionKey.THEME}


class SectionRead(CamelModel):
    key: SectionKey
    is_visible: bool
    content: dict[str, Any]
    updated_at: datetime


class SectionVisibilityUpdate(CamelModel):
    is_visible: bool


class SectionVisibility(CamelModel):
    key: SectionKey
    is_visible: bool
    hideable: bool
