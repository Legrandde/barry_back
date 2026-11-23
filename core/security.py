import base64
import hashlib
import hmac
import secrets
from datetime import UTC, datetime, timedelta

import jwt

from core.config import settings

# Paramètres scrypt (bibliothèque standard, aucune dépendance native)
_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1

_TWO_FACTOR_EXPIRE_SECONDS = 300  # 5 minutes pour saisir le code 2FA


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=_SCRYPT_N, r=_SCRYPT_R, p=_SCRYPT_P)
    salt_b64 = base64.b64encode(salt).decode()
    digest_b64 = base64.b64encode(digest).decode()
    return f"scrypt${_SCRYPT_N}${_SCRYPT_R}${_SCRYPT_P}${salt_b64}${digest_b64}"


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        algorithm, n, r, p, salt_b64, digest_b64 = hashed_password.split("$")
    except ValueError:
        return False
    if algorithm != "scrypt":
        return False
    expected = base64.b64decode(digest_b64)
    digest = hashlib.scrypt(
        password.encode(),
        salt=base64.b64decode(salt_b64),
        n=int(n),
        r=int(r),
        p=int(p),
        dklen=len(expected),
    )
    return hmac.compare_digest(digest, expected)


def create_access_token(subject: str) -> tuple[str, int]:
    """Retourne le token JWT d'accès complet et sa durée de validité en secondes."""
    expires_in = settings.access_token_expire_minutes * 60
    now = datetime.now(UTC)
    payload = {"sub": subject, "scope": "access", "iat": now, "exp": now + timedelta(seconds=expires_in)}
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    return token, expires_in


def create_2fa_challenge_token(subject: str) -> str:
    """Token temporaire (5 min) utilisable uniquement pour valider le code 2FA."""
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "scope": "2fa",
        "iat": now,
        "exp": now + timedelta(seconds=_TWO_FACTOR_EXPIRE_SECONDS),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> str | None:
    """Retourne le username si le token est un vrai token d'accès (refuse les tokens 2fa)."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        return None
    if payload.get("scope") == "2fa":
        return None
    return payload.get("sub")


def decode_2fa_challenge_token(token: str) -> str | None:
    """Retourne le username si le token est un challenge 2FA valide."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        return None
    if payload.get("scope") != "2fa":
        return None
    return payload.get("sub")
