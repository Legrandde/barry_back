"""Limiteur de débit en mémoire (fenêtre glissante) pour protéger auth et routes publiques."""

import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

_lock = threading.Lock()
_buckets: dict[tuple[str, str], deque[float]] = defaultdict(deque)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        first = forwarded.split(",")[0].strip()
        if first:
            return first
    return request.client.host if request.client else "unknown"


def reset_rate_limits() -> None:
    """Vide tous les compteurs (utile entre les tests unitaires)."""
    with _lock:
        _buckets.clear()


def rate_limit(scope: str, max_requests: int, window_seconds: int):
    """Dépendance FastAPI qui renvoie HTTP 429 si la limite est dépassée."""

    def _dependency(request: Request) -> None:
        now = time.monotonic()
        cutoff = now - window_seconds
        key = (scope, _client_ip(request))
        with _lock:
            bucket = _buckets[key]
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= max_requests:
                retry_after = max(1, int(window_seconds - (now - bucket[0])))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Trop de tentatives. Veuillez réessayer dans quelques instants.",
                    headers={"Retry-After": str(retry_after)},
                )
            bucket.append(now)

    return _dependency
