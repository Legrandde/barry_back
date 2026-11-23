from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from core.deps import CurrentAdmin, DbSession
from core.security import create_access_token
from schemas.auth import AdminRead, PasswordChange, Token, UsernameChange
from services import auth as auth_service

router = APIRouter(prefix="/api/auth", tags=["Authentification"])


@router.post("/login", response_model=Token)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession):
    admin = auth_service.authenticate(db, form.username, form.password)
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiant ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token, expires_in = create_access_token(admin.username)
    return Token(access_token=token, expires_in=expires_in)


@router.get("/me", response_model=AdminRead)
def me(admin: CurrentAdmin):
    return admin


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(payload: PasswordChange, admin: CurrentAdmin, db: DbSession):
    auth_service.change_password(db, admin, payload.current_password, payload.new_password)


@router.put("/username", response_model=Token)
def change_username(payload: UsernameChange, admin: CurrentAdmin, db: DbSession):
    """Le token porte l'identifiant : un nouveau token est renvoyé, l'ancien devient invalide."""
    auth_service.change_username(db, admin, payload.current_password, payload.new_username)
    token, expires_in = create_access_token(admin.username)
    return Token(access_token=token, expires_in=expires_in)
