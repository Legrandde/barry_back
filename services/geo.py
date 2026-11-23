"""Géolocalisation IP -> pays / région / ville, entièrement locale.

Aucune IP n'est envoyée à un service tiers ni stockée en base.
Base : DB-IP « IP to City Lite » (licence CC BY 4.0, attribution « IP Geolocation by DB-IP »),
téléchargée par `uv run python -m db.download_geoip`.

Sans base (dev ou téléchargement raté), `locate()` renvoie des champs vides sans jamais bloquer.
"""

import ipaddress
import logging
import threading
from functools import lru_cache
from pathlib import Path

from core.config import settings

logger = logging.getLogger("uvicorn.error")

EMPTY_LOCATION: dict[str, str] = {"country": "", "region": "", "city": ""}

_reader = None
_missing = False
_lock = threading.Lock()


def db_path() -> Path:
    return settings.geoip_db_path


def _open_reader():
    global _reader, _missing
    if _reader is not None or _missing:
        return _reader
    with _lock:
        if _reader is None and not _missing:
            try:
                import maxminddb

                _reader = maxminddb.open_database(str(db_path()))
            except Exception as exc:  # fichier absent ou corrompu
                _missing = True
                logger.warning(
                    "Géolocalisation IP locale désactivée (%s) : lancez `uv run python -m db.download_geoip`.",
                    exc,
                )
    return _reader


def is_available() -> bool:
    return _open_reader() is not None


def _localized_name(block: dict | None) -> str:
    names = (block or {}).get("names") or {}
    return str(names.get("fr") or names.get("en") or "")[:120]


@lru_cache(maxsize=4096)
def locate(ip: str) -> dict[str, str]:
    """Retourne {"country": "GN", "region": "Conakry", "city": "Conakry"} ; vides si inconnu."""
    if not ip:
        return EMPTY_LOCATION
    try:
        address = ipaddress.ip_address(str(ip).strip())
    except ValueError:
        return EMPTY_LOCATION
    if not address.is_global:  # localhost, réseau privé : rien à localiser
        return EMPTY_LOCATION
    reader = _open_reader()
    if reader is None:
        return EMPTY_LOCATION
    try:
        record = reader.get(str(address)) or {}
    except Exception:
        return EMPTY_LOCATION
    subdivisions = record.get("subdivisions") or []
    return {
        "country": str(((record.get("country") or {}).get("iso_code")) or "")[:2].upper(),
        "region": _localized_name(subdivisions[0]) if subdivisions else "",
        "city": _localized_name(record.get("city")),
    }


def reset() -> None:
    """Recharge la base au prochain appel (après un téléchargement, et pour les tests)."""
    global _reader, _missing
    with _lock:
        if _reader is not None:
            try:
                _reader.close()
            except Exception:
                pass
        _reader, _missing = None, False
    locate.cache_clear()
