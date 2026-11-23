from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field, StringConstraints

from schemas.base import (
    CamelModel,
    LongText,
    MediaPath,
    Position,
    RequiredText,
    ShortText,
    partial_model,
)

Slug = Annotated[str, StringConstraints(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=150)]
ProjectType = Literal["web", "mobile", "desktop", "other"]


class ProjectBase(CamelModel):
    title: RequiredText
    description: LongText = ""
    main_image: MediaPath = ""
    images: list[MediaPath] = Field(default_factory=list)
    type: ProjectType = "web"
    category: ShortText = "Web Development"
    technologies: list[RequiredText] = Field(default_factory=list)
    live_url: MediaPath | None = None
    demo_url: MediaPath | None = None
    github_url: MediaPath | None = None


class ProjectCreate(ProjectBase):
    slug: Slug | None = Field(None, description="Généré automatiquement depuis le titre si absent")
    position: Position | None = None
    is_published: bool = True


ProjectUpdate = partial_model(ProjectCreate, "ProjectUpdate")


class ProjectRead(ProjectBase):
    id: int
    slug: str
    position: int
    is_published: bool
    updated_at: datetime
