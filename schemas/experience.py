from datetime import datetime

from pydantic import Field

from schemas.base import CamelModel, LongText, Position, RequiredText, partial_model


class ExperienceBase(CamelModel):
    title: RequiredText
    company: RequiredText
    period: RequiredText
    description: LongText = ""
    technologies: list[RequiredText] = Field(default_factory=list)


class ExperienceCreate(ExperienceBase):
    position: Position | None = None
    is_published: bool = True


ExperienceUpdate = partial_model(ExperienceCreate, "ExperienceUpdate")


class ExperienceRead(ExperienceBase):
    id: int
    position: int
    is_published: bool
    updated_at: datetime
