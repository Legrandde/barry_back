"""Authentification à deux facteurs TOTP (RFC 6238), 100 % bibliothèque standard Python.

Compatible avec Google Authenticator, Authy, Microsoft Authenticator, 1Password, Bitwarden...
"""

import base64
import hashlib
import hmac
import secrets
import struct
import time
from urllib.parse import quote

TOTP_PERIOD = 30
TOTP_DIGITS = 6
TOTP_ISSUER = "Barry Portfolio Admin"


def generate_secret() -> str:
    """Génère un secret Base32 aléatoire de 160 bits (sans padding '=')."""
    return base64.b32encode(secrets.token_bytes(20)).decode("ascii").rstrip("=")


def _decode_secret(secret: str) -> bytes:
    cleaned = secret.strip().replace(" ", "").upper()
    padding = (-len(cleaned)) % 8
    return base64.b32decode(cleaned + ("=" * padding), casefold=True)


def totp_at(secret: str, timestamp: float | None = None, *, offset_steps: int = 0) -> str:
    """Calcule le code TOTP à 6 chiffres pour un instant donné."""
    counter = int((timestamp if timestamp is not None else time.time()) // TOTP_PERIOD) + offset_steps
    key = _decode_secret(secret)
    msg = struct.pack(">Q", counter)
    digest = hmac.new(key, msg, hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    code = (struct.unpack(">I", digest[offset : offset + 4])[0] & 0x7FFFFFFF) % (10**TOTP_DIGITS)
    return f"{code:0{TOTP_DIGITS}d}"


def verify_totp(secret: str, code: str, *, valid_window: int = 1) -> bool:
    """Vérifie un code TOTP à 6 chiffres (tolérance ±1 fenêtre de 30 s)."""
    cleaned = code.strip().replace(" ", "")
    if not (len(cleaned) == TOTP_DIGITS and cleaned.isdigit()):
        return False
    now = time.time()
    for step in range(-valid_window, valid_window + 1):
        if hmac.compare_digest(totp_at(secret, now, offset_steps=step), cleaned):
            return True
    return False


def build_otpauth_uri(secret: str, username: str, issuer: str = TOTP_ISSUER) -> str:
    """Construit l'URI otpauth:// à encoder en QR code pour l'application Authenticator."""
    label = quote(f"{issuer}:{username}")
    return f"otpauth://totp/{label}?secret={secret}&issuer={quote(issuer)}&algorithm=SHA1&digits={TOTP_DIGITS}&period={TOTP_PERIOD}"
