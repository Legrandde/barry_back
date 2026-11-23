from datetime import datetime
from typing import Literal

from schemas.base import CamelModel


class MediaRead(CamelModel):
    id: int
    filename: str
    original_name: str
    content_type: str
    size: int
    status: Literal["processing", "ready"]
    original_size: int | None
    url: str
    created_at: datetime
