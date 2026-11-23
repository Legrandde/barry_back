from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.security import decode_access_token
from db.session import get_db
from models import Admin

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

DbSession = Annotated[Session, Depends(get_db)]


def get_current_admin(token: Annotated[str, Depends(oauth2_scheme)], db: DbSession) -> Admin:
    username = decode_access_token(token)
    admin = db.scalar(select(Admin).where(Admin.username == username)) if username else None
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session invalide ou expirée. Veuillez vous reconnecter.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return admin


CurrentAdmin = Annotated[Admin, Depends(get_current_admin)]
