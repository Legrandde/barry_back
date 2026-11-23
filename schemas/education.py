from datetime import datetime

from pydantic import Field

from schemas.base import CamelModel, LongText, Position, RequiredText, partial_model


class EducationBase(CamelModel):
    degree: RequiredText
    institution: RequiredText
    period: RequiredText
    description: LongText = ""
    achievements: list[RequiredText] = Field(default_factory=list)


class EducationCreate(EducationBase):
    position: Position | None = None
    is_published: bool = True


EducationUpdate = partial_model(EducationCreate, "EducationUpdate")


class EducationRead(EducationBase):
    id: int
    position: int
    is_published: bool
    updated_at: datetime
