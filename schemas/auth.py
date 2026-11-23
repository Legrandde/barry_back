from datetime import datetime

from pydantic import BaseModel, Field

from schemas.base import CamelModel


class Token(BaseModel):
    # Format standard OAuth2 (snake_case attendu par les clients OAuth2 / Swagger)
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class AdminRead(CamelModel):
    id: int
    username: str
    created_at: datetime


class PasswordChange(CamelModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class UsernameChange(CamelModel):
    current_password: str
    new_username: str = Field(min_length=3, max_length=100, pattern=r"^\S+$")
