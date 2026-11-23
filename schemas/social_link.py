from datetime import datetime
from typing import Literal

from schemas.base import CamelModel, MediaPath, Position, RequiredText, partial_model

SocialIcon = Literal[
    "github",
    "linkedin",
    "x",
    "twitter",
    "facebook",
    "instagram",
    "youtube",
    "tiktok",
    "whatsapp",
    "website",
    "email",
]


class SocialLinkBase(CamelModel):
    label: RequiredText
    url: MediaPath
    icon: SocialIcon = "website"


class SocialLinkCreate(SocialLinkBase):
    position: Position | None = None
    is_published: bool = True


SocialLinkUpdate = partial_model(SocialLinkCreate, "SocialLinkUpdate")


class SocialLinkRead(SocialLinkBase):
    id: int
    position: int
    is_published: bool
    updated_at: datetime
