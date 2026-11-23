from typing import Any

from fastapi import APIRouter, Request, Response

from core.deps import DbSession
from routers.analytics import _extract_client_ip
from schemas.content import SiteContent
from schemas.project import ProjectRead
from schemas.sections import SectionKey
from services import collections, content, geo
from services import sections as sections_service

router = APIRouter(prefix="/api/public", tags=["Site public"])


def _visitor_country(request: Request) -> str | None:
    ip = _extract_client_ip(request)
    loc = geo.locate(ip)
    if loc["country"]:
        return loc["country"]
    proxy = request.headers.get("cf-ipcountry") or request.headers.get("x-vercel-ip-country")
    if proxy:
        clean = proxy.strip().upper()
        if len(clean) == 2 and clean.isalpha() and clean not in {"XX", "T1"}:
            return clean
    return None


@router.get("/content", response_model=SiteContent)
def get_site_content(request: Request, response: Response, db: DbSession):
    """Tout le contenu publié du portfolio, en un seul appel (adapté au pays du visiteur)."""
    response.headers["Cache-Control"] = "private, no-store"
    return content.get_site_content(db, visitor_country=_visitor_country(request))


@router.get("/sections/{key}")
def get_section(key: SectionKey, db: DbSession) -> dict[str, Any]:
    return sections_service.get_visible_content(db, key).model_dump(by_alias=True, mode="json")


@router.get("/projects/{slug}", response_model=ProjectRead)
def get_project(slug: str, db: DbSession):
    return collections.projects.get_published_by_slug(db, slug)
