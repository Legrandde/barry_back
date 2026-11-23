from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field

from schemas.base import CamelModel, Position, RequiredText, partial_model

SkillIcon = Literal["code", "database", "mobile", "cloud", "tools", "default"]
SkillLevel = Annotated[int, Field(ge=0, le=100)]


class SkillEntry(CamelModel):
    name: RequiredText
    level: SkillLevel


class SkillCategoryBase(CamelModel):
    name: RequiredText
    icon: SkillIcon = "code"
    skills: list[SkillEntry] = Field(default_factory=list)


class SkillCategoryCreate(SkillCategoryBase):
    position: Position | None = None
    is_published: bool = True


SkillCategoryUpdate = partial_model(SkillCategoryCreate, "SkillCategoryUpdate")


class SkillCategoryRead(SkillCategoryBase):
    id: int
    position: int
    is_published: bool
    updated_at: datetime
