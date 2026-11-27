from datetime import date, datetime
from typing import Literal

from pydantic import Field

from schemas.base import CamelModel, LongText, MediaPath, RequiredText, SafeUrl, ShortText, partial_model

ProspectStatus = Literal[
    "a_prospecter",
    "a_contacter",
    "contacte",
    "en_discussion",
    "proposition_envoyee",
    "en_negociation",
    "gagne",
    "perdu",
    "en_pause",
]

ProspectPriority = Literal["basse", "moyenne", "haute", "urgente"]

InteractionType = Literal["email", "appel", "rendez_vous", "relance", "proposition", "note", "statut"]


class ProspectSocialLink(CamelModel):
    label: RequiredText
    url: SafeUrl


class ProspectBase(CamelModel):
    name: RequiredText
    cover_image: MediaPath = ""
    logo: MediaPath = ""
    description: LongText = ""
    sector: ShortText = ""
    location: ShortText = ""
    website: SafeUrl = ""
    social_links: list[ProspectSocialLink] = Field(default_factory=list)

    contact_name: ShortText = ""
    contact_role: ShortText = ""
    contact_email: ShortText = ""
    contact_phone: ShortText = ""
    identified_need: LongText = ""
    proposed_service: ShortText = ""
    estimated_budget: ShortText = ""
    priority: ProspectPriority = "moyenne"

    status: ProspectStatus = "a_prospecter"
    first_contact_date: date | None = None
    last_contact_date: date | None = None
    next_follow_up_date: date | None = None
    next_action: ShortText = ""
    notes: LongText = ""
    is_archived: bool = False


class ProspectCreate(ProspectBase):
    pass


ProspectUpdate = partial_model(ProspectBase, "ProspectUpdate")


class ProspectInteractionCreate(CamelModel):
    type: InteractionType = "note"
    title: RequiredText
    content: LongText = ""
    interaction_date: datetime | None = None


class ProspectInteractionRead(CamelModel):
    id: int
    prospect_id: int
    type: InteractionType
    title: str
    content: str
    interaction_date: datetime
    created_at: datetime


class ProspectDocumentRead(CamelModel):
    id: int
    prospect_id: int
    filename: str
    original_name: str
    content_type: str
    size: int
    url: str
    created_at: datetime


class ProspectRead(ProspectBase):
    id: int
    created_at: datetime
    updated_at: datetime


class ProspectDetailRead(ProspectRead):
    interactions: list[ProspectInteractionRead] = Field(default_factory=list)
    documents: list[ProspectDocumentRead] = Field(default_factory=list)


class ProspectStatsRead(CamelModel):
    total: int
    a_contacter: int
    en_discussion: int
    propositions_envoyees: int
    gagnes: int
    archived: int
    overdue_follow_ups: int
    today_follow_ups: int
