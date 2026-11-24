from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from core.deps import CurrentAdmin, DbSession
from core.rate_limit import rate_limit
from core.security import (
    create_2fa_challenge_token,
    create_access_token,
    decode_2fa_challenge_token,
)
from schemas.auth import (
    AdminRead,
    PasswordChange,
    Token,
    TwoFactorCodePayload,
    TwoFactorDisablePayload,
    TwoFactorSetupRead,
    TwoFactorVerifyPayload,
    UsernameChange,
)
from services import auth as auth_service

router = APIRouter(prefix="/api/auth", tags=["Authentification"])


@router.post(
    "/login",
    response_model=Token,
    dependencies=[Depends(rate_limit("login", max_requests=10, window_seconds=60))],
)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession):
    admin = auth_service.authenticate(db, form.username, form.password)
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiant ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if admin.totp_enabled and admin.totp_secret:
        challenge = create_2fa_challenge_token(admin.username)
        return Token(requires_2fa=True, challenge_token=challenge)
    token, expires_in = create_access_token(admin.username, admin.token_version)
    return Token(access_token=token, expires_in=expires_in, requires_2fa=False)


@router.post(
    "/verify-2fa",
    response_model=Token,
    dependencies=[Depends(rate_limit("verify-2fa", max_requests=5, window_seconds=60))],
)
def verify_2fa(payload: TwoFactorVerifyPayload, db: DbSession):
    """Étape 2 de la connexion : valide le code à 6 chiffres et renvoie le vrai token d'accès."""
    username = decode_2fa_challenge_token(payload.challenge_token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session 2FA expirée. Veuillez vous reconnecter.",
        )
    admin = auth_service.verify_2fa_for_username(db, username, payload.code)
    token, expires_in = create_access_token(admin.username, admin.token_version)
    return Token(access_token=token, expires_in=expires_in, requires_2fa=False)


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
    token, expires_in = create_access_token(admin.username, admin.token_version)
    return Token(access_token=token, expires_in=expires_in)


@router.post("/2fa/setup", response_model=TwoFactorSetupRead)
def setup_2fa(admin: CurrentAdmin, db: DbSession):
    """Génère un secret TOTP et l'URI QR code à scanner dans Google Authenticator / Authy."""
    secret, otpauth_uri = auth_service.setup_2fa(db, admin)
    return TwoFactorSetupRead(secret=secret, otpauth_uri=otpauth_uri)


@router.post("/2fa/enable", status_code=status.HTTP_204_NO_CONTENT)
def enable_2fa(payload: TwoFactorCodePayload, admin: CurrentAdmin, db: DbSession):
    """Active la 2FA après vérification du premier code à 6 chiffres."""
    auth_service.enable_2fa(db, admin, payload.code)


@router.post("/2fa/disable", status_code=status.HTTP_204_NO_CONTENT)
def disable_2fa(payload: TwoFactorDisablePayload, admin: CurrentAdmin, db: DbSession):
    """Désactive la 2FA (requiert le mot de passe actuel et un code 2FA valide)."""
    auth_service.disable_2fa(db, admin, payload.current_password, payload.code)
