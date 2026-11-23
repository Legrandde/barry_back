from datetime import datetime
from typing import Annotated

from pydantic import Field

from schemas.base import CamelModel, LongText, MediaPath, Position, RequiredText, ShortText, partial_model

Rating = Annotated[int, Field(ge=1, le=5)]


class TestimonialBase(CamelModel):
    name: RequiredText
    role: ShortText = ""
    company: ShortText = ""
    image: MediaPath = ""
    rating: Rating = 5
    text: LongText = ""


class TestimonialCreate(TestimonialBase):
    position: Position | None = None
    is_published: bool = True


TestimonialUpdate = partial_model(TestimonialCreate, "TestimonialUpdate")


class TestimonialRead(TestimonialBase):
    id: int
    position: int
    is_published: bool
    updated_at: datetime
