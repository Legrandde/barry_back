from datetime import date
from typing import Annotated

from pydantic import StringConstraints

from schemas.base import CamelModel

PAGEVIEW = "pageview"

EventName = Annotated[str, StringConstraints(pattern=r"^[a-z0-9_]{1,50}$")]


class TrackEvent(CamelModel):
    """Envoyé par le site à chaque visite (name="pageview") ou action à suivre.

    Exemples d'actions : whatsapp_click, contact_click, email_click, phone_click,
    project_open (label = slug du projet), social_click (label = réseau).
    """

    name: EventName = PAGEVIEW
    label: Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)] | None = None
    path: Annotated[str, StringConstraints(max_length=500)] = "/"
    referrer: Annotated[str, StringConstraints(max_length=1000)] | None = None
    utm_source: Annotated[str, StringConstraints(strip_whitespace=True, max_length=100)] | None = None


class CountItem(CamelModel):
    name: str
    count: int


class CountryStat(CamelModel):
    code: str
    visitors: int
    pageviews: int


class RegionStat(CamelModel):
    country: str
    region: str
    visitors: int
    pageviews: int


class EventCount(CamelModel):
    name: str
    label: str | None
    count: int


class DailyStat(CamelModel):
    date: date
    pageviews: int
    unique_visitors: int


class PeriodTotals(CamelModel):
    pageviews: int
    unique_visitors: int
    events: int


class AnalyticsSummary(CamelModel):
    start_date: date
    end_date: date
    days: int
    geo_available: bool
    totals: PeriodTotals
    today: PeriodTotals
    active_visitors: int
    daily: list[DailyStat]
    top_pages: list[CountItem]
    countries: list[CountryStat]
    regions: list[RegionStat]
    referrers: list[CountItem]
    utm_sources: list[CountItem]
    devices: list[CountItem]
    browsers: list[CountItem]
    operating_systems: list[CountItem]
    languages: list[CountItem]
    events: list[EventCount]
