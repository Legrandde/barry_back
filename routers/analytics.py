import ipaddress
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status

from core.deps import DbSession, get_current_admin
from schemas.analytics import AnalyticsSummary, TrackEvent
from services import analytics as analytics_service

public_router = APIRouter(prefix="/api/public", tags=["Site public"])

admin_router = APIRouter(
    prefix="/api/admin/analytics",
    tags=["Admin · Statistiques"],
    dependencies=[Depends(get_current_admin)],
)


def _extract_client_ip(request: Request) -> str:
    """Extrait l'IP réelle derrière un reverse proxy (Cloudflare, Render, Nginx, Vercel...)."""
    candidates: list[str] = []
    if cf_ip := request.headers.get("cf-connecting-ip"):
        candidates.append(cf_ip.strip())
    if xff := request.headers.get("x-forwarded-for"):
        candidates.extend(part.strip() for part in xff.split(",") if part.strip())
    if real_ip := request.headers.get("x-real-ip"):
        candidates.append(real_ip.strip())
    if request.client and request.client.host:
        candidates.append(request.client.host)

    # Privilégie la première IP publique valide, sinon la première IP valide
    first_valid = ""
    for candidate in candidates:
        try:
            addr = ipaddress.ip_address(candidate)
        except ValueError:
            continue
        if addr.is_global:
            return str(addr)
        if not first_valid:
            first_valid = str(addr)
    return first_valid


@public_router.post("/track", status_code=status.HTTP_204_NO_CONTENT)
def track(event: TrackEvent, request: Request, db: DbSession):
    """Enregistre une visite ou une action. Les robots sont ignorés silencieusement."""
    analytics_service.record_event(
        db,
        event,
        ip=_extract_client_ip(request),
        user_agent=request.headers.get("user-agent", ""),
        origin=request.headers.get("origin"),
        accept_language=request.headers.get("accept-language"),
        proxy_country=request.headers.get("cf-ipcountry") or request.headers.get("x-vercel-ip-country"),
        proxy_region=request.headers.get("x-vercel-ip-country-region"),
        proxy_city=request.headers.get("x-vercel-ip-city"),
    )


@admin_router.get("/summary", response_model=AnalyticsSummary)
def summary(db: DbSession, days: Annotated[int, Query(ge=1, le=365)] = 30):
    """Statistiques sur les `days` derniers jours (aujourd'hui inclus)."""
    return analytics_service.get_summary(db, days)
