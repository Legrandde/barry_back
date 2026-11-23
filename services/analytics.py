import hashlib
import ipaddress
from datetime import UTC, date, datetime, time, timedelta
from urllib.parse import unquote, urlsplit

from sqlalchemy import ColumnElement, delete, distinct, func, select
from sqlalchemy.orm import Session

from core.config import settings
from models import AnalyticsEvent
from schemas.analytics import (
    PAGEVIEW,
    AnalyticsSummary,
    CountItem,
    CountryStat,
    DailyStat,
    EventCount,
    PeriodTotals,
    RegionStat,
    TrackEvent,
)
from services import geo

ACTIVE_WINDOW = timedelta(minutes=5)

_BOT_MARKERS = (
    "bot", "crawl", "spider", "slurp", "headless", "lighthouse", "preview",
    "curl", "wget", "python-requests", "httpx", "facebookexternalhit", "whatsapp",
)


# --- Analyse du visiteur -------------------------------------------------------------

def normalize_ip(raw_ip: str | None) -> str:
    """Nettoie une adresse IP et unifie localhost IPv6 (::1) sur 127.0.0.1."""
    if not raw_ip:
        return ""
    candidate = raw_ip.strip()
    try:
        addr = ipaddress.ip_address(candidate)
    except ValueError:
        return candidate
    if addr.is_loopback:
        return "127.0.0.1"
    return str(addr)


def is_bot(user_agent: str) -> bool:
    ua = user_agent.lower()
    return not ua or any(marker in ua for marker in _BOT_MARKERS)


def visitor_hash(ip: str, user_agent: str, day: date) -> str:
    """Identifiant anonyme : impossible de retrouver l'IP, et il change chaque jour."""
    raw = f"{settings.secret_key}|{day.isoformat()}|{normalize_ip(ip)}|{user_agent}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def parse_device(ua: str) -> str:
    if "iPad" in ua or "Tablet" in ua or ("Android" in ua and "Mobile" not in ua):
        return "Tablette"
    if "Mobi" in ua or "iPhone" in ua:
        return "Mobile"
    return "Ordinateur"


def parse_browser(ua: str) -> str:
    for marker, name in (
        ("Edg/", "Edge"),
        ("OPR/", "Opera"),
        ("SamsungBrowser", "Samsung Internet"),
        ("Firefox/", "Firefox"),
        ("FxiOS", "Firefox"),
        ("CriOS", "Chrome"),
        ("Chrome/", "Chrome"),
        ("Safari/", "Safari"),
    ):
        if marker in ua:
            return name
    return "Autre"


def parse_os(ua: str) -> str:
    for marker, name in (
        ("Windows", "Windows"),
        ("Android", "Android"),
        ("iPhone", "iOS"),
        ("iPad", "iOS"),
        ("Mac OS X", "macOS"),
        ("Linux", "Linux"),
    ):
        if marker in ua:
            return name
    return "Autre"


def _host(url: str | None) -> str | None:
    if not url:
        return None
    host = urlsplit(url).hostname
    return host.removeprefix("www.") if host else None


def referrer_host(referrer: str | None, origin: str | None) -> str | None:
    """Domaine d'où vient le visiteur ; None pour un accès direct ou une navigation interne."""
    host = _host(referrer)
    if host is None or host == _host(origin):
        return None
    return host[:255]


def _clean_country(code: str | None) -> str | None:
    if not code:
        return None
    clean = code.strip().upper()
    if len(clean) == 2 and clean.isalpha() and clean not in {"XX", "T1"}:
        return clean
    return None


def _resolve_location(
    ip: str,
    *,
    proxy_country: str | None = None,
    proxy_region: str | None = None,
    proxy_city: str | None = None,
) -> tuple[str | None, str | None, str | None]:
    """Déduit pays/région/ville via la base locale DB-IP, avec secours par en-têtes proxy."""
    loc = geo.locate(ip)
    country = _clean_country(loc["country"]) or _clean_country(proxy_country)
    region = (loc["region"] or (unquote(proxy_region).strip() if proxy_region else ""))[:120] or None
    city = (loc["city"] or (unquote(proxy_city).strip() if proxy_city else ""))[:120] or None
    return country, region, city


# --- Enregistrement ------------------------------------------------------------------

def record_event(
    db: Session,
    event: TrackEvent,
    *,
    ip: str,
    user_agent: str,
    origin: str | None,
    accept_language: str | None,
    proxy_country: str | None = None,
    proxy_region: str | None = None,
    proxy_city: str | None = None,
) -> bool:
    """Enregistre l'événement. Retourne False s'il a été ignoré (robot)."""
    if is_bot(user_agent):
        return False
    now = datetime.now(UTC)
    language = (accept_language or "")[:2].lower() or None
    clean_ip = normalize_ip(ip)
    country, region, city = _resolve_location(
        clean_ip,
        proxy_country=proxy_country,
        proxy_region=proxy_region,
        proxy_city=proxy_city,
    )
    db.add(
        AnalyticsEvent(
            created_at=now,
            name=event.name,
            label=event.label or None,
            path=event.path or "/",
            referrer=referrer_host(event.referrer, origin),
            utm_source=event.utm_source or None,
            visitor_hash=visitor_hash(clean_ip, user_agent, now.date()),
            device=parse_device(user_agent),
            browser=parse_browser(user_agent),
            os=parse_os(user_agent),
            language=language if language and language.isalpha() else None,
            country=country,
            region=region,
            city=city,
        )
    )
    db.commit()
    return True


def purge_old_events(db: Session) -> None:
    limit = datetime.now(UTC) - timedelta(days=settings.analytics_retention_days)
    db.execute(delete(AnalyticsEvent).where(AnalyticsEvent.created_at < limit))


# --- Statistiques --------------------------------------------------------------------

_visitors = func.count(distinct(AnalyticsEvent.visitor_hash))
_is_pageview = AnalyticsEvent.name == PAGEVIEW


def _totals(db: Session, since: ColumnElement[bool]) -> PeriodTotals:
    pageviews, visitors = db.execute(
        select(func.count(), _visitors).where(since, _is_pageview)
    ).one()
    events = db.scalar(select(func.count()).where(since, AnalyticsEvent.name != PAGEVIEW))
    return PeriodTotals(pageviews=pageviews, unique_visitors=visitors, events=events or 0)


def _breakdown(db: Session, column, since: ColumnElement[bool], *, empty: str, limit: int = 10) -> list[CountItem]:
    """Répartition des visiteurs uniques selon une colonne (appareil, navigateur, provenance...)."""
    rows = db.execute(
        select(column, _visitors.label("total"))
        .where(since, _is_pageview)
        .group_by(column)
        .order_by(_visitors.desc())
        .limit(limit)
    )
    return [CountItem(name=value or empty, count=total) for value, total in rows]


def _countries(db: Session, since: ColumnElement[bool], limit: int = 20) -> list[CountryStat]:
    rows = db.execute(
        select(AnalyticsEvent.country, _visitors.label("visitors"), func.count().label("pageviews"))
        .where(since, _is_pageview)
        .group_by(AnalyticsEvent.country)
        .order_by(_visitors.desc(), func.count().desc())
        .limit(limit)
    )
    return [CountryStat(code=code or "", visitors=visitors, pageviews=pageviews) for code, visitors, pageviews in rows]


def _regions(db: Session, since: ColumnElement[bool], limit: int = 20) -> list[RegionStat]:
    rows = db.execute(
        select(
            AnalyticsEvent.country,
            AnalyticsEvent.region,
            _visitors.label("visitors"),
            func.count().label("pageviews"),
        )
        .where(since, _is_pageview, AnalyticsEvent.region.is_not(None), AnalyticsEvent.region != "")
        .group_by(AnalyticsEvent.country, AnalyticsEvent.region)
        .order_by(_visitors.desc(), func.count().desc())
        .limit(limit)
    )
    return [
        RegionStat(country=country or "", region=region, visitors=visitors, pageviews=pageviews)
        for country, region, visitors, pageviews in rows
    ]


def get_summary(db: Session, days: int) -> AnalyticsSummary:
    now = datetime.now(UTC)
    end_date = now.date()
    start_date = end_date - timedelta(days=days - 1)
    since = AnalyticsEvent.created_at >= datetime.combine(start_date, time.min, tzinfo=UTC)
    today = AnalyticsEvent.created_at >= datetime.combine(end_date, time.min, tzinfo=UTC)

    day = func.date(AnalyticsEvent.created_at)
    per_day = {
        str(value): (pageviews, visitors)
        for value, pageviews, visitors in db.execute(
            select(day, func.count(), _visitors).where(since, _is_pageview).group_by(day)
        )
    }
    daily = []
    for offset in range(days):
        current = start_date + timedelta(days=offset)
        pageviews, visitors = per_day.get(current.isoformat(), (0, 0))
        daily.append(DailyStat(date=current, pageviews=pageviews, unique_visitors=visitors))

    top_pages = [
        CountItem(name=path, count=total)
        for path, total in db.execute(
            select(AnalyticsEvent.path, func.count().label("total"))
            .where(since, _is_pageview)
            .group_by(AnalyticsEvent.path)
            .order_by(func.count().desc())
            .limit(10)
        )
    ]
    events = [
        EventCount(name=name, label=label, count=total)
        for name, label, total in db.execute(
            select(AnalyticsEvent.name, AnalyticsEvent.label, func.count().label("total"))
            .where(since, AnalyticsEvent.name != PAGEVIEW)
            .group_by(AnalyticsEvent.name, AnalyticsEvent.label)
            .order_by(func.count().desc())
            .limit(30)
        )
    ]
    active = db.scalar(select(_visitors).where(AnalyticsEvent.created_at >= now - ACTIVE_WINDOW))

    return AnalyticsSummary(
        start_date=start_date,
        end_date=end_date,
        days=days,
        geo_available=geo.is_available(),
        totals=_totals(db, since),
        today=_totals(db, today),
        active_visitors=active or 0,
        daily=daily,
        top_pages=top_pages,
        countries=_countries(db, since),
        regions=_regions(db, since),
        referrers=_breakdown(db, AnalyticsEvent.referrer, since, empty="Accès direct"),
        utm_sources=_breakdown(db, AnalyticsEvent.utm_source, since, empty="Aucune"),
        devices=_breakdown(db, AnalyticsEvent.device, since, empty="Inconnu"),
        browsers=_breakdown(db, AnalyticsEvent.browser, since, empty="Inconnu"),
        operating_systems=_breakdown(db, AnalyticsEvent.os, since, empty="Inconnu"),
        languages=_breakdown(db, AnalyticsEvent.language, since, empty="Inconnue"),
        events=events,
    )
