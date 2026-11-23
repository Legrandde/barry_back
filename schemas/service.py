from datetime import datetime
from typing import Literal

from schemas.base import CamelModel, LongText, Position, RequiredText, partial_model

ServiceIcon = Literal["web", "mobile", "api", "consulting", "code", "cloud", "design", "default"]


class ServiceBase(CamelModel):
    title: RequiredText
    description: LongText = ""
    icon: ServiceIcon = "code"


class ServiceCreate(ServiceBase):
    position: Position | None = None
    is_published: bool = True


ServiceUpdate = partial_model(ServiceCreate, "ServiceUpdate")


class ServiceRead(ServiceBase):
    id: int
    position: int
    is_published: bool
    updated_at: datetime
