from sqlalchemy import func, select
from sqlalchemy.orm import Session

from core.security import hash_password, verify_password
from core.totp import build_otpauth_uri, generate_secret, verify_totp
from models import Admin
from services.exceptions import ConflictError, InvalidDataError


_DUMMY_HASH = hash_password("timing-padding-placeholder-not-used")


def authenticate(db: Session, username: str, password: str) -> Admin | None:
    admin = db.scalar(select(Admin).where(Admin.username == username))
    if admin is None:
        verify_password(password, _DUMMY_HASH)
        return None
    if not verify_password(password, admin.hashed_password):
        return None
    return admin


def change_password(db: Session, admin: Admin, current_password: str, new_password: str) -> None:
    if not verify_password(current_password, admin.hashed_password):
        raise InvalidDataError("Le mot de passe actuel est incorrect.")
    admin.hashed_password = hash_password(new_password)
    admin.token_version += 1
    db.commit()


def change_username(db: Session, admin: Admin, current_password: str, new_username: str) -> None:
    if not verify_password(current_password, admin.hashed_password):
        raise InvalidDataError("Le mot de passe actuel est incorrect.")
    if new_username == admin.username:
        return
    if db.scalar(select(Admin).where(Admin.username == new_username)):
        raise ConflictError("Cet identifiant est déjà utilisé.")
    admin.username = new_username
    db.commit()


def setup_2fa(db: Session, admin: Admin) -> tuple[str, str]:
    """Génère un secret TOTP en attente de confirmation."""
    secret = generate_secret()
    admin.totp_secret = secret
    admin.totp_enabled = False
    db.commit()
    return secret, build_otpauth_uri(secret, admin.username)


def enable_2fa(db: Session, admin: Admin, code: str) -> None:
    if not admin.totp_secret:
        raise InvalidDataError("Veuillez d'abord initialiser la configuration 2FA.")
    if not verify_totp(admin.totp_secret, code):
        raise InvalidDataError("Code d'authentification invalide ou expiré.")
    admin.totp_enabled = True
    db.commit()


def disable_2fa(db: Session, admin: Admin, current_password: str, code: str) -> None:
    if not verify_password(current_password, admin.hashed_password):
        raise InvalidDataError("Le mot de passe actuel est incorrect.")
    if admin.totp_enabled and admin.totp_secret and not verify_totp(admin.totp_secret, code):
        raise InvalidDataError("Code 2FA invalide.")
    admin.totp_enabled = False
    admin.totp_secret = None
    db.commit()


def verify_2fa_for_username(db: Session, username: str, code: str) -> Admin:
    admin = db.scalar(select(Admin).where(Admin.username == username))
    if admin is None or not admin.totp_enabled or not admin.totp_secret:
        raise InvalidDataError("Session 2FA invalide.")
    if not verify_totp(admin.totp_secret, code):
        raise InvalidDataError("Code 2FA invalide ou expiré.")
    return admin


def ensure_admin(db: Session, username: str, password: str) -> None:
    """Crée le compte admin initial si aucun admin n'existe encore."""
    if db.scalar(select(func.count()).select_from(Admin)):
        return
    db.add(Admin(username=username, hashed_password=hash_password(password)))
