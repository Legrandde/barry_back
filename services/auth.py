from sqlalchemy import func, select
from sqlalchemy.orm import Session

from core.security import hash_password, verify_password
from models import Admin
from services.exceptions import ConflictError, InvalidDataError


def authenticate(db: Session, username: str, password: str) -> Admin | None:
    admin = db.scalar(select(Admin).where(Admin.username == username))
    if admin is None or not verify_password(password, admin.hashed_password):
        return None
    return admin


def change_password(db: Session, admin: Admin, current_password: str, new_password: str) -> None:
    if not verify_password(current_password, admin.hashed_password):
        raise InvalidDataError("Le mot de passe actuel est incorrect.")
    admin.hashed_password = hash_password(new_password)
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


def ensure_admin(db: Session, username: str, password: str) -> None:
    """Crée le compte admin initial si aucun admin n'existe encore."""
    if db.scalar(select(func.count()).select_from(Admin)):
        return
    db.add(Admin(username=username, hashed_password=hash_password(password)))
